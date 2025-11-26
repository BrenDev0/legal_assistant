from typing import TypeVar, Dict, cast, List
from src.shared.domain.exceptions.dependencies import DependencyNotRegistered

T = TypeVar('T')
class Container:
    __instances:  Dict[str, T] = {}

    @classmethod
    def register(cls, key: str, instance: T) -> None:
        cls.__instances[key] = instance
    
    @classmethod
    def resolve(cls, key: str):
        if key not in cls.__instances:
            raise DependencyNotRegistered(f"Dependency '{key}' not registerd!")
        
        return cast(T, cls.__instances[key])
    
    @classmethod
    def clear(cls) -> None:
        cls.__instances.clear()

    @classmethod
    def get_instances(cls) -> List[str]:
        return list(cls.__instances.keys())
