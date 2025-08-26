from  fastapi import Request, BackgroundTasks
from fastapi.responses import JSONResponse
from src.workflow.state import State

class InteractionsController: 
    async def interact(
        backgound_tasks: BackgroundTasks,
        req: Request,
        state: State,
        graph,
    ) -> State:
        backgound_tasks.add_task(graph.ainvoke, state)

        return JSONResponse(status_code=202, content={"detail": "Request received"})