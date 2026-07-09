"""
loop.py — Main agent REPL with tool-calling (ReAct pattern).

Per user turn, the loop may run multiple LLM <-> tool cycles:
    1. User message  →  history
    2. LLM think     →  action (tool_call or final)
    3. If tool_call  →  run tool, append observation to history, goto 2.
    4. If final      →  print answer, return to user prompt.

Max iterations cap prevents infinite loops if LLM keeps calling tools.

Special: bash tool is permission-gated via agent/safety.py.
"""

from __future__ import annotations

import json
import re
import sys
from typing import Callable

from agent import llm
from agent import memory as mem
from agent import tools as tool_registry
from agent import verifier
from agent import rules
from agent.prompts import build_system_prompt


# Cap on how many LLM↔tool cycles per single user turn.
MAX_ITERATIONS = 8

# Tool name that needs permission gating.
_BASH_TOOL = "bash"


def _emit(output_fn: Callable[[str], None], text: str) -> None:
    output_fn(text)
    sys.stdout.flush()


def _run_once(
    history: list[dict],
    output_fn: Callable[[str], None],
    input_fn: Callable[[str], str],
    always_allow: set[str],
    plan_mode: bool = False,
) -> bool | tuple:
    """One LLM ↔ tool cycle.

    Returns:
        True if we got a final answer (turn is done).
        False if we did a tool call (need another iteration).
        ("plan", steps) if the LLM returned a structured plan.

    Args:
        always_allow: session-scoped set of commands pre-approved by user
            via "always" answer to a WARN prompt.
        plan_mode: when True, the LLM is told (via system prompt) to return
            a "plan" action instead of executing tools directly.
    """
    # ── LLM think ─────────────────────────────────────────
    raw = llm.chat(history, system=build_system_prompt(), plan_mode=plan_mode)

    # ── Parse action ───────────────────────────────────────
    try:
        action = json.loads(raw)
    except json.JSONDecodeError as e:
        _emit(output_fn, f"[error] LLM returned non-JSON: {e}")
        return True  # bail out of this turn

    act_type = action.get("action")

    # ── Branch: tool_call ──────────────────────────────────
    if act_type == "tool_call":
        tool_name = action.get("tool", "")
        tool_args = action.get("args", {}) or {}

        handler = tool_registry.get_handler(tool_name)
        if handler is None:
            observation = f"[error] Unknown tool: {tool_name}"
        else:
            try:
                # Special-case bash: inject prompt_fn + always_allow.
                if tool_name == _BASH_TOOL:
                    observation = handler(
                        prompt_fn=input_fn,
                        always_allow=always_allow,
                        **tool_args,
                    )
                else:
                    observation = handler(**tool_args)
            except Exception as e:
                observation = f"[error] {type(e).__name__}: {e}"

        # Pretty-print for the user
        _emit(output_fn, f"  🔧 {tool_name}({tool_args})")
        preview = observation if len(observation) < 200 else observation[:200] + "..."
        _emit(output_fn, f"  ✓ {preview}")

        # Append tool result to history.
        # Role "user" + [Tool Result] prefix — this is what the LLM expects:
        # the user (system on its behalf) is feeding the tool's output back in.
        # Using "assistant" here confused the LLM into thinking IT produced
        # the observation, which broke multi-turn reasoning.
        history.append({
            "role": "user",
            "content": f"[Tool Result for {tool_name}]\n{observation}",
        })
        return False  # keep iterating

    # ── Branch: final ──────────────────────────────────────
    if act_type == "final":
        answer = action.get("answer", "")
        _emit(output_fn, f"Agent: {answer}")
        mem.add_assistant(history, answer)
        return True

    # ── Branch: plan ───────────────────────────────────────
    if act_type == "plan":
        # Plan-mode: LLM returned a structured plan (not a tool call).
        # Return tuple so caller can handle user approval.
        steps = action.get("steps", [])
        if not isinstance(steps, list) or not steps:
            _emit(output_fn, "[error] Plan action missing 'steps' list.")
            return True
        return ("plan", steps)

    # ── Unknown action ─────────────────────────────────────
    _emit(output_fn, f"[error] Unknown action type: {act_type}")
    return True


# ─────────────────────────────────────────────────────────
# Plan-mode helpers
# ─────────────────────────────────────────────────────────

