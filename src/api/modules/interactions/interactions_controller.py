from  fastapi import Request
from src.workflow.state import State

class InteractionsController: 
    async def interact(
        req: Request,
        state: State,
        graph,
    ) -> State:
        final_state = await graph.ainivoke(state)

        return final_state