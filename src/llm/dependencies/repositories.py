import logging
import os 
from src.shared.dependencies.container import Container
from src.shared.domain.exceptions.dependencies import DependencyNotRegistered

from src.llm.domain.repositorties.vector_repository import VectorRepository

from src.llm.infrastructure.qdrant.vector_repository import QdrantClient, QdrantVectorRepository
logger = logging.getLogger(__name__)


def get_qdrant_client():
    return QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )

def get_vector_repository() -> VectorRepository:
    try:
        instance_key = "vector_repository"
        repository = Container.resolve(instance_key)

    except DependencyNotRegistered:
        client = get_qdrant_client()
        repository = QdrantVectorRepository(
            client=client
        )

        Container.register(instance_key, repository)
    
    return repository