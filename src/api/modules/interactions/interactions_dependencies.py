from src.api.modules.interactions.interactions_controller import InteractionsController
from src.dependencies.container import Container


def get_interactions_controller():
    return InteractionsController()