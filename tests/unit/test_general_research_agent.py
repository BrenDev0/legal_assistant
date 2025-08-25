import pytest
from unittest.mock import Mock, AsyncMock, ANY
from src.workflow.agents.general_legal_research.general_legal_agent import GeneralLegalResearcher
from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.workflow.state import State
from langchain_openai import ChatOpenAI

class TestGeneralLegalResearcher:
    
    @pytest.fixture
    def mock_prompt_service(self):
        return Mock(spec=PromptService)
    
    @pytest.fixture
    def mock_llm_service(self):
        return Mock(spec=LlmService)
    
    @pytest.fixture
    def mock_llm(self):
        llm = Mock(spec=ChatOpenAI)
        return llm
    
    @pytest.fixture
    def general_legal_researcher(self, mock_prompt_service, mock_llm_service):
        return GeneralLegalResearcher(mock_prompt_service, mock_llm_service)
    
    @pytest.fixture
    def sample_state(self):
        return State({
            "input": "What are the employment laws in Mexico?",
            "agent_id": "test_agent",
            "user_id": "test_user",
            "chat_history": []
        })

    @pytest.mark.asyncio
    async def test_interact_employment_law_query(self, general_legal_researcher, sample_state, mock_prompt_service, mock_llm_service):
        # Mock the LLM service
        mock_llm = Mock(spec=ChatOpenAI)
        mock_llm_service.get_llm.return_value = mock_llm
        
        # Mock the prompt template
        mock_prompt = Mock()
        mock_prompt_service.custom_prompt_template.return_value = mock_prompt
        
        # Mock the chain response
        mock_response = Mock()
        mock_response.content = "**Legal Framework:** Ley Federal del Trabajo\n**Relevant Provisions:** Article 123 of Mexican Constitution..."
        
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.__or__ = Mock(return_value=mock_chain)
        
        # Execute
        result = await general_legal_researcher.interact(sample_state)
        
        # Assertions
        assert isinstance(result, str)
        assert "Legal Framework" in result
        assert "Ley Federal del Trabajo" in result
        
        # Verify method calls
        mock_llm_service.get_llm.assert_called_once_with(temperature=0.5)
        mock_prompt_service.custom_prompt_template.assert_called_once_with(
            state=sample_state,
            system_message=ANY,
            with_context=True,
            context_collection="general_legal"
        )
        mock_chain.ainvoke.assert_called_once_with({"input": sample_state["input"]})

    @pytest.mark.asyncio
    async def test_interact_corporate_law_query(self, general_legal_researcher, mock_prompt_service, mock_llm_service):
        state = State({
            "input": "What are the requirements for forming a corporation in Mexico?",
            "agent_id": "test_agent",
            "user_id": "test_user",
            "chat_history": []
        })
        
        # Mock setup
        mock_llm = Mock(spec=ChatOpenAI)
        mock_llm_service.get_llm.return_value = mock_llm
        
        mock_prompt = Mock()
        mock_prompt_service.custom_prompt_template.return_value = mock_prompt
        
        mock_response = Mock()
        mock_response.content = "**Legal Framework:** Ley General de Sociedades Mercantiles\n**Relevant Provisions:** Articles 6-11..."
        
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.__or__ = Mock(return_value=mock_chain)
        
        # Execute
        result = await general_legal_researcher.interact(state)
        
        # Assertions
        assert isinstance(result, str)
        assert "Ley General de Sociedades Mercantiles" in result
        assert "Legal Framework" in result
        
        # Verify prompt was called with correct collection
        mock_prompt_service.custom_prompt_template.assert_called_once_with(
            state=state,
            system_message=ANY,
            with_context=True,
            context_collection="general_legal"
        )

    @pytest.mark.asyncio
    async def test_interact_tax_law_query(self, general_legal_researcher, mock_prompt_service, mock_llm_service):
        state = State({
            "input": "What are the tax obligations for Mexican companies?",
            "agent_id": "test_agent",
            "user_id": "test_user",
            "chat_history": []
        })
        
        # Mock setup
        mock_llm = Mock(spec=ChatOpenAI)
        mock_llm_service.get_llm.return_value = mock_llm
        
        mock_prompt = Mock()
        mock_prompt_service.custom_prompt_template.return_value = mock_prompt
        
        mock_response = Mock()
        mock_response.content = "**Legal Framework:** Código Fiscal de la Federación\n**Relevant Provisions:** ISR and IVA regulations..."
        
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.__or__ = Mock(return_value=mock_chain)
        
        # Execute
        result = await general_legal_researcher.interact(state)
        
        # Assertions
        assert isinstance(result, str)
        assert "Código Fiscal" in result
        assert "ISR" in result or "IVA" in result
        
        # Verify LLM temperature setting
        mock_llm_service.get_llm.assert_called_once_with(temperature=0.5)

    @pytest.mark.asyncio
    async def test_interact_empty_response_handling(self, general_legal_researcher, mock_prompt_service, mock_llm_service):
        state = State({
            "input": "Tell me about obscure legal topic",
            "agent_id": "test_agent",
            "user_id": "test_user",
            "chat_history": []
        })
        
        # Mock setup for empty/whitespace response
        mock_llm = Mock(spec=ChatOpenAI)
        mock_llm_service.get_llm.return_value = mock_llm
        
        mock_prompt = Mock()
        mock_prompt_service.custom_prompt_template.return_value = mock_prompt
        
        mock_response = Mock()
        mock_response.content = "   \n  \t  "  # Whitespace content
        
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.__or__ = Mock(return_value=mock_chain)
        
        # Execute
        result = await general_legal_researcher.interact(state)
        
        # Assertions - should return empty string after strip()
        assert result == ""
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_prompt_template_system_message_content(self, general_legal_researcher, mock_prompt_service, mock_llm_service):
        state = State({
            "input": "Test query",
            "agent_id": "test_agent",
            "user_id": "test_user"
        })
        
        # Mock setup
        mock_llm = Mock(spec=ChatOpenAI)
        mock_llm_service.get_llm.return_value = mock_llm
        
        mock_prompt = Mock()
        mock_prompt_service.custom_prompt_template.return_value = mock_prompt
        
        mock_response = Mock()
        mock_response.content = "Test response"
        
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.__or__ = Mock(return_value=mock_chain)
        
        # Execute
        await general_legal_researcher.interact(state)
        
        # Get the system message that was passed
        call_args = mock_prompt_service.custom_prompt_template.call_args
        system_message = call_args[1]['system_message']
        
        # Verify key elements are in the system message
        assert "Mexican Legal Research Expert" in system_message
        assert "Legal Framework" in system_message
        assert "Relevant Provisions" in system_message
        assert "Citations" in system_message
        assert "context documents" in system_message

    @pytest.mark.asyncio
    async def test_interact_with_context_enabled(self, general_legal_researcher, mock_prompt_service, mock_llm_service):
        state = State({
            "input": "Constitutional rights question",
            "agent_id": "test_agent",
            "user_id": "test_user"
        })
        
        # Mock setup
        mock_llm = Mock(spec=ChatOpenAI)
        mock_llm_service.get_llm.return_value = mock_llm
        
        mock_prompt = Mock()
        mock_prompt_service.custom_prompt_template.return_value = mock_prompt
        
        mock_response = Mock()
        mock_response.content = "Constitutional analysis result"
        
        mock_chain = Mock()
        mock_chain.ainvoke = AsyncMock(return_value=mock_response)
        mock_prompt.__or__ = Mock(return_value=mock_chain)
        
        # Execute
        result = await general_legal_researcher.interact(state)
        
        # Verify context was requested
        mock_prompt_service.custom_prompt_template.assert_called_once_with(
            state=state,
            system_message=ANY,
            with_context=True,  # Verify context is enabled
            context_collection="general_legal"  # Verify correct collection
        )
        
        assert result == "Constitutional analysis result"