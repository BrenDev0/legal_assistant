import pytest
from unittest.mock import Mock, AsyncMock, ANY
from src.workflow.agents.context_orchestrator.agent import ContextOrchestrator
from src.workflow.agents.context_orchestrator.models import ContextOrchestratorOutput
from src.workflow.services.prompt_service import PromptService
from src.workflow.services.llm_service import LlmService
from src.workflow.state import State
from langchain_openai import ChatOpenAI

@pytest.fixture
def mock_prompt_service():
    return Mock(spec=PromptService)

@pytest.fixture
def mock_llm_service():
    return Mock(spec=LlmService)

@pytest.fixture
def mock_llm():
    llm = Mock(spec=ChatOpenAI)
    structured_llm = Mock()
    llm.with_structured_output.return_value = structured_llm
    return llm, structured_llm

@pytest.fixture
def routing_agent(mock_prompt_service, mock_llm_service):
    return ContextOrchestrator(mock_prompt_service, mock_llm_service)

@pytest.fixture
def sample_state():
    return State({
        "input": "What are the employment laws in California?",
        "agent_id": "test_agent",
        "user_id": "test_user",
        "chat_history": []
    })

@pytest.mark.asyncio
async def test_interact_general_law_only(routing_agent, mock_llm, sample_state, mock_prompt_service, mock_llm_service):
    llm, structured_llm = mock_llm
    
    # Mock the LLM service
    mock_llm_service.get_llm.return_value = llm
    
    # Mock the prompt template  
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    # Mock the chain
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=ContextOrchestratorOutput(
        general_law=True,
        company_law=False
    ))
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await routing_agent.interact(sample_state)
    
    # Assertions
    assert isinstance(result, ContextOrchestratorOutput)
    assert result.general_law == True
    assert result.company_law == False
    
    # Verify method calls
    mock_llm_service.get_llm.assert_called_once_with(temperature=0.1)
    mock_prompt_service.custom_prompt_template.assert_called_once_with(
        state=sample_state, 
        system_message=ANY,
        with_chat_history=True
    )
    llm.with_structured_output.assert_called_once_with(ContextOrchestratorOutput)

@pytest.mark.asyncio
async def test_interact_company_law_only(routing_agent, mock_llm, mock_prompt_service, mock_llm_service):
    llm, structured_llm = mock_llm
    
    state = State({
        "input": "Review our employment contract",
        "agent_id": "test_agent", 
        "user_id": "test_user",
        "chat_history": []
    })
    
    # Mock setup
    mock_llm_service.get_llm.return_value = llm
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=ContextOrchestratorOutput(
        general_law=False,
        company_law=True
    ))
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await routing_agent.interact(state)
    
    # Assertions
    assert result.general_law == False
    assert result.company_law == True

@pytest.mark.asyncio
async def test_interact_all_fields_true(routing_agent, mock_llm, mock_prompt_service, mock_llm_service):
    llm, structured_llm = mock_llm
    
    state = State({
        "input": "Is our privacy policy still compliant with what we discussed last week?",
        "agent_id": "test_agent",
        "user_id": "test_user", 
        "chat_history": [{"sender": "client", "text": "Previous conversation"}]
    })
    
    # Mock setup
    mock_llm_service.get_llm.return_value = llm
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=ContextOrchestratorOutput(
        general_law=True,
        company_law=True
    ))
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await routing_agent.interact(state)
    
    # Assertions
    assert result.general_law == True
    assert result.company_law == True

@pytest.mark.asyncio
async def test_interact_no_fields_true(routing_agent, mock_llm, mock_prompt_service, mock_llm_service):
    llm, structured_llm = mock_llm
    
    state = State({
        "input": "Hello, how are you?",
        "agent_id": "test_agent",
        "user_id": "test_user",
        "chat_history": []
    })
    
    # Mock setup  
    mock_llm_service.get_llm.return_value = llm
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=ContextOrchestratorOutput(
        general_law=False,
        company_law=False
    ))
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await routing_agent.interact(state)
    
    # Assertions
    assert result.general_law == False
    assert result.company_law == False

@pytest.mark.asyncio
async def test_interact_system_message_validation(routing_agent, mock_llm, sample_state, mock_prompt_service, mock_llm_service):
    llm, structured_llm = mock_llm
    
    # Mock setup
    mock_llm_service.get_llm.return_value = llm
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=ContextOrchestratorOutput(
        general_law=True,
        company_law=False
    ))
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    await routing_agent.interact(sample_state)
    
    # Get the system message that was passed
    call_args = mock_prompt_service.custom_prompt_template.call_args
    system_message = call_args[1]['system_message']
    
    # Verify key elements are in the system message
    assert "legal context orchestrator" in system_message
    assert "general_law" in system_message
    assert "company_law" in system_message
    assert "employment laws" in system_message

@pytest.mark.asyncio
async def test_interact_structured_output_configuration(routing_agent, mock_llm, sample_state, mock_prompt_service, mock_llm_service):
    llm, structured_llm = mock_llm
    
    # Mock setup
    mock_llm_service.get_llm.return_value = llm
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=ContextOrchestratorOutput(
        general_law=True,
        company_law=False
    ))
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await routing_agent.interact(sample_state)
    
    # Verify structured output was configured correctly
    llm.with_structured_output.assert_called_once_with(ContextOrchestratorOutput)
    
    # Verify the chain was created and called
    mock_chain.ainvoke.assert_called_once_with({"input": sample_state["input"]})
    
    # Verify return type
    assert isinstance(result, ContextOrchestratorOutput)

@pytest.mark.asyncio
async def test_interact_llm_service_parameters(routing_agent, mock_llm, sample_state, mock_prompt_service, mock_llm_service):
    llm, structured_llm = mock_llm
    
    # Mock setup
    mock_llm_service.get_llm.return_value = llm
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=ContextOrchestratorOutput(
        general_law=True,
        company_law=False
    ))
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    await routing_agent.interact(sample_state)
    
    # Verify LLM service called with correct temperature
    mock_llm_service.get_llm.assert_called_once_with(temperature=0.1)

@pytest.mark.asyncio
async def test_interact_prompt_template_parameters(routing_agent, mock_llm, sample_state, mock_prompt_service, mock_llm_service):
    llm, structured_llm = mock_llm
    
    # Mock setup
    mock_llm_service.get_llm.return_value = llm
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=ContextOrchestratorOutput(
        general_law=True,
        company_law=False
    ))
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    await routing_agent.interact(sample_state)
    
    # Verify prompt template called with correct parameters
    mock_prompt_service.custom_prompt_template.assert_called_once_with(
        state=sample_state,
        system_message=ANY,
        with_chat_history=True
    )