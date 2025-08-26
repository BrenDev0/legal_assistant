import pytest
from unittest.mock import Mock, AsyncMock, ANY
from src.workflow.agents.research_aggregator.research_aggregator_agent import ResearchAggregator
from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.workflow.state import State
from src.workflow.agents.context_orchestrator.context_orchestrator_models import ContextOrchestratorOutput
from langchain_openai import ChatOpenAI
from uuid import uuid4

@pytest.fixture
def mock_prompt_service():
    return Mock(spec=PromptService)

@pytest.fixture
def mock_llm_service():
    return Mock(spec=LlmService)

@pytest.fixture
def mock_llm():
    llm = Mock(spec=ChatOpenAI)
    return llm

@pytest.fixture
def research_aggregator(mock_prompt_service, mock_llm_service):
    return ResearchAggregator(mock_prompt_service, mock_llm_service)

@pytest.fixture
def base_state():
    return State({
        "chat_id": uuid4(),
        "company_id": uuid4(),
        "chat_history": [],
        "input": "What are the employment laws for our company?",
        "context_orchestrator_response": ContextOrchestratorOutput(general_law=True, company_law=True),
        "general_legal_response": "",
        "company_legal_response": "",
        "final_response": ""
    })

@pytest.mark.asyncio
async def test_interact_with_both_research_responses(research_aggregator, base_state, mock_prompt_service, mock_llm_service):
    # Set up state with both research responses
    state = base_state.copy()
    state["general_legal_response"] = "**Legal Framework:** Ley Federal del Trabajo - Article 123"
    state["company_legal_response"] = "**Document Type:** Employment Policy - Section 2.1 Working Hours"
    
    # Mock the LLM service
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    # Mock the prompt template
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    # Mock the chain response
    mock_response = Mock()
    mock_response.content = "**Legal Overview:** Employment laws combine federal requirements with company policies..."
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await research_aggregator.interact(state)
    
    # Assertions
    assert isinstance(result, str)
    assert "Legal Overview" in result
    assert "Employment laws" in result
    
    # Verify method calls
    mock_llm_service.get_llm.assert_called_once_with(temperature=0.5, max_tokens=2500)
    mock_prompt_service.custom_prompt_template.assert_called_once_with(
        state=state,
        system_message=ANY,
        with_chat_history=True
    )
    mock_chain.ainvoke.assert_called_once_with({"input": state["input"]})

@pytest.mark.asyncio
async def test_interact_with_general_legal_only(research_aggregator, base_state, mock_prompt_service, mock_llm_service):
    # Set up state with only general legal response
    state = base_state.copy()
    state["general_legal_response"] = "**Legal Framework:** Mexican Constitution Article 123 - Labor Rights"
    
    # Mock setup
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_response = Mock()
    mock_response.content = "**Legal Overview:** Based on Mexican constitutional law..."
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await research_aggregator.interact(state)
    
    # Assertions
    assert isinstance(result, str)
    assert "Legal Overview" in result
    assert "constitutional law" in result

@pytest.mark.asyncio
async def test_interact_with_company_legal_only(research_aggregator, base_state, mock_prompt_service, mock_llm_service):
    # Set up state with only company legal response
    state = base_state.copy()
    state["company_legal_response"] = "**Document Type:** HR Policy - Vacation and Leave Procedures"
    
    # Mock setup
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_response = Mock()
    mock_response.content = "**Company Policy:** According to internal HR policies..."
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await research_aggregator.interact(state)
    
    # Assertions
    assert isinstance(result, str)
    assert "Company Policy" in result
    assert "HR policies" in result

@pytest.mark.asyncio
async def test_interact_with_no_research_responses(research_aggregator, base_state, mock_prompt_service, mock_llm_service):
    # Set up state with no research responses (empty strings)
    state = base_state.copy()
    
    # Mock setup
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_response = Mock()
    mock_response.content = "I don't have specific legal research available for this query."
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await research_aggregator.interact(state)
    
    # Assertions
    assert isinstance(result, str)
    assert "don't have specific" in result

@pytest.mark.asyncio
async def test_interact_with_chat_history_response(research_aggregator, base_state, mock_prompt_service, mock_llm_service):
    # Set up state with chat history response
    state = base_state.copy()
    state["general_legal_response"] = "**Legal Framework:** Labor Law provisions"
    state["chat_history_response"] = "**Previous Discussion:** User asked about overtime policies last week"
    
    # Mock setup
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_response = Mock()
    mock_response.content = "**Previous Discussion:** Continuing from our overtime discussion..."
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await research_aggregator.interact(state)
    
    # Assertions
    assert isinstance(result, str)
    assert "Previous Discussion" in result
    assert "overtime" in result

@pytest.mark.asyncio
async def test_system_message_context_building(research_aggregator, base_state, mock_prompt_service, mock_llm_service):
    # Set up state with all types of responses
    state = base_state.copy()
    state["general_legal_response"] = "General legal context"
    state["company_legal_response"] = "Company specific context"
    state["chat_history_response"] = "Chat history context"
    
    # Mock setup
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_response = Mock()
    mock_response.content = "Comprehensive response"
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    await research_aggregator.interact(state)
    
    # Get the system message that was passed
    call_args = mock_prompt_service.custom_prompt_template.call_args
    system_message = call_args[1]['system_message']
    
    # Verify all research contexts are included in system message
    assert "GENERAL LEGAL RESEARCH:" in system_message
    assert "General legal context" in system_message
    assert "COMPANY LEGAL RESEARCH:" in system_message
    assert "Company specific context" in system_message
    assert "CHAT HISTORY CONTEXT:" in system_message
    assert "Chat history context" in system_message
    
    # Verify system message structure
    assert "Legal Research Aggregator" in system_message
    assert "Response Structure:" in system_message
    assert "Legal Overview:" in system_message
    assert "Guidelines:" in system_message

@pytest.mark.asyncio
async def test_system_message_no_research_available(research_aggregator, base_state, mock_prompt_service, mock_llm_service):
    # Set up state with no research responses
    state = base_state.copy()
    
    # Mock setup
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_response = Mock()
    mock_response.content = "No research available"
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    await research_aggregator.interact(state)
    
    # Get the system message that was passed
    call_args = mock_prompt_service.custom_prompt_template.call_args
    system_message = call_args[1]['system_message']
    
    # Verify fallback message is included
    assert "No additional research context available." in system_message

@pytest.mark.asyncio
async def test_interact_empty_response_handling(research_aggregator, base_state, mock_prompt_service, mock_llm_service):
    # Set up state
    state = base_state.copy()
    
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
    result = await research_aggregator.interact(state)
    
    # Assertions - should return empty string after strip()
    assert result == ""
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_interact_llm_service_parameters(research_aggregator, base_state, mock_prompt_service, mock_llm_service):
    # Set up state
    state = base_state.copy()
    
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
    await research_aggregator.interact(state)
    
    # Verify LLM service called with correct parameters
    mock_llm_service.get_llm.assert_called_once_with(temperature=0.5, max_tokens=2500)

@pytest.mark.asyncio
async def test_interact_prompt_service_parameters(research_aggregator, base_state, mock_prompt_service, mock_llm_service):
    # Set up state
    state = base_state.copy()
    
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
    await research_aggregator.interact(state)
    
    # Verify prompt service called with correct parameters
    mock_prompt_service.custom_prompt_template.assert_called_once_with(
        state=state,
        system_message=ANY,
        with_chat_history=True
    )