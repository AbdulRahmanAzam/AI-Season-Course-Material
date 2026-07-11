// LESSON 2: Streaming
// Without streaming: wait for full response, then print.
// With streaming:    tokens arrive and print one-by-one (feels instant to user).

import OpenAI from "openai";
import "dotenv/config";

const client = new OpenAI({
  apiKey: process.env.DO_API_KEY,
  baseURL: process.env.DO_BASE_URL,
});

console.log("--- WITHOUT STREAMING ---");
const full = await client.chat.completions.create({
  model: process.env.MODEL,
  messages: [{ role: "user", content: "Count from 1 to 5, one per line." }],
});
console.log(full.choices[0].message.content);


console.log("\n--- WITH STREAMING ---");
const stream = await client.chat.completions.create({
  model: process.env.MODEL,
  messages: [{ role: "user", content: "Count from 1 to 5, one per line." }],
  stream: true, // <-- only change needed
});

for await (const chunk of stream) {
  const delta = chunk.choices[0]?.delta?.content ?? "";
  process.stdout.write(delta); // print each token as it arrives
}

console.log("\n\n[stream ended]");
