import logging
from expertise_chats.dependencies.container import Container
from expertise_chats.exceptions.dependencies import DependencyNotRegistered

from src.llm.domain.services.embedding_service import EmbeddingService
from src.llm.domain.services.llm_service import LlmService
from src.llm.domain.services.workflow_service import WorkflowService

from src.llm.application.services.prompt_service import PromptService

from src.llm.infrastructure.langchain.llm_service import LangchainLlmService
from src.llm.infrastructure.openai.embedding_service import OpenAIEmbeddingService
from src.llm.infrastructure.langgraph.workflow_service import LanggraphWorkflowService

logger = logging.getLogger(__name__)

def get_llm_service() -> LlmService:
    try:
        instance_key = "llm_service"
        service = Container.resolve(instance_key)

    except DependencyNotRegistered:
        service = LangchainLlmService()
        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")

    return service


def get_ebedding_service() -> EmbeddingService:
    try:
        instance_key = "embedding_service"
        service = Container.resolve(instance_key)

    except DependencyNotRegistered:
        service = OpenAIEmbeddingService()
        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service

def get_prompt_service() -> PromptService:
    try:
        instance_key = "prompt_service"
        service = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        service = PromptService()

        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service

def get_workflow_service() -> WorkflowService:
    try:
        instance_key = "workflow_service"
        service = Container.resolve(instance_key)
    
    except DependencyNotRegistered:
        from  src.llm.dependencies.agents import get_orchestrator_agent, get_aggregator_agent, get_company_legal_agent, get_fallback_agent, get_general_legal_agent
        service = LanggraphWorkflowService(
            context_orchestrator=get_orchestrator_agent(),
            general_legal_researcher=get_general_legal_agent(),
            company_legal_researcher=get_company_legal_agent(),
            research_aggregator_agent=get_aggregator_agent(),
            fallback_agent=get_fallback_agent()
        )

        Container.register(instance_key, service)
        logger.info(f"{instance_key} registered")
    
    return service


