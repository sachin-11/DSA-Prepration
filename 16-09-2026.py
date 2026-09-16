from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agent import create_react_agent, AgentExcutor
from langchain import hub


# tool define karo

@tool
def get_weather(city: str) -> str:
    """get the current weather of current city when user asked about city"""
    return f"{city}: 32°C, Humid"

@tool
def calculater(expression:str) -> str:
    """ calculte the expression like 2 + 2"""
    try:
        return str(eval(expression))
    except:
        return "Invalid expression"

@tool
def search_web(query:str) -> str:
    """get query of serach web reasult"""
    return f"search for result of the {query}"

tools = [get_weather, calculater, search_web]


# LLM calling 
llm  = ChatOpenAI(model = "gpt-4o-min", tempreture = 0)
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(llm = llm, tools = tools, prompt = prompt)

# agent actually run karta he tool me 

agent_exicutor = AgentExcutor(
    agent = agent,
    tools = tools,
    verbose = True,
    max_itration = 5
)


result = agent_exicutor.invoke({
    "input": "delhi ka weather kya he kal kitna change honga"
}) 

print(result["output"])

