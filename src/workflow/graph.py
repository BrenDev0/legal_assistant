from fastapi import Depends
from typing import List
import os
from langgraph.graph import StateGraph, END, START
import httpx

from src.workflow.state import State
from src.workflow.agents.context_orchestrator.agent import ContextOrchestrator
from src.workflow.agents.context_orchestrator.dependencies import get_context_orchestrator
from src.workflow.agents.context_orchestrator.models import ContextOrchestratorOutput
from src.workflow.agents.general_legal_research.agent import GeneralLegalResearcher
from src.workflow.agents.general_legal_research.dependencies import get_general_legal_agent
from src.workflow.agents.company_legal_research.agent import CompanyLegalResearcher
from src.workflow.agents.company_legal_research.dependencies import get_company_legal_agent
from src.workflow.agents.research_aggregator.agent import ResearchAggregator
from src.workflow.agents.research_aggregator.dependencies import get_research_aggregator
from src.workflow.agents.fallback.agent import FallBackAgent
from src.workflow.agents.fallback.dependencies import get_fallback_agent

from src.utils.http.get_hmac_header import generate_hmac_headers


def create_graph(
    context_orchestrator_agent: ContextOrchestrator = Depends(get_context_orchestrator),
    general_legal_researcher: GeneralLegalResearcher = Depends(get_general_legal_agent),
    company_legal_researcher: CompanyLegalResearcher = Depends(get_company_legal_agent),
    research_aggregator: ResearchAggregator = Depends(get_research_aggregator),
    fallback_agent: FallBackAgent = Depends(get_fallback_agent)
):
    graph = StateGraph(State)


    async def context_orchestrator_node(state: State):       
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
            next_nodes.append("fallback")
        
        return next_nodes
    

    async def general_legal_research_node(state: State):
        response = await general_legal_researcher.interact(state=state)

        return {"general_legal_response": response}


    async def company_legal_research_node(state: State):
        response = await company_legal_researcher.interact(state=state)


        return {"company_legal_response": response}
    

    async def aggregator_node(state: State):
        response = await research_aggregator.interact(state=state)

        return {"final_response": response}
    
    async def fallback_node(state: State):
        response = await fallback_agent.interact(state=state)
        return {"final_response": response}
    
    async def hanlde_response_node(state: State):
        hmac_headers = generate_hmac_headers(os.getenv("HMAC_SECRET"))
        main_server = os.getenv("MAIN_SERVER_ENDPOINT")
        req_body = {
            "sender": os.getenv("AGENT_ID"),
            "message_type": "ai",
            "text": state["final_response"]
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{main_server}/messages/internal/{state['chat_id']}",
                headers=hmac_headers,
                json=req_body
            )

            return state
            

    graph.add_node("context_orchestrator", context_orchestrator_node)
    graph.add_node("general_legal_research", general_legal_research_node)
    graph.add_node("company_legal_research", company_legal_research_node)
    graph.add_node("aggregator", aggregator_node)
    graph.add_node("fallback", fallback_node)
    graph.add_node("handle_response", hanlde_response_node)
    
    graph.add_edge(START, "context_orchestrator")
    
    graph.add_conditional_edges(
        "context_orchestrator",
        orchestrate_research,
        [
            "general_legal_research",
            "company_legal_research",
            "fallback",
            "aggregator"
        ]
    )

    graph.add_edge("general_legal_research", "aggregator")
    graph.add_edge("company_legal_research", "aggregator")
    graph.add_edge("aggregator", "handle_response")
    graph.add_edge("fallback", "handle_response")
    graph.add_edge("handle_response", END)


    return graph.compile()
   

