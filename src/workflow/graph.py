from langchain_openai import ChatOpenAI
from src.workflow.state import State
from src.dependencies.container import Container
from langgraph.graph import StateGraph, END, START

def create_graph(llm: ChatOpenAI):
    graph = StateGraph(State)

    return graph.compile()
   

