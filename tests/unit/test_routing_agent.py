import pytest
from unittest.mock import Mock, AsyncMock, ANY
from src.workflow.agents.routing.routing_agent import RoutingAgent
from src.workflow.agents.routing.routing_agent_models import MainRouterOutput
from src.workflow.services.prompt_service import PromptService
from src.workflow.state import State
from langchain_openai import ChatOpenAI

class TestRoutingAgent:
    
    @pytest.fixture
    def mock_prompt_service(self):
        return Mock(spec=PromptService)
    
    @pytest.fixture
    def mock_llm(self):
        llm = Mock(spec=ChatOpenAI)
        structured_llm = Mock()
        llm.with_structured_output.return_value = structured_llm
        return llm, structured_llm
    
    @pytest.fixture
    def routing_agent(self, mock_prompt_service):
        return RoutingAgent(mock_prompt_service)
    
    @pytest.fixture
    def sample_state(self):
        return State({
            "input": "What are the employment laws in California?",
            "agent_id": "test_agent",
            "user_id": "test_user",
            "chat_history": []
        })

    @pytest.mark.asyncio
    async def test_interact_general_law_only(self, routing_agent, mock_llm, sample_state, mock_prompt_service):
        llm, structured_llm = mock_llm
        
        # Mock the prompt template
        mock_prompt = Mock()
        mock_prompt_service.custom_prompt_chat_history_template.return_value = mock_prompt
        
        # Mock the chain
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=MainRouterOutput(
            general_law=True,
            company_law=False,
            chat_history=False
        ))
        mock_prompt.__or__ = Mock(return_value=mock_chain)
        
        # Execute
        result = await routing_agent.interact(llm, sample_state)
        
        # Assertions
        assert isinstance(result, MainRouterOutput)
        assert result.general_law == True
        assert result.company_law == False
        assert result.chat_history == False
        
        # Verify method calls
        mock_prompt_service.custom_prompt_chat_history_template.assert_called_once_with(
            state=sample_state, 
            system_message=ANY
        )
        llm.with_structured_output.assert_called_once_with(MainRouterOutput)

    @pytest.mark.asyncio
    async def test_interact_company_law_only(self, routing_agent, mock_llm, mock_prompt_service):
        llm, structured_llm = mock_llm
        
        state = State({
            "input": "Review our employment contract",
            "agent_id": "test_agent", 
            "user_id": "test_user",
            "chat_history": []
        })
        
        # Mock setup
        mock_prompt = Mock()
        mock_prompt_service.custom_prompt_chat_history_template.return_value = mock_prompt
        
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=MainRouterOutput(
            general_law=False,
            company_law=True,
            chat_history=False
        ))
        mock_prompt.__or__ = Mock(return_value=mock_chain)
        
        # Execute
        result = await routing_agent.interact(llm, state)
        
        # Assertions
        assert result.general_law == False
        assert result.company_law == True
        assert result.chat_history == False

    @pytest.mark.asyncio
    async def test_interact_all_fields_true(self, routing_agent, mock_llm, mock_prompt_service):
        llm, structured_llm = mock_llm
        
        state = State({
            "input": "Is our privacy policy still compliant with what we discussed last week?",
            "agent_id": "test_agent",
            "user_id": "test_user", 
            "chat_history": [{"sender": "client", "text": "Previous conversation"}]
        })
        
        # Mock setup
        mock_prompt = Mock()
        mock_prompt_service.custom_prompt_chat_history_template.return_value = mock_prompt
        
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=MainRouterOutput(
            general_law=True,
            company_law=True,
            chat_history=True
        ))
        mock_prompt.__or__ = Mock(return_value=mock_chain)
        
        # Execute
        result = await routing_agent.interact(llm, state)
        
        # Assertions
        assert result.general_law == True
        assert result.company_law == True
        assert result.chat_history == True

    @pytest.mark.asyncio
    async def test_interact_chat_history_only(self, routing_agent, mock_llm, mock_prompt_service):
        llm, structured_llm = mock_llm
        
        state = State({
            "input": "Can you elaborate on what you mentioned earlier?",
            "agent_id": "test_agent",
            "user_id": "test_user",
            "chat_history": [{"sender": "agent", "text": "Previous response"}]
        })
        
        # Mock setup  
        mock_prompt = Mock()
        mock_prompt_service.custom_prompt_chat_history_template.return_value = mock_prompt
        
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=MainRouterOutput(
            general_law=False,
            company_law=False,
            chat_history=True
        ))
        mock_prompt.__or__ = Mock(return_value=mock_chain)
        
        # Execute
        result = await routing_agent.interact(llm, state)
        
        # Assertions
        assert result.general_law == False
        assert result.company_law == False
        assert result.chat_history == True