def _print_plan(steps: list[str], output_fn: Callable[[str], None]) -> None:
    """Display a numbered plan to the user."""
    _emit(output_fn, "\n  Agent's plan:")
    for i, step in enumerate(steps, 1):
        _emit(output_fn, f"    {i}. {step}")
    _emit(output_fn, "")


def _handle_plan_mode(
    history: list[dict],
    output_fn: Callable[[str], None],
    input_fn: Callable[[str], str],
    always_allow: set[str],
    goal: str = "",
    verifier_mode: bool = False,
) -> None:
    """Plan flow: get plan from LLM, ask user to approve/edit/reject.

    'y'   → hand off to _execute_plan_steps (Commit 5)
    'n'   → reject plan, return to outer loop
    'edit' → get feedback, append to history, loop back to get revised plan
    """
    while True:
        # Get plan from LLM (plan_mode=True → tools=None, forced JSON).
        result = _run_once(history, output_fn, input_fn, always_allow, plan_mode=True)

        # LLM should return a tuple ("plan", steps).
        if not (isinstance(result, tuple) and result[0] == "plan"):
            # LLM didn't return a plan — bail out cleanly.
            return

        steps = result[1]
        _print_plan(steps, output_fn)

        try:
            response = input_fn("  [Plan mode] Proceed? [y/n/edit]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            _emit(output_fn, "\n  Plan cancelled.")
            return

        if response in ("y", "yes"):
            # Hand off to executor (Commit 5).
            _execute_plan_steps(
                history, steps, output_fn, input_fn, always_allow,
                goal=goal, verifier_mode=verifier_mode,
            )
            return
        elif response in ("edit", "e"):
            try:
                feedback = input_fn("  Edit feedback: ").strip()
            except (EOFError, KeyboardInterrupt):
                _emit(output_fn, "\n  Plan cancelled.")
                return
            history.append({
                "role": "user",
                "content": f"User feedback on your plan: {feedback}",
            })
            _emit(output_fn, "  Re-planning with your feedback...\n")
            continue  # loop back to get revised plan
        else:
            # 'n' or anything else = reject
            _emit(output_fn, "  Plan rejected.\n")
            return


def _execute_plan_steps(
    history: list[dict],
    steps: list[str],
    output_fn: Callable[[str], None],
    input_fn: Callable[[str], str],
    always_allow: set[str],
    goal: str = "",
    verifier_mode: bool = False,
    max_verify_retries: int = 10,
) -> None:
    """Execute each approved plan step with proper retry on tool-skip.

    For each step:
        1. Inject step as user message with strong "USE TOOLS" prompt.
        2. Run internal loop (up to MAX_ITERATIONS).
        3. Track whether ANY tool was called during this step's iterations.
        4. If final returned without any tool call → LLM skipped work,
           log warning and continue to next step.

    If verifier_mode=True and goal is given, after all steps finish we
    call the verifier. On FAIL we append the reason to history and
    re-execute the plan (up to max_verify_retries times) so the agent
    can fix the issue based on the verifier's feedback.

    This fixes the failure mode where LLM returns a "summary" without
    actually calling any tool.
    """
    verify_attempt = 0
    while True:
        total = len(steps)
        for i, step in enumerate(steps, 1):
            _emit(output_fn, f"\n  ── Step {i}/{total}: {step} ──")

            # Mark this step's start so we can detect tool calls.
            history_len_before = len(history)
            tool_called = False
            step_finished = False

            # Inject step as user message (first iteration only).
            history.append({
                "role": "user",
                "content": (
                    f"[Plan step {i}/{total} of approved plan]\n"
                    f"Task: {step}\n\n"
                    f"REQUIRED: Call the appropriate tool NOW (read_file, "
                    f"write_file, edit_file, bash, etc.) — do NOT just describe. "
                    f"After the tool result is back and this step is complete, "
                    f"return {{\"action\": \"final\", \"answer\": \"<one-line summary>\"}}."
                ),
            })

            for iteration in range(MAX_ITERATIONS):
                result = _run_once(history, output_fn, input_fn, always_allow, plan_mode=False)
                if isinstance(result, tuple):
                    # Plan-mode unexpected here, bail.
                    break

                # Detect if a tool was called during this iteration.
                if len(history) > history_len_before:
                    tool_called = True

                if result:  # True = final/error → step done
                    step_finished = True
                    break

            # If LLM returned final without calling any tool, retry once with
            # an explicit "you must call a tool first" message.
            if step_finished and not tool_called:
                _emit(output_fn, f"  ⚠ Step {i} skipped tool use — retrying with reminder.")
                retry_history_len = len(history)
                history.append({
                    "role": "user",
                    "content": (
                        f"[Retry: Step {i}/{total}]\n"
                        f"You returned a final answer without calling any tool. "
                        f"Task: {step}\n\n"
                        f"You MUST call a tool (read_file/write_file/edit_file/bash) "
                        f"BEFORE answering. Use the tool to actually do the work. "
                        f"Then return final with a one-line summary."
                    ),
                })
                for _ in range(MAX_ITERATIONS):
                    result = _run_once(history, output_fn, input_fn, always_allow, plan_mode=False)
                    if isinstance(result, tuple):
                        break
                    if len(history) > retry_history_len:
                        tool_called = True
                    if result:
                        break
                if not tool_called:
                    _emit(output_fn, f"  ⚠ Step {i} retry also skipped tools.")
            elif not step_finished:
                _emit(output_fn, f"  ⚠ Step {i} hit MAX_ITERATIONS={MAX_ITERATIONS}.")

        _emit(output_fn, "\n  ✓ Plan steps executed.\n")

        # ── Verifier phase (only if enabled and goal was provided) ──
        if not verifier_mode or not goal:
            return

        verify_attempt += 1
        if verify_attempt > max_verify_retries:
            _emit(output_fn, f"  ⚠ Verifier retries exhausted ({max_verify_retries}).\n")
            return

        verdict = verifier.verify(goal, history, emit=output_fn)

        if verdict.passed:
            _emit(output_fn, "  ✓ Plan completed & verified.\n")
            return

        # FAIL: feed coach feedback back as a user message and re-execute the plan.
        _emit(output_fn, f"  ⟳ Re-running plan with verifier feedback (attempt {verify_attempt + 1})...\n")
        feedback = (
            f"[Verifier feedback — round {verify_attempt}]\n"
            f"{verdict.to_feedback_message()}\n\n"
            f"Re-execute the same plan with this guidance. "
            f"When done, return final with a one-line summary."
        )
        history.append({"role": "user", "content": feedback})
        # loop continues: re-execute the same plan with feedback in context.


def run(input_fn: Callable[[str], str] = input,
        output_fn: Callable[[str], None] = print) -> None:
    """Run the agent REPL."""
    history = mem.init_history(build_system_prompt())

    # Session-scoped: commands the user has pre-approved via "always" answer.
    always_allow: set[str] = set()

    # Session-scoped: plan mode toggle (via /plan command).
    plan_mode: bool = False

    # Session-scoped: verifier mode toggle (via /verifier command).
    # When True, the agent's completed work is judged by a separate LLM call
    # before the turn is considered done. On FAIL, feedback is fed back to
    # the agent for a re-attempt.
    verifier_mode: bool = False

    _emit(output_fn, "╔════════════════════════════════════════════╗")
    _emit(output_fn, "║   Demo Harness — Checkpoint 2              ║")
    _emit(output_fn, "║   Mock LLM + Tools (ReAct loop)            ║")
    _emit(output_fn, "║   Tools: " + ", ".join(tool_registry.list_names()) + "  ║")
    _emit(output_fn, "║   Type 'quit' or 'exit' to leave.          ║")
    _emit(output_fn, "╚════════════════════════════════════════════╝")
    _emit(output_fn, "")

    while True:
        try:
            user_text = input_fn("You: ")
        except (EOFError, KeyboardInterrupt):
            _emit(output_fn, "\nBye!")
            return

        user_text = user_text.strip()
        if not user_text:
            continue
        if user_text.lower() in ("quit", "exit", "q"):
            _emit(output_fn, "Bye!")
            return

        # /plan toggle (session-scoped)
        if user_text.lower() == "/plan":
            plan_mode = not plan_mode
            state = "ON" if plan_mode else "OFF"
            _emit(output_fn, f"\n  ☐ Plan mode: {state}\n")
            continue

        # /verifier toggle (session-scoped)
        if user_text.lower() == "/verifier":
            verifier_mode = not verifier_mode
            state = "ON" if verifier_mode else "OFF"
            _emit(output_fn, f"\n  ☐ Verifier mode: {state}\n")
            continue

        # /log_mistake [description]
        #   with text → manual entry
        #   no args   → auto-detect mistakes from recent history, LLM-extract rules
        if re.match(r"^/log_mistake(?:\s|$)", user_text, re.IGNORECASE):
            from agent import mistakes
            description = user_text[len("/log_mistake"):].strip()

            if description:
                # Manual mode: user typed free-form text.
                rule = rules.log_mistake(description)
                _emit(output_fn, f"  ✓ Logged as [{rule.id}] in DemoHarness.md\n")
                continue

            # Auto-detect mode: scan recent history for mistake signals.
            detected = mistakes.detect_mistakes(history)
            if not detected:
                _emit(output_fn, "  No mistakes detected in recent history.\n")
                continue

            _emit(output_fn, f"  Detected {len(detected)} mistake signal(s):\n")
            for m in detected:
                _emit(output_fn, f"    • [{m.source}] {m.why}\n")

            # Meta-LLM call: mistakes → rule candidates.
            candidates = mistakes.extract_rules(detected)
            if not candidates:
                _emit(output_fn, "  No generalizable rules emerged.\n")
                continue

            _emit(output_fn, f"  Extracted {len(candidates)} rule(s):\n")
            for c in candidates:
                rule = rules.log_rule(
                    text=c["text"],
                    why=c.get("why", ""),
                    category=c.get("category", "general"),
                )
                _emit(output_fn, f"  ✓ [{rule.id}] {c['text']}\n")
            continue

        # /recall <keyword> — search and show matching rules.
        if re.match(r"^/recall(?:\s|$)", user_text, re.IGNORECASE):
            query = user_text[len("/recall"):].strip()
            if not query:
                _emit(output_fn, "  Usage: /recall <keyword>\n")
                continue
            matches = rules.recall(query)
            if not matches:
                _emit(output_fn, f"  No rules matching '{query}'.\n")
                continue
            _emit(output_fn, f"  Found {len(matches)} rule(s) for '{query}':\n")
            for r in matches:
                _emit(output_fn, f"\n  ── [{r.id}] {r.title} ──\n")
                # First non-metadata line of body, trimmed.
                for line in r.body.splitlines():
                    stripped = line.strip()
                    if stripped and not stripped.startswith("**Logged:"):
                        _emit(output_fn, f"  {stripped}\n")
                        break
            continue

        # /list — show all rules (compact view).
        if user_text.lower() == "/list":
            all_rules = rules.list_rules()
            if not all_rules:
                _emit(output_fn, "  No rules yet. Use /log_mistake to add one.\n")
                continue
            _emit(output_fn, f"  {len(all_rules)} rule(s) in DemoHarness.md:\n\n")
            for r in all_rules:
                _emit(output_fn, f"  • {r.short()}\n")
            continue

        # Add user message once.
        mem.add_user(history, user_text)
        goal = user_text  # used by verifier if enabled

        # Plan mode flow: get plan → approve → execute.
        if plan_mode:
            _handle_plan_mode(
                history, output_fn, input_fn, always_allow,
                goal=goal, verifier_mode=verifier_mode,
            )
            continue

        # Iterate LLM <-> tools until final answer or cap.
        for i in range(MAX_ITERATIONS):
            done = _run_once(history, output_fn, input_fn, always_allow)
            if done:
                break
        else:
            _emit(output_fn, f"[warn] Hit MAX_ITERATIONS={MAX_ITERATIONS}, stopping.")

        # Verifier phase (single task, no plan).
        if verifier_mode:
            for attempt in range(1, 11):  # up to 10 retries
                verdict = verifier.verify(goal, history, emit=output_fn)
                if verdict.passed:
                    _emit(output_fn, "  ✓ Verified.\n")
                    break
                _emit(output_fn, f"  ⟳ Verifier said: {verdict.reason}\n")
                feedback = (
                    f"[Verifier feedback — attempt {attempt}]\n"
                    f"{verdict.to_feedback_message()}"
                )
                history.append({"role": "user", "content": feedback})
                for j in range(MAX_ITERATIONS):
                    done = _run_once(history, output_fn, input_fn, always_allow)
                    if done:
                        break
                else:
                    _emit(output_fn, f"[warn] Hit MAX_ITERATIONS={MAX_ITERATIONS} during verify retry.")
                    break
            else:
                _emit(output_fn, "  ⚠ Verifier retries exhausted.\n")