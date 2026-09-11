# first thing we do define state for the agent 
from typing import Annotated, TypedDict, List
from langgraph.graph import add_mesages
from langchain.openai import ChatOpenAI
from langgraph.graph import stateGraph, End


class AgentState(TypedDict):
    message: Annotated[list, add_mesages]
    task: str
    result: dict
    next_agent: str
    error: str | None

# next supper vison and wroker agent

llm = ChatOpenAI("gpt-4o-min")



