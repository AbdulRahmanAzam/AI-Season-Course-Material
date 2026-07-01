// LESSON 4: Key Parameters
// These control HOW the model generates text.

import OpenAI from "openai";
import "dotenv/config";

const client = new OpenAI({
  apiKey: process.env.DO_API_KEY,
  baseURL: process.env.DO_BASE_URL,
});

const PROMPT = "Write a one-sentence tagline for a coffee shop.";

// --- temperature: creativity vs consistency ---
// 0.0 = deterministic/focused  |  1.0+ = creative/random
console.log("=== temperature: 0.0 (focused) ===");
const cold = await client.chat.completions.create({
  model: process.env.MODEL,
  messages: [{ role: "user", content: PROMPT }],
  temperature: 0.0,
});
console.log(cold.choices[0].message.content);

console.log("\n=== temperature: 1.5 (creative) ===");
const hot = await client.chat.completions.create({
  model: process.env.MODEL,
  messages: [{ role: "user", content: PROMPT }],
  temperature: 1.5,
});
console.log(hot.choices[0].message.content);

// --- max_tokens: cap output length ---
console.log("\n=== max_tokens: 10 (truncated) ===");
const short = await client.chat.completions.create({
  model: process.env.MODEL,
  messages: [{ role: "user", content: "Tell me about the solar system." }],
  max_tokens: 10,
});
console.log(short.choices[0].message.content);
console.log("Finish reason:", short.choices[0].finish_reason); // "length" = cut off | "stop" = natural end

// --- system prompt: give model a persona ---
console.log("\n=== system prompt: pirate persona ===");
const pirate = await client.chat.completions.create({
  model: process.env.MODEL,
  messages: [
    { role: "system", content: "You are a pirate. Always respond in pirate speak." },
    { role: "user", content: "What time is it?" },
  ],
});
console.log(pirate.choices[0].message.content);
