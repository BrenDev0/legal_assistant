from dotenv import load_dotenv
load_dotenv()
import pytest
from unittest.mock import Mock, AsyncMock, ANY
from src.workflow.agents.context_orchestrator.agent import ContextOrchestrator
from src.workflow.agents.context_orchestrator.models import ContextOrchestratorOutput
from src.workflow.services.prompt_service import PromptService
from src.workflow.state import State
from langchain_openai import ChatOpenAI
from src.workflow.services.embeddings_service import EmbeddingService
from src.api.core.services.redis_service import RedisService


class TestRoutingAgentIntegration:
    
    @pytest.fixture
    def llm(self):
        return ChatOpenAI(
            model="gpt-4o-mini"
        )
    
  

    @pytest.fixture
    def routing_agent(self):
        embedding_service = Mock(spec=EmbeddingService)
        redis_service = Mock(spec=RedisService)
        prompt_service = PromptService(embedding_service=embedding_service, redis_service=redis_service)
        return ContextOrchestrator(prompt_service=prompt_service)
    

    @pytest.mark.asyncio
    async def test_real_general_law_query(self, routing_agent, llm):
        state = State({
            "input": "What are the employment laws in California?",
            "agent_id": "test_agent",
            "user_id": "test_user"
        })

        result = await routing_agent.interact(llm, state)

        assert result.general_law == True
        assert result.company_law == False
        assert result.chat_history == False

 
    @pytest.mark.asyncio
    async def test_company_law_query(self, routing_agent, llm):
        state = State({
            "input": "Whos our companies legal counsel?",
            "agent_id": "test_agent",
            "user_id": "test_user"
        })

        result = await routing_agent.interact(llm, state)

        assert result.general_law == False
        assert result.company_law == True
        assert result.chat_history == False
    

    @pytest.mark.asyncio
    async def test_chat_history_query(self, routing_agent, llm):
        state = State({
            "input": "explain the amendment we talked about earlier?",
            "agent_id": "test_agent",
            "user_id": "test_user"
        })

        result = await routing_agent.interact(llm, state)

        assert result.general_law == False
        assert result.company_law == False
        assert result.chat_history == True


    @pytest.mark.asyncio
    async def test_multicontext_query(self, routing_agent, llm):
        state = State({
            "input": "Review our employment contract for compliance issues",
            "agent_id": "test_agent",
            "user_id": "test_user"
        })

        result = await routing_agent.interact(llm, state)

        assert result.general_law == True
        assert result.company_law == True
        assert result.chat_history == False