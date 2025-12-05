import logging
import os 
from expertise_chats.dependencies.container import Container
from expertise_chats.exceptions.dependencies import DependencyNotRegistered

from src.llm.domain.repositorties.vector_repository import VectorRepository

from src.llm.infrastructure.qdrant.vector_repository import QdrantVectorRepository
logger = logging.getLogger(__name__)


def get_vector_repository() -> VectorRepository:
    try:
        instance_key = "vector_repository"
        repository = Container.resolve(instance_key)

    except DependencyNotRegistered:
        repository = QdrantVectorRepository()

        Container.register(instance_key, repository)
    
    return repository