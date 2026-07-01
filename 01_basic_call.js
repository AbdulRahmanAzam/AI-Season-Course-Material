// LESSON 1: Basic API Call
// Digital Ocean Serverless Inference is OpenAI-compatible.
// That means we can use the official OpenAI SDK — just swap the base URL.

import OpenAI from "openai";
import "dotenv/config";

const client = new OpenAI({
  apiKey: process.env.DO_API_KEY,
  baseURL: process.env.DO_BASE_URL,
});

const response = await client.chat.completions.create({
  model: process.env.MODEL,
  messages: [
    {
      role: "user",
      content: "What is 2 + 2? Answer in one sentence.",
    },
  ],
});

// The response object has a nested structure — dig to get text
const text = response.choices[0].message.content;
console.log("Model replied:", text);

// Also log token usage — always track this in production
console.log("\nToken usage:", response.usage);
