from typing_extensions import TypedDict
from src.workflow.agents.context_orchestrator.context_orchestrator_models import ContextOrchestratorOutput

class State(TypedDict):
    input: str
    context_orchestrator_response: ContextOrchestratorOutput
    final_response: str
