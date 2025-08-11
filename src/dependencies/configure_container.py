from src.dependencies.container import Container
from src.api.core.services.redis_service import RedisService
from src.workflow.services.embeddings_service import EmbeddingService
from src.workflow.services.prompt_service import PromptService
from src.workflow.agents.context_orchestrator.context_orchestrator_agent import ContextOrchestrator

def configure_container():
  ## Idenpendent ##
  embeddings_service = EmbeddingService()
  Container.register("embeddings_service", embeddings_service)


  redis_service = RedisService()
  Container.register("redis_service", redis_service)

 
 
  
  
  ## Dependent # All independent instances must be configured above this line ##
  prompt_service = PromptService(
    embedding_service=embeddings_service,
    redis_service=redis_service
  )
  Container.register("prompt_service", prompt_service)
 
 
  context_orchestrator_agent = ContextOrchestrator(
    prompt_service=prompt_service
  )
  Container.register("context_orchestrator_agent", context_orchestrator_agent)
  
  
  ## Modules # All core dependencies must be configured above this line ##