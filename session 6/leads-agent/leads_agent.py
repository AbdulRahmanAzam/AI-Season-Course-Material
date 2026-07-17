"""
THE AGENT (this is the AI part)
===============================
Same idea as 05_tools_and_agents.py: we give the model some tools and it decides
when to call them. Here the tools come from leads_core.py.

You talk to it in plain English, for example:
    coffee shops in los angeles
    find restaurants in miami and save them

The agent figures out the category + city, calls the tools, and saves a CSV.

Run:  python leads_agent.py     (needs your free GROQ_API_KEY in a .env file)
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain.agents import create_agent

import leads_core  # our engine from the other file

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

# The two tools share the last search here, so the model never has to carry the
# big list of businesses around itself - it just says "search" then "save".
_LEADS = []


@tool
def find_businesses(category: str, city: str) -> str:
    """Find businesses of a given category in a given city.
    Example: category='coffee shop', city='los angeles'."""
    global _LEADS
    print(f"   [tool] searching for '{category}' in '{city}' ...")
    try:
        _LEADS = leads_core.find_places(category, city)
    except Exception as e:
        _LEADS = []
        return f"ERROR: search failed - {e}"
    if not _LEADS:
        return f"No {category} found in {city}."
    have_phone = sum(1 for lead in _LEADS if lead["phone"])
    have_email = sum(1 for lead in _LEADS if lead["email"])
    return (f"Found {len(_LEADS)} businesses ({have_phone} with phone, {have_email} "
            f"with email). Now save all of them with save_to_csv.")


@tool
def save_to_csv(filename: str) -> str:
    """Save the businesses from the last search to a CSV file.
    Pick a short filename like 'coffee_los_angeles'."""
    if not _LEADS:
        return "Nothing to save - the last search returned no businesses."
    print(f"   [tool] saving {len(_LEADS)} businesses to CSV ...")
    try:
        path = leads_core.save_leads_csv(_LEADS, filename)
    except Exception as e:
        return f"ERROR: could not save - {e}"
    return f"Saved {len(_LEADS)} businesses to {path}"


agent = create_agent(
    model=llm,
    tools=[find_businesses, save_to_csv],
    system_prompt=(
        "You generate marketing leads. From the user's request, work out the business "
        "category and the city. First call find_businesses, then call save_to_csv. "
        "Always save the results if one or more businesses were found, even if some "
        "have no phone or email. Only state facts the tools actually returned - never "
        "invent the number of results and never claim a file was saved unless "
        "save_to_csv confirms the path. If a tool returns an error or finds nothing, "
        "tell the user plainly."
    ),
)


def run(request: str):
    """Send one request to the agent and print what it did."""
    result = agent.invoke({"messages": [{"role": "user", "content": request}]})
    print("\nAgent:", result["messages"][-1].content, "\n")


if __name__ == "__main__":
    print("Marketing Leads Agent  (type 'quit' to exit)")
    print("Example: coffee shops in los angeles\n")
    while True:
        request = input("What leads do you want? ").strip()
        if request.lower() in ("quit", "exit", "q", ""):
            break
        run(request)
