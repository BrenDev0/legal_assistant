from fastapi import Depends

from src.dependencies.services import get_llm_service, get_prompt_service, get_websocket_service

from src.workflow.agents.research_aggregator.research_aggregator_agent import ResearchAggregator
from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService

from src.api.modules.websocket.websocket_service import WebsocketService

def get_research_aggregator(
    llm_service: LlmService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service),
    websocket_service: WebsocketService = Depends(get_websocket_service)
) -> ResearchAggregator:
    return ResearchAggregator(
        llm_service=llm_service,
        prompt_service=prompt_service,
        websocket_service=websocket_service
    )