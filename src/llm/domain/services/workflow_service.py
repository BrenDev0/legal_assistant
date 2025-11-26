from abc import ABC, abstractmethod


class WorkflowService(ABC):
    @abstractmethod
    def create_workflow(self):
        raise NotImplementedError()

    @abstractmethod
    async def invoke_workflow(self, state):
        raise NotImplementedError()