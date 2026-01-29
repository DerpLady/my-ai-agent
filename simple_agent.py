from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

@tool
def calculator(expression: str) -> str:
    """Use this tool to perform mathematical calculations. Pass in a math expression like '25*17' and get back the result."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error: {e}"

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
tools = [calculator]

agent = create_agent(llm, tools)

if __name__ == "__main__":
    user_input = input("Ask a question: ")
    result = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
    print(result["messages"][-1].content)
