from fastapi import Depends
from typing import List
import os
import logging
from langgraph.graph import StateGraph, END, START
import httpx

from src.workflow.state import State
from src.workflow.application.agents.context_orchestrator_agent import ContextOrchestrator
from src.workflow.dependencies import get_context_orchestrator
from src.workflow.domain.models import ContextOrchestratorOutput
from src.workflow.application.agents.general_legal_agent import GeneralLegalResearcher
from src.workflow.dependencies import get_general_legal_agent
from src.workflow.application.agents.company_research_agent import CompanyLegalResearcher
from src.workflow.dependencies import get_company_legal_agent
from src.workflow.application.agents.aggregator_agent import ResearchAggregator
from src.workflow.dependencies import get_research_aggregator
from src.workflow.application.agents.fallback_agent import FallBackAgent
from src.workflow.dependencies import get_fallback_agent

from src.shared.utils.http.get_hmac_header import generate_hmac_headers
logger = logging.getLogger(__name__)

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
            res = await client.post(
                f"{main_server}/messages/internal/{state['chat_id']}",
                headers=hmac_headers,
                json=req_body
            )

            if res.status_code != 201:
                logger.warning("POST response:", res)

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
   

