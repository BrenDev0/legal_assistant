from langchain_openai import ChatOpenAI
from typing import List
from src.workflow.state import State
from src.dependencies.container import Container
from langgraph.graph import StateGraph, END, START
from src.workflow.agents.context_orchestrator.context_orchestrator_agent import ContextOrchestrator
from src.workflow.agents.context_orchestrator.context_orchestrator_models import ContextOrchestratorOutput
from src.workflow.agents.general_legal_research.general_legal_agent import GeneralLegalResearcher
from src.workflow.agents.company_legal_research.company_legal_research_agent import CompanyLegalResearcher
from src.workflow.agents.research_aggregator.research_aggregator_agent import ResearchAggregator


def create_graph():
    graph = StateGraph(State)


    async def context_orchestrator_node(state: State):
        context_orchestrator_agent: ContextOrchestrator = Container.resolve("context_orchestrator_agent")
        
        response =  await context_orchestrator_agent.interact(state=state)

        return {"context_orchestrator_response": response}
    

    def orchestrate_research(state: State) -> List[str]:
        orchestrator_response: ContextOrchestratorOutput = state["context_orchestrator_response"]
        next_nodes = []

        if orchestrator_response.general_law:
            next_nodes.append("general_legal_research")

        if orchestrator_response.company_law:
            next_nodes.append("company_legal_research")
        
        if not next_nodes:
            next_nodes.append("aggregator")
        
        return next_nodes
    

    async def general_legal_research_node(state: State):
        general_legal_researcher: GeneralLegalResearcher = Container.resolve("general_legal_researcher")

        response = await general_legal_researcher.interact(state=state)

        return {"general_legal_response": response}


    async def company_legal_research_node(state: State):
        company_legal_researcher: CompanyLegalResearcher = Container.resolve("company_legal_researcher")

        response = await company_legal_researcher.interact(state=state)


        return {"company_legal_response": response}
    

    async def aggregator_node(state: State):
        research_aggregator: ResearchAggregator = Container.resolve("research_aggregator")

        response = await research_aggregator.interact(state=state)

        return {"final_response": response}



    graph.add_node("context_orchestrator", context_orchestrator_node)
    graph.add_node("general_legal_research", general_legal_research_node)
    graph.add_node("company_legal_research", company_legal_research_node)
    graph.add_node("aggregator", aggregator_node)
    



    graph.add_edge(START, "context_orchestrator")
    
    graph.add_conditional_edges(
        "context_orchestrator",
        orchestrate_research,
        [
            "general_legal_research",
            "company_legal_research",
            "aggregator"
        ]
    )

    graph.add_edge("general_legal_research", "aggregator")
    graph.add_edge("company_legal_research", "aggregator")
    graph.add_edge("aggregator", END)


    return graph.compile()
   

