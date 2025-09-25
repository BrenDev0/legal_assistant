from fastapi import Depends

from src.dependencies.services import get_llm_service, get_prompt_service

from src.workflow.agents.context_orchestrator.context_orchestrator_agent import ContextOrchestrator
from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService

def get_context_orchestrator(
    llm_service: LlmService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service)
) -> ContextOrchestrator:
    return ContextOrchestrator(
        llm_service=llm_service,
        prompt_service=prompt_service
    )