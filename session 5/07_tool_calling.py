"""
FILE 7: Tool Calling (Function Calling)
========================================
The model cannot check the weather or your database by itself.
But it can ASK US to run a function for it. That is tool calling.

The flow:
    1. We tell the model which tools (functions) exist
    2. Model says: "please run get_weather(city='Karachi')"
    3. WE run the function in our Python code
    4. We send the result back to the model
    5. Model writes the final answer using that result

This is what makes a model an AGENT - it can take actions!
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"


# ---------- Our tools (normal Python functions) ----------
# IMPORTANT: type hints + docstring are required.
# The model reads them to understand what the tool does!

def get_weather(city: str) -> str:
    """Gets the current weather for a city."""
    print(f"   [tool running] get_weather(city='{city}')")
    fake_weather = {"karachi": "34 C, sunny", "london": "18 C, rainy", "tokyo": "25 C, cloudy"}
    return fake_weather.get(city.lower(), "22 C, clear sky")


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Converts an amount of money from one currency to another."""
    print(f"   [tool running] convert_currency({amount}, '{from_currency}', '{to_currency}')")
    rates = {"USD": 1.0, "PKR": 278.0, "EUR": 0.9}     # fake rates for the demo
    result = amount / rates[from_currency.upper()] * rates[to_currency.upper()]
    return f"{amount} {from_currency} = {result:.0f} {to_currency}"


# ---------- DEMO 1: See tool calling step by step (manual) ----------
print("=" * 50)
print("DEMO 1: Manual - see what the model asks for")
print("=" * 50)

config = types.GenerateContentConfig(
    tools=[get_weather],
    # turn OFF automatic mode so we can see the steps ourselves
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)

conversation = [
    types.Content(role="user", parts=[types.Part(text="What is the weather in Karachi?")])
]

# Step 1+2: model does NOT answer - it asks us to call a function
response = client.models.generate_content(model=MODEL, contents=conversation, config=config)
tool_call = response.function_calls[0]
print("Model asks us to run:", tool_call.name, "with arguments:", dict(tool_call.args))

# Step 3: WE run the function
result = get_weather(**tool_call.args)
print("Our function returned:", result)

# Step 4: send the result back to the model
conversation.append(response.candidates[0].content)   # the model's tool request
conversation.append(
    types.Content(
        role="user",
        parts=[types.Part.from_function_response(name=tool_call.name, response={"result": result})],
    )
)

# Step 5: now the model writes the final answer
response = client.models.generate_content(model=MODEL, contents=conversation, config=config)
print("Final answer:", response.text)


# ---------- DEMO 2: Automatic mode (the easy way) ----------
print("=" * 50)
print("DEMO 2: Automatic - the SDK runs the tools for us")
print("=" * 50)

# Just pass the Python functions as tools - the SDK does steps 2,3,4 for us!
config = types.GenerateContentConfig(tools=[get_weather, convert_currency])

response = client.models.generate_content(
    model=MODEL,
    contents="What is the weather in Tokyo? Also, how much is 100 USD in PKR?",
    config=config,
)
print("Final answer:", response.text)
