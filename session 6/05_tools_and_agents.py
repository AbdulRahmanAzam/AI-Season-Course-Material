"""
FILE 5: Tools + Agents
========================
Session 5 FILE 7 did this by hand:
    1. tell the model which functions exist
    2. model says "please run get_weather(city='Karachi')"
    3. WE run the function
    4. we send the result back
    5. model writes the final answer
...then showed an "automatic" mode where the SDK does steps 2-4 for you.

create_agent() IS that automatic mode. Give it tools + a model, and it
runs that whole loop by itself - even calling SEVERAL tools in a row
if one question needs more than one.
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent

load_dotenv()
MODEL = "llama-3.3-70b-versatile"
llm = ChatGroq(model=MODEL, temperature=0)


# ---------- Our tools (normal Python functions) ----------
# IMPORTANT: type hints + docstring are required.
# The model reads them to decide WHEN and HOW to call the tool!

@tool
def get_weather(city: str) -> str:
    """Gets the current weather for a city."""
    print(f"   [tool running] get_weather(city='{city}')")

    # real weather api key call
    fake_weather = {"karachi": "34 C, sunny", "london": "18 C, rainy", "tokyo": "25 C, cloudy"}
    return fake_weather.get(city.lower(), "22 C, clear sky")


@tool
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Converts an amount of money from one currency to another."""
    print(f"   [tool running] convert_currency({amount}, '{from_currency}', '{to_currency}')")
    rates = {"USD": 1.0, "PKR": 278.0, "EUR": 0.9}     # fake rates for the demo
    result = amount / rates[from_currency.upper()] * rates[to_currency.upper()]
    return f"{amount} {from_currency} = {result:.0f} {to_currency}"


agent = create_agent(
    model=llm,
    tools=[get_weather, convert_currency],
    system_prompt="You are a helpful assistant. Use tools whenever it is necessary to answer the specific question, and if they are not needed, answer the question directly.",
)


def ask(question: str):
    """Small helper: run the agent and print which tools it used + the final answer."""
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})

    for msg in result["messages"]:
        if getattr(msg, "tool_calls", None):
            for call in msg.tool_calls:
                print(f"   [agent decided to call] {call['name']}({call['args']})")
    print("Final answer:", result["messages"][-1].content)


# ---------- DEMO 1: one question, one tool ----------
print("\n\n ","=" * 50)
print("\n\n DEMO 1: Single tool call")
print("=" * 50)
ask("What is the weather in Karachi?")


# ---------- DEMO 2: one question, TWO tools - agent chains them itself ----------
print("\n\n ", "=" * 50)
print("DEMO 2: The agent chains multiple tool calls on its own")
print("=" * 50)
ask("What is the weather in Tokyo? Also, how much is 100 USD in PKR?")

print("\n\n ", "=" * 50)


ask("who is the prime minister of pakistan?")