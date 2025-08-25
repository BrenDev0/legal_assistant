from typing_extensions import TypedDict
from src.workflow.agents.context_orchestrator.context_orchestrator_models import ContextOrchestratorOutput
from  uuid import UUID
from typing import Dict, List, Any

class State(TypedDict):
    chat_id: UUID
    company_id: UUID
    chat_history: List[Dict[str, Any]]
    input: str
    context_orchestrator_response: ContextOrchestratorOutput
    general_legal_response: str
    company_legal_response: str
    final_response: str
