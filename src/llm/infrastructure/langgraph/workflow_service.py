from typing import List
import logging
from langgraph.graph import START, END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from expertise_chats.llm import WorkflowServiceAbsract
from src.llm.domain.models import ContextOrchestratorOutput
from src.llm.domain.state import State
from src.llm.application.agents.aggregator_agent import ResearchAggregator
from src.llm.application.agents.company_research_agent import CompanyLegalResearcher
from src.llm.application.agents.context_orchestrator_agent import ContextOrchestrator
from src.llm.application.agents.fallback_agent import FallBackAgent
from src.llm.application.agents.general_legal_agent import GeneralLegalResearcher
logger = logging.getLogger(__name__)

class LanggraphWorkflowService(WorkflowServiceAbsract):
    def __init__(
        self,
        research_aggregator_agent: ResearchAggregator,
        general_legal_researcher: GeneralLegalResearcher,
        company_legal_researcher: CompanyLegalResearcher,
        context_orchestrator: ContextOrchestrator,
        fallback_agent: FallBackAgent
    ):
        self.__context_orchestrator_agent = context_orchestrator
        self.__general_legal_researcher = general_legal_researcher
        self.__company_legal_researcher = company_legal_researcher
        self.__fallback_agent = fallback_agent
        self.__research_aggregator = research_aggregator_agent

    def create_workflow(self):
        graph = StateGraph(State)


        async def context_orchestrator_node(state: State):       
            response =  await self.__context_orchestrator_agent.interact(state=state)

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
            response = await self.__general_legal_researcher.interact(state=state)

            return {"general_legal_response": response}


        async def company_legal_research_node(state: State):
            response = await self.__company_legal_researcher.interact(state=state)


            return {"company_legal_response": response}
        

        async def aggregator_node(state: State):
            response = await self.__research_aggregator.interact(state=state)

            return {"final_response": response}
        
        async def fallback_node(state: State):
            response = await self.__fallback_agent.interact(state=state)
            return {"final_response": response}
        
        
                

        graph.add_node("context_orchestrator", context_orchestrator_node)
        graph.add_node("general_legal_research", general_legal_research_node)
        graph.add_node("company_legal_research", company_legal_research_node)
        graph.add_node("aggregator", aggregator_node)
        graph.add_node("fallback", fallback_node)
        
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
        graph.add_edge("fallback", END)
        graph.add_edge("aggregator", END)


        return graph.compile()
    
    async def invoke_workflow(self, state):
        graph: CompiledStateGraph = self.create_workflow()
        try:
            final_state = await graph.ainvoke(state)
    
            return final_state
        
        except Exception as e:
            raise