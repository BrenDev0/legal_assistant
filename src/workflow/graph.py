from langchain_openai import ChatOpenAI
from typing import List
from src.workflow.state import State
from src.dependencies.container import Container
from langgraph.graph import StateGraph, END, START
from src.workflow.agents.context_orchestrator.context_orchestrator_agent import ContextOrchestrator
from src.workflow.agents.context_orchestrator.context_orchestrator_models import ContextOrchestratorOutput

def create_graph():
    graph = StateGraph(State)


    async def context_orchestrator_node(state: State):
        context_orchestrator_agent: ContextOrchestrator = Container.resolve("context_orchestrator_agent")
        
        response =  await context_orchestrator_agent.interact(state=state)

        state["context_orchestrator_response"] = response
        return state
    

    def orchestrate_research(state: State) -> List[str]:
        orchestrator_response: ContextOrchestratorOutput = state["context_orchestrator_response"]
        next_nodes = []

        if orchestrator_response.general_law:
            next_nodes.append("general_legal_research")

        if orchestrator_response.company_law:
            next_nodes.append("company_legal_research")

        if orchestrator_response.chat_history:
            next_nodes.append("chat_history")
        
        if not next_nodes:
            next_nodes.append("aggregator")
        
        return next_nodes
    

    async def general_legal_research_node(state: State):
        pass


    async def company_legal_research_node(state: State):
        pass
    

    async def chat_history_node(state: State):
        pass


    async def aggregator_node(state: State):
        pass

    async def reflection_node(state: State): 
        pass


    graph.add_node("context_orchestrator", context_orchestrator_node)
    graph.add_node("general_legal_research", general_legal_research_node)
    graph.add_node("company_legal_research", company_legal_research_node)
    graph.add_node("chat_history", chat_history_node)
    graph.add_node("aggregator", aggregator_node)
    graph.add_node("reflection", reflection_node)



    graph.add_edge(START, "context_orchestrator")
    
    graph.add_conditional_edges(
        "context_orchestrator",
        orchestrate_research,
        [
            "general_legal_research",
            "company_legal_research",
            "chat_history",
            "aggregator"
        ]
    )

    graph.add_edge("general_legal_research", "aggregator")
    graph.add_edge("company_legal_research", "aggregator")
    graph.add_edge("chat_history", "aggregator")
    graph.add_edge("aggregator", "reflection")
    graph.add_edge("reflection", END)


    return graph.compile()
   

