# =================================================================
# Agent Builder — practical example (annotated)
# =================================================================
# Interview mein aksar poocha jaata hai: "Build a simple agent that
# can use tools", "ReAct loop implement karo", ya "LangGraph agent
# banao". Yeh file ek chhota lekin complete "tool-using agent" hai,
# taaki concept practically samjha (aur explain kiya) ja sake.
#
# Idea/purpose: Ek personal-assistant-style agent jo do tools use kar
# sakta hai — weather lookup aur calculator — aur khud decide karta
# hai ki query ke liye kaunsa tool chahiye (ya tool ki zaroorat hi
# nahi hai).
#
# Key concepts (agar interview mein poochein to yeh bullets bolo):
#   1. Tools     -> agent jo actual kaam kar sakta hai (plain Python functions).
#   2. State     -> agent ki "memory" jo ek step se dusre step tak carry hoti hai.
#   3. Agent node -> decide karta hai: tool call karna hai ya final answer dena hai
#                    (real project mein yahan LLM call hota hai; yahan mock/rule-based hai).
#   4. Tool node  -> jo tool agent ne maanga tha, usse actually run karta hai.
#   5. Router     -> conditional edge: agent -> tool_node (kaam abhi baaki hai)
#                    ya agent -> END (final answer mil gaya).
#   6. Loop       -> tool ka result wapas agent ko milta hai, agent dobara decide
#                    karta hai — yahi "ReAct" (Reason + Act) pattern hai.
#
# Real LLM ke saath upgrade: agent_node ke andar rule-based if/else ki
# jagah `llm.bind_tools([...])` call aayega — LLM khud decide karega
# konsa tool chahiye aur kis argument ke saath.
# =================================================================

import ast
import operator
from typing import Optional, TypedDict

from langgraph.graph import END, StateGraph

# -----------------------------------------------------------------
# 1. Tools — agent ke paas jo "actions" available hain
# -----------------------------------------------------------------
_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}


def _safe_eval(node):
    # eval() seedha use karna unsafe hai (arbitrary code run ho sakta hai),
    # isliye sirf numbers aur basic math operators allow karte hain.
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPERATORS:
        return _ALLOWED_OPERATORS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("unsupported expression")


def calculator(expression: str) -> str:
    """Safe calculator tool — sirf + - * / ** numbers pe."""
    try:
        tree = ast.parse(expression, mode="eval")
        return str(_safe_eval(tree.body))
    except Exception as e:
        return f"error: {e}"


def get_weather(city: str) -> str:
    """Mock weather tool — real project mein weather API call hoga."""
    return f"{city} mein abhi 28C aur sunny hai."


TOOLS = {
    "get_weather": get_weather,
    "calculator": calculator,
}


# -----------------------------------------------------------------
# 2. State — agent ki memory (LangGraph ke nodes ke beech shared)
# -----------------------------------------------------------------
class AgentState(TypedDict):
    query: str                     # user ka original sawal
    tool_name: Optional[str]       # agent ne jo tool call karne ka socha
    tool_input: Optional[str]      # us tool ko diya gaya argument
    observation: Optional[str]     # tool ka result
    final_answer: Optional[str]    # final response jo user ko dena hai
    steps: int                     # kitni baar loop chal chuka (infinite loop se bachne ke liye)


# -----------------------------------------------------------------
# 3. Agent node — "Thought": decide karo tool chahiye ya final answer
# -----------------------------------------------------------------
def agent_node(state: AgentState) -> AgentState:
    """
    Real project mein yahan LLM call hoga (system prompt + tool schemas +
    query), aur LLM khud decide karega: tool call karna hai ya seedha
    final answer dena hai. Yahan bina API key ke test karne ke liye
    simple rule-based mock decision hai.
    """
    query = state["query"].lower()

    if state.get("observation"):
        # tool se result mil chuka hai -> ab final answer bana do
        state["final_answer"] = f"Final answer: {state['observation']}"
        state["tool_name"] = None
        return state

    if "weather" in query:
        state["tool_name"] = "get_weather"
        city = query.split("in")[-1].strip() if "in" in query else "mumbai"
        state["tool_input"] = city.strip("?. !").title()
    elif any(op in query for op in ["+", "-", "*", "/"]):
        state["tool_name"] = "calculator"
        state["tool_input"] = state["query"]
    else:
        state["final_answer"] = "I don't have a tool for this, but here's a direct answer (mock)."
        state["tool_name"] = None

    return state


# -----------------------------------------------------------------
# 4. Tool node — "Act": jo tool agent ne maanga, usko run karo
# -----------------------------------------------------------------
def tool_node(state: AgentState) -> AgentState:
    tool_fn = TOOLS[state["tool_name"]]
    state["observation"] = tool_fn(state["tool_input"])
    state["steps"] += 1
    return state


# -----------------------------------------------------------------
# 5. Router — conditional edge: aage tool chahiye ya khatam karo
# -----------------------------------------------------------------
def router(state: AgentState) -> str:
    if state.get("final_answer"):
        return "end"
    if state["steps"] >= 3:  # safety limit — infinite loop na ho jaaye
        return "end"
    return "tools"


# -----------------------------------------------------------------
# 6. Graph assemble — agent <-> tools loop (ReAct pattern)
# -----------------------------------------------------------------
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", tool_node)

builder.set_entry_point("agent")
builder.add_conditional_edges("agent", router, {"tools": "tools", "end": END})
builder.add_edge("tools", "agent")  # tool result wapas agent ko milta hai -> loop

graph = builder.compile()


def run_agent(query: str) -> str:
    initial_state: AgentState = {
        "query": query,
        "tool_name": None,
        "tool_input": None,
        "observation": None,
        "final_answer": None,
        "steps": 0,
    }
    result = graph.invoke(initial_state)
    return result["final_answer"]


if __name__ == "__main__":
    print(run_agent("What's the weather in Delhi?"))
    print(run_agent("12 * 4 + 5"))
    print(run_agent("who are you"))
