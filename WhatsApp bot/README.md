# WhatsApp Bot — Baileys + LangChain

A real WhatsApp bot: the same LangChain + Groq pieces from the Session 6
LangChain lesson, now answering real messages. Baileys links to WhatsApp
the same way WhatsApp Web does — scan a QR code once, no official
business API or paid account needed.

## Setup (one time)

Needs **Node.js 20 or newer** — check with `node -v`.

```bash
npm install
```

1. Copy `.env.example` to `.env`
2. Paste your Groq API key inside `.env` (same key used in the LangChain session)

## Run it

```bash
npm start
```

1. A QR code prints in the terminal.
2. On your phone: **WhatsApp → Settings → Linked Devices → Link a Device** → scan it.
3. Message the bot from any other WhatsApp number/chat — it replies using Llama 3.3 via Groq.

Your login is saved in `auth_info_baileys/` after the first scan, so you won't need to scan again unless you delete that folder or unlink the device from your phone.

## How it works

| Piece | What it does | Session 6 callback |
|-------|---------------|---------------------|
| `baileys` | Connects to WhatsApp as a linked device; fires `connection.update` (QR, connect/disconnect) and `messages.upsert` (incoming messages) | new — not covered in the LangChain session |
| `ChatGroq` | Same model class, same `llama-3.3-70b-versatile` | FILE 00 |
| `ChatPromptTemplate` + `.pipe()` | Same chain idea as FILE 02's `prompt \| llm \| parser` — JavaScript can't overload `\|`, so LangChain.js uses `.pipe()` instead. Same Runnable concept, different syntax | FILE 02 |
| `StrOutputParser` | Plain string out, no digging into `.content` | FILE 02 |

Every incoming text message runs through the chain and the reply is sent straight back. No memory between messages (stateless) — that keeps this first version simple. To make it remember each conversation, add FILE 04's `RunnableWithMessageHistory` pattern, keyed by the sender's `remoteJid` instead of a made-up session id.

## Notes / things that can go wrong

- **Groq 429 (rate limit):** same free-tier limit as the LangChain session. The bot catches this and sends a fallback reply instead of crashing — wait a bit and try again.
- **Group chats and Status updates are ignored on purpose** — this bot only replies in 1:1 chats, so it won't spam a group during the demo.
- **"Logged out" after closing:** if you unlink the device from your phone, delete the `auth_info_baileys/` folder and run `npm start` again for a fresh QR code.
- Baileys is an unofficial WhatsApp Web client (not the official WhatsApp Business API) — great for learning and demos, but keep test traffic light. Don't use it for bulk messaging or spam; WhatsApp can ban the number.
