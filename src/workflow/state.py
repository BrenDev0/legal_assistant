from typing_extensions import TypedDict
from src.workflow.domain.models import ContextOrchestratorOutput
from  uuid import UUID
from typing import Dict, List, Any

class State(TypedDict):
    company_id: UUID
    chat_history: List[Dict[str, Any]]
    input: str
    context_orchestrator_response: ContextOrchestratorOutput
    general_legal_response: str
    company_legal_response: str
    final_response: str
    chat_id: UUID
    voice: bool
