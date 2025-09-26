from fastapi import Depends

from src.dependencies.services import get_llm_service, get_prompt_service, get_websocket_service

from src.workflow.agents.company_legal_research.agent import CompanyLegalResearcher
from src.workflow.services.llm_service import LlmService
from src.workflow.services.prompt_service import PromptService

from src.api.modules.websocket.websocket_service import WebsocketService

def get_company_legal_agent(
    llm_service: LlmService = Depends(get_llm_service),
    prompt_service: PromptService = Depends(get_prompt_service),
    websocket_service: WebsocketService = Depends(get_websocket_service)
) -> CompanyLegalResearcher:
    return CompanyLegalResearcher(
        llm_service=llm_service,
        prompt_service=prompt_service,
        websocket_service=websocket_service
    )