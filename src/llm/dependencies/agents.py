import logging
from src.shared.dependencies.container import Container
from src.shared.domain.exceptions.dependencies import DependencyNotRegistered

from src.llm.application.agents.aggregator_agent import ResearchAggregator
from src.llm.application.agents.company_research_agent import CompanyLegalResearcher
from src.llm.application.agents.context_orchestrator_agent import ContextOrchestrator
from src.llm.application.agents.fallback_agent import FallBackAgent
from src.llm.application.agents.general_legal_agent import GeneralLegalResearcher

from src.llm.dependencies.services import get_ebedding_service, get_llm_service, get_prompt_service
from src.llm.dependencies.use_cases import get_search_for_context_use_case
from src.web_sockets.dependencies.use_cases import get_ws_streaming_use_case

logger = logging.getLogger(__name__)

def get_aggregator_agent() -> ResearchAggregator:
    try: 
        instance_key = "aggregator_agent"
        agent = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        agent = ResearchAggregator(
            prompt_service=get_prompt_service(),
            llm_service=get_llm_service(),
            streaming=get_ws_streaming_use_case()
        )

        Container.register(instance_key, agent)
        logger.info(f"{instance_key} registered")
        logger.debug("THIS IS A DEBUG MESSAGE:::::::::::::")
    
    return agent


def get_company_legal_agent() -> CompanyLegalResearcher:
    try: 
        instance_key = "company_legal_agent"
        agent = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        agent = CompanyLegalResearcher(
            prompt_service=get_prompt_service(),
            llm_service=get_llm_service(),
            streaming=get_ws_streaming_use_case(),
            search_for_context=get_search_for_context_use_case()
        )

        Container.register(instance_key, agent)
        logger.info(f"{instance_key} registered")
    
    return agent

def get_orchestrator_agent() -> ContextOrchestrator:
    try: 
        instance_key = "orchestrator_agent"
        agent = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        agent = ContextOrchestrator(
            prompt_service=get_prompt_service(),
            llm_service=get_llm_service()
        )

        Container.register(instance_key, agent)
        logger.info(f"{instance_key} registered")
    
    return agent

def get_general_legal_agent() -> GeneralLegalResearcher:
    try: 
        instance_key = "general_legal_agent"
        agent = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        agent = GeneralLegalResearcher(
            prompt_service=get_prompt_service(),
            llm_service=get_llm_service(),
            streaming=get_ws_streaming_use_case(),
            search_for_context=get_search_for_context_use_case()
        )

        Container.register(instance_key, agent)
        logger.info(f"{instance_key} registered")
    
    return agent

def get_fallback_agent() -> FallBackAgent:
    try: 
        instance_key = "fallback_agent"
        agent = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        agent = FallBackAgent(
            prompt_service=get_prompt_service(),
            llm_service=get_llm_service(),
            streaming=get_ws_streaming_use_case()
        )

        Container.register(instance_key, agent)
        logger.info(f"{instance_key} registered")
    
    return agent




