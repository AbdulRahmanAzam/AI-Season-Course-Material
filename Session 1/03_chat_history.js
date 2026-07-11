// LESSON 3: Multi-turn Chat (Conversation History)
// LLMs are stateless — they forget everything after each call.
// YOU must send the full conversation history every time.

import OpenAI from "openai";
import "dotenv/config";

const client = new OpenAI({
  apiKey: process.env.DO_API_KEY,
  baseURL: process.env.DO_BASE_URL,
});

async function chat(history, userMessage) {
  // Push new user message into history
  history.push({ role: "user", content: userMessage });

  const response = await client.chat.completions.create({
    model: process.env.MODEL,
    messages: history, // send FULL history every call
  });

  const assistantMessage = response.choices[0].message;

  // Push assistant reply into history so next turn remembers it
  history.push(assistantMessage);

  return assistantMessage.content;
}

// Simulate a 3-turn conversation
const history = [
  {
    role: "system",
    content: "You are a helpful assistant. Keep answers short.",
  },
];

const reply1 = await chat(history, "My name is Abdul.");
console.log("Turn 1:", reply1);

const reply2 = await chat(history, "What is the capital of France?");
console.log("Turn 2:", reply2);

// This proves model remembers earlier context
const reply3 = await chat(history, "What is my name?");
console.log("Turn 3:", reply3);

console.log("\nFull history sent on last call:");
console.log(JSON.stringify(history, null, 2));
