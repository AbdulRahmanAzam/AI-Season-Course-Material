"""
HELPER: writes the debate to disk WHILE it is still happening
=============================================================
This is not a lesson file -- it is plumbing. Ignore it in class if you want.

The demo calls one method, .add(), once per message, and this file keeps
three views of the same conversation up to date on disk:

    transcripts/debate_<topic>.md     a clean markdown log
    transcripts/debate_<topic>.json   the same conversation as data
    transcripts/debate_<topic>.html   a chat page you can WATCH LIVE

The HTML page reloads itself every 2 seconds and scrolls to the bottom,
so you can double-click it BEFORE the debate finishes and watch the
bubbles show up one by one. No server, no extra library.
"""

import os
import re
import json
import html
from datetime import datetime

FOLDER = "transcripts"


def _slug(topic):
    """'Toyota is better!' -> 'toyota_is_better' so it is a safe file name."""
    words = re.sub(r"[^a-z0-9 ]", "", topic.lower()).split()
    return "_".join(words[:6]) or "debate"


class Transcript:
    """Holds the messages so far and rewrites the three files after each one."""

    def __init__(self, topic):
        os.makedirs(FOLDER, exist_ok=True)
        self.topic = topic
        self.messages = []          # list of {"n", "who", "text", "verdict"}
        self.result = None          # filled in by .finish()

        base = os.path.join(FOLDER, "debate_" + _slug(topic))
        self.md_path = base + ".md"
        self.json_path = base + ".json"
        self.html_path = base + ".html"

        # start the markdown file fresh for this run
        with open(self.md_path, "w", encoding="utf-8") as f:
            f.write(f"# Debate: {topic}\n\n")
            f.write(f"_started {datetime.now():%d %b %Y, %H:%M:%S}_\n\n")
        self._write_json()
        self._write_html()

    # ---------- the only method the demo calls ----------
    def add(self, who, text, verdict):
        """Record one message and immediately refresh all three files."""
        self.messages.append({
            "n": len(self.messages) + 1,
            "who": who,
            "text": text,
            "verdict": verdict,
        })

        with open(self.md_path, "a", encoding="utf-8") as f:   # append, do not rewrite
            f.write(f"**[{len(self.messages)}] {who}**\n\n{text}\n\n---\n\n")

        self._write_json()
        self._write_html()

    def finish(self, verdict, how):
        """Called once at the end. 'how' explains why the debate stopped."""
        self.result = {"verdict": verdict, "how": how}
        with open(self.md_path, "a", encoding="utf-8") as f:
            f.write(f"## Final answer: {verdict}\n\n{how}\n")
        self._write_json()
        self._write_html()

    # ---------- file writers ----------
    def _write_json(self):
        data = {
            "topic": self.topic,
            "messages": self.messages,
            "result": self.result,
        }
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _write_html(self):
        bubbles = ""
        for m in self.messages:
            side = {"PRO": "left", "CON": "right"}.get(m["who"], "middle")
            body = html.escape(m["text"]).replace("\n", "<br>")
            bubbles += (
                f'<div class="row {side}">'
                f'<div class="bubble {side}">'
                f'<div class="who">{m["n"]}. {m["who"]}</div>{body}</div></div>'
            )

        if self.result:
            banner = (f'<div class="done">DEBATE OVER &mdash; both agents say '
                      f'<b>{html.escape(self.result["verdict"])}</b>'
                      f'<div class="how">{html.escape(self.result["how"])}</div></div>')
            refresh = ""                    # finished, so stop reloading the page
            status = "finished"
        else:
            banner = '<div class="waiting">debating... this page refreshes itself</div>'
            refresh = '<meta http-equiv="refresh" content="2">'
            status = f"{len(self.messages)} messages so far"

        page = f"""<!doctype html>
<html><head><meta charset="utf-8">{refresh}
<title>Debate: {html.escape(self.topic)}</title>
<style>
  body {{ background:#faf7f5; color:#111; font-family:Segoe UI,Arial,sans-serif;
         margin:0; padding:24px 16px 60px; }}
  h1 {{ font-size:20px; max-width:760px; margin:0 auto 4px; }}
  .sub {{ max-width:760px; margin:0 auto 24px; color:#777; font-size:13px; }}
  .row {{ display:flex; max-width:760px; margin:0 auto 14px; }}
  .row.right {{ justify-content:flex-end; }}
  .row.middle {{ justify-content:center; }}
  .bubble.middle {{ background:#111; color:#fff; max-width:80%; }}
  .bubble.middle .who {{ color:#ffb182; }}
  .bubble {{ max-width:70%; padding:12px 16px; border-radius:14px;
             line-height:1.5; font-size:15px; white-space:normal; }}
  .bubble.left  {{ background:#fff2e8; border:1px solid #ff6b1a; border-bottom-left-radius:4px; }}
  .bubble.right {{ background:#fff;    border:1px solid #ccc;    border-bottom-right-radius:4px; }}
  .who {{ font-size:11px; letter-spacing:1px; font-weight:700;
          text-transform:uppercase; margin-bottom:6px; color:#ff6b1a; }}
  .bubble.right .who {{ color:#555; }}
  .waiting {{ max-width:760px; margin:24px auto; color:#999; font-size:13px; font-style:italic; }}
  .done {{ max-width:760px; margin:28px auto; padding:16px 20px; border-radius:12px;
           background:#111; color:#fff; font-size:16px; }}
  .how {{ margin-top:8px; font-size:13px; color:#ffb182; }}
</style></head>
<body>
  <h1>{html.escape(self.topic)}</h1>
  <div class="sub">PRO argues yes (left) &nbsp;|&nbsp; CON argues no (right) &nbsp;|&nbsp; {status}</div>
  {bubbles}
  {banner}
  <script>window.scrollTo(0, document.body.scrollHeight);</script>
</body></html>"""

        with open(self.html_path, "w", encoding="utf-8") as f:
            f.write(page)
