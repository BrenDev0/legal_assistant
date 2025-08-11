from langchain_openai import ChatOpenAI
from src.workflow.state import State
from src.dependencies.container import Container
from langgraph.graph import StateGraph, END, START
from src.workflow.agents.context_orchestrator.context_orchestrator_agent import ContextOrchestrator

def create_graph(llm: ChatOpenAI):
    graph = StateGraph(State)

    async def context_orchestrator_node(state: State):
        context_orchestrator_agent: ContextOrchestrator = Container.resolve("routing_agent")
        
        response =  await context_orchestrator_agent.interact(llm=llm, state=state)

        state["router_response"] = response
        return state
    
    graph.add_node("context_orchestrator", context_orchestrator_node)

    graph.add_edge(START, "context_orchestrator")

    return graph.compile()
   

