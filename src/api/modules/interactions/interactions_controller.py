from  fastapi import Request, BackgroundTasks
from src.workflow.state import State

class InteractionsController: 
    async def interact(
        backgound_tasks: BackgroundTasks,
        req: Request,
        state: State,
        graph,
    ) -> State:
        final_state = await graph.ainvoke(state)

        return final_state