from  fastapi import Request
import asyncio
from src.workflow.state import State

from src.api.core.models.http_responses import CommonHttpResponse

class InteractionsController: 
    async def interact(
        self,
        req: Request,
        state: State,
        graph,
    ) -> CommonHttpResponse:
        
        final_state: State = asyncio.create_task(
            graph.ainvike(state)
        )

        return CommonHttpResponse(
            detail="Request received"
        )
  