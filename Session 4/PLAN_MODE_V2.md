Step 1: Terminal se input
     
  You: /plan

  Terminal mein input("You: ") se user ne /plan type kiya + Enter press kiya.

  Step 2: main.py:run() ko milta hai

  # main.py
  run()  # no args → defaults: input_fn=input, output_fn=print

  main.py bas run() call karta hai with defaults.

  Step 3: run() ka main loop

  # loop.py:run()
  while True:
      user_text = input_fn("You: ")   # ← "/plan" yahan se aaya
      user_text = user_text.strip()   # → "/plan"

      if user_text == "":
          continue
      if user_text in ("quit", "exit", "q"):
          return

      # ← YAHAN PE! Plan toggle check
      if user_text.lower() == "/plan":
          plan_mode = not plan_mode   # flip: False → True
          _emit(output_fn, "Plan mode: ON")
          continue  # ← back to loop start

  Plan mode parse yahan hota hai — loop.py:run() ke andar, plain string comparison (== "/plan").

  Koi special "command parser" nahi hai — bas if/else block.

  Step 4: Flag flip + continue

  plan_mode = True   # ab True hai
  _emit(output_fn, "Plan mode: ON")  # user ko print hua
  continue  # ← ye `continue` loop ke top pe le jata hai

  Important: continue ke baad user message (/plan) history mein append NAHI hota. Ye sirf flag flip hai. Bilkul clean — no
  pollution.

  ---
  🤔 Phir user actual task deta hai

  You: refactor Steps.md

  Step 5: User message path

  user_text = "refactor Steps.md"
  # quit/exit check fails
  # /plan check fails (ye /plan nahi hai)
  # ↓
  mem.add_user(history, "refactor Steps.md")  # ← history mein add

  if plan_mode:  # ← True hai
      _handle_plan_mode(history, output_fn, input_fn, always_allow)
      continue

  Step 6: _handle_plan_mode call

  def _handle_plan_mode(history, output_fn, input_fn, always_allow):
      while True:
          result = _run_once(history, output_fn, input_fn, always_allow, plan_mode=True)
          #                                 ↑ plan_mode=True pass kiya

  Step 7: _run_once ke andar

  def _run_once(history, ..., plan_mode=False):
      raw = llm.chat(history, system=build_system_prompt(), plan_mode=plan_mode)
      #                                      ↑ plan_mode pass through      ↑ yahan bhi

  Step 8: llm.py:chat

  def chat(messages, system="", plan_mode=False):
      return real_llm.chat(messages, system=system, plan_mode=plan_mode)
      #                                          ↑ pass through

  Step 9: real_llm.py:chat — YAHAN ASLI DECISION HOTA HAI

  def chat(messages, system="", plan_mode=False):
      full_system = _build_system_prompt(plan_mode=plan_mode)
      #                                     ↑ plan mode mein alag prompt

      tools_arg = None if plan_mode else _to_anthropic_tools()
      #                ↑↑↑ YE LINE SABSE IMPORTANT

      response = client.messages.create(
          ...
          tools=tools_arg,  # ← SDK ko None bheja
          ...
      )

  Yahan 2 cheezein change hoti hain:
  1. Prompt alag (_PLAN_MODE_PREFIX)
  2. Tools hidden (None)

  ---
  📊 Complete flow (textual diagram)

  Terminal
    ↓ /plan
  input("You: ")           ← built-in Python function
    ↓ "/plan"
  loop.py:run()
    ↓ strip() → "/plan"
    ↓ if user_text.lower() == "/plan":
          plan_mode = True       ← LOCAL VARIABLE flip
          print("Plan mode: ON")
          continue               ← back to loop top
    ↓ (next iteration)

    User: "refactor Steps.md"
    ↓ strip() → "refactor Steps.md"
    ↓ mem.add_user(history, "refactor Steps.md")
    ↓ if plan_mode == True:
          _handle_plan_mode(history, ...)
            ↓
            while True:
              result = _run_once(history, plan_mode=True)
                ↓
                llm.chat(history, plan_mode=True)
                  ↓
                  real_llm.chat(messages, plan_mode=True)
                    ↓
                    1. _build_system_prompt(plan_mode=True)
                       → returns _PLAN_MODE_PREFIX only
                    2. tools = None
                    3. client.messages.create(tools=None)
                    4. LLM returns text-only JSON response
                    5. json.loads(raw) → {"action": "plan", "steps": [...]}
              ↓
              return ("plan", steps)
            ↓
            _print_plan(steps)
            ↓
            user_input = "y"
            ↓
            _execute_plan_steps(history, steps, ...)

  ---
  🎯 Where exactly does parsing happen?

  ┌─────────────────┬───────────────────────────┬─────────────────────────┐
  │      Layer      │           What            │          Where          │
  ├─────────────────┼───────────────────────────┼─────────────────────────┤
  │ User input      │ Raw /plan string          │ input() builtin         │
  ├─────────────────┼───────────────────────────┼─────────────────────────┤
  │ Detect command  │ if user_text == "/plan"   │ loop.py:run() line ~150 │
  ├─────────────────┼───────────────────────────┼─────────────────────────┤
  │ Flip flag       │ plan_mode = not plan_mode │ Same line               │
  ├─────────────────┼───────────────────────────┼─────────────────────────┤
  │ Pass flag down  │ Through 4 function calls  │ loop.py chain           │
  ├─────────────────┼───────────────────────────┼─────────────────────────┤
  │ Apply flag      │ tools=None, prompt change │ real_llm.py:chat()      │
  ├─────────────────┼───────────────────────────┼─────────────────────────┤
  │ API enforcement │ SDK ignores tools         │ Anthropic API           │
  └─────────────────┴───────────────────────────┴─────────────────────────┘

  ---
  🔥 The single point of decision

  real_llm.py:chat() line 144:
  tools=None if plan_mode else _to_anthropic_tools()

  Yahi ek line decide karti hai:
  - Plan mode → no tools → LLM forced to JSON
  - Normal mode → all tools → LLM free to act

  Agar ye line galat ho, sab kuch galat hota. Agar ye line sahi hai, sab kuch sahi.

  ---
  💡 Kya samjha?

  1. /plan parsing = plain if statement, no magic
  2. Flag propagation = manual pass through 4 functions (could be AgentState object, but currently param)
  3. Real enforcement = tools=None in API call, not prompt
  4. Plan detection = "action": "plan" in JSON, returns tuple
