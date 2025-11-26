import logging
from src.shared.dependencies.container import Container
from src.shared.domain.exceptions.dependencies import DependencyNotRegistered

from src.llm.dependencies.services import get_ebedding_service
from src.llm.dependencies.repositories import get_vector_repository

from src.llm.application.use_cases.search_for_context import SearchForContext

logger = logging.getLogger(__name__)

def get_search_for_context_use_case() -> SearchForContext:
    try:
        instance_key = "search_for_context_use_case"
        use_case = Container.resolve(instance_key)

    except DependencyNotRegistered:
        use_case = SearchForContext(
            embedding_service=get_ebedding_service(),
            vector_repository=get_vector_repository()
        )

        Container.register(instance_key, use_case)
        logger.info(f"{instance_key} registered")

    return use_case