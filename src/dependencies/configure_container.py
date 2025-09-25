from src.dependencies.container import Container
from src.api.core.services.redis_service import RedisService
from src.workflow.services.embeddings_service import EmbeddingService
from src.workflow.services.prompt_service import PromptService
from src.api.modules.websocket.websocket_service import WebsocketService
from src.workflow.agents.context_orchestrator.context_orchestrator_agent import ContextOrchestrator
from src.workflow.agents.general_legal_research.general_legal_agent import GeneralLegalResearcher
from src.workflow.agents.research_aggregator.research_aggregator_agent import ResearchAggregator
from src.workflow.agents.company_legal_research.company_legal_research_agent import CompanyLegalResearcher
from src.workflow.services.llm_service import LlmService
from src.api.modules.interactions.interactions_dependencies import configure_interactions_dependencies

def configure_container():
  ## Idenpendent ##
  embeddings_service = EmbeddingService()
  Container.register("embeddings_service", embeddings_service)

  llm_service = LlmService()
  Container.register("llm_service", llm_service)

  redis_service = RedisService()
  Container.register("redis_service", redis_service)

  
  websocket_service = WebsocketService()
  Container.register("websocket_service", websocket_service)

  ## Dependent # All independent instances must be configured above this line ##
  prompt_service = PromptService(
    embedding_service=embeddings_service,
    redis_service=redis_service
  )
  Container.register("prompt_service", prompt_service)
 
 ## Agents ##
  company_legal_researcher = CompanyLegalResearcher(
    prompt_service=prompt_service,
    llm_service=llm_service,
    websocket_service=websocket_service
  )
  Container.register("company_legal_researcher", company_legal_researcher)

  context_orchestrator_agent = ContextOrchestrator(
    prompt_service=prompt_service,
    llm_service=llm_service
  )
  Container.register("context_orchestrator_agent", context_orchestrator_agent)
  
  general_legal_researcher = GeneralLegalResearcher(
    prompt_service=prompt_service,
    llm_service=llm_service,
    websocket_service=websocket_service
  )
  Container.register("general_legal_researcher", general_legal_researcher)

  research_aggregator = ResearchAggregator(
    prompt_service=prompt_service,
    llm_service=llm_service,
    websocket_service=websocket_service
  )
  Container.register("research_aggregator", research_aggregator)


  ## Modules # All core dependencies must be configured above this line ##
  configure_interactions_dependencies()