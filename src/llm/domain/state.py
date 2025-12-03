from typing_extensions import TypedDict
from expertise_chats.broker.domain.interaction_event import InteractionEvent
from src.llm.domain.models import ContextOrchestratorOutput

class State(TypedDict):
    context_orchestrator_response: ContextOrchestratorOutput
    general_legal_response: str
    company_legal_response: str
    final_response: str
    event: InteractionEvent
