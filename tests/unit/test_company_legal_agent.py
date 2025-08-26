import pytest
from unittest.mock import Mock, AsyncMock, ANY
from src.workflow.agents.company_legal_research.company_legal_research_agent import CompanyLegalResearcher
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
    return llm

@pytest.fixture
def company_legal_researcher(mock_prompt_service, mock_llm_service):
    return CompanyLegalResearcher(mock_prompt_service, mock_llm_service)

@pytest.fixture
def sample_state():
    return State({
        "input": "What are our company's employment policies?",
        "agent_id": "test_agent",
        "user_id": "test_user",
        "company_id": "test_company",
        "chat_history": []
    })

@pytest.mark.asyncio
async def test_interact_employment_policy_query(company_legal_researcher, sample_state, mock_prompt_service, mock_llm_service):
    # Mock the LLM service
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    # Mock the prompt template
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    # Mock the chain response
    mock_response = Mock()
    mock_response.content = "**Document Type:** Employment Policy\n**Relevant Clauses:** Section 3.1 - Working Hours..."
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await company_legal_researcher.interact(sample_state)
    
    # Assertions
    assert isinstance(result, str)
    assert "Document Type" in result
    assert "Employment Policy" in result
    
    # Verify method calls
    mock_llm_service.get_llm.assert_called_once_with(temperature=0.1, max_tokens=2000)
    mock_prompt_service.custom_prompt_template.assert_called_once_with(
        state=sample_state,
        system_message=ANY,
        with_context=True,
        context_collection="test_company_company_docs"
    )
    mock_chain.ainvoke.assert_called_once_with({"input": sample_state["input"]})

@pytest.mark.asyncio
async def test_interact_vendor_contract_query(company_legal_researcher, mock_prompt_service, mock_llm_service):
    state = State({
        "input": "What are the terms in our vendor agreements?",
        "agent_id": "test_agent",
        "user_id": "test_user",
        "company_id": "test_company",
        "chat_history": []
    })
    
    # Mock setup
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_response = Mock()
    mock_response.content = "**Document Type:** Vendor Agreement\n**Relevant Clauses:** Payment terms clause 4.2..."
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await company_legal_researcher.interact(state)
    
    # Assertions
    assert isinstance(result, str)
    assert "Vendor Agreement" in result
    assert "Payment terms" in result
    
    # Verify collection name with company_id
    mock_prompt_service.custom_prompt_template.assert_called_once_with(
        state=state,
        system_message=ANY,
        with_context=True,
        context_collection="test_company_company_docs"
    )

@pytest.mark.asyncio
async def test_interact_compliance_document_query(company_legal_researcher, mock_prompt_service, mock_llm_service):
    state = State({
        "input": "What compliance certifications do we have?",
        "agent_id": "test_agent",
        "user_id": "test_user",
        "company_id": "acme_corp",
        "chat_history": []
    })
    
    # Mock setup
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_response = Mock()
    mock_response.content = "**Document Type:** Compliance Certificate\n**Relevant Clauses:** ISO 27001 certification valid until..."
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await company_legal_researcher.interact(state)
    
    # Assertions
    assert isinstance(result, str)
    assert "Compliance Certificate" in result
    assert "ISO 27001" in result
    
    # Verify collection name with different company_id
    mock_prompt_service.custom_prompt_template.assert_called_once_with(
        state=state,
        system_message=ANY,
        with_context=True,
        context_collection="acme_corp_company_docs"
    )

@pytest.mark.asyncio
async def test_interact_corporate_governance_query(company_legal_researcher, mock_prompt_service, mock_llm_service):
    state = State({
        "input": "What are our board resolution procedures?",
        "agent_id": "test_agent",
        "user_id": "test_user",
        "company_id": "test_company",
        "chat_history": []
    })
    
    # Mock setup
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_response = Mock()
    mock_response.content = "**Document Type:** Corporate Bylaws\n**Relevant Clauses:** Article 5 - Board Resolutions..."
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await company_legal_researcher.interact(state)
    
    # Assertions
    assert isinstance(result, str)
    assert "Corporate Bylaws" in result
    assert "Board Resolutions" in result
    
    # Verify LLM parameters
    mock_llm_service.get_llm.assert_called_once_with(temperature=0.1, max_tokens=2000)

@pytest.mark.asyncio
async def test_interact_empty_response_handling(company_legal_researcher, mock_prompt_service, mock_llm_service):
    state = State({
        "input": "Tell me about non-existent policy",
        "agent_id": "test_agent",
        "user_id": "test_user",
        "company_id": "test_company",
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
    result = await company_legal_researcher.interact(state)
    
    # Assertions - should return empty string after strip()
    assert result == ""
    assert isinstance(result, str)

@pytest.mark.asyncio
async def test_prompt_template_system_message_content(company_legal_researcher, mock_prompt_service, mock_llm_service):
    state = State({
        "input": "Test company query",
        "agent_id": "test_agent",
        "user_id": "test_user",
        "company_id": "test_company"
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
    await company_legal_researcher.interact(state)
    
    # Get the system message that was passed
    call_args = mock_prompt_service.custom_prompt_template.call_args
    system_message = call_args[1]['system_message']
    
    # Verify key elements are in the system message
    assert "Company Legal Document Specialist" in system_message
    assert "Extract relevant provisions" in system_message
    assert "company contracts and policies" in system_message
    assert "compliance status" in system_message
    assert "provided context" in system_message

@pytest.mark.asyncio
async def test_interact_with_context_enabled(company_legal_researcher, mock_prompt_service, mock_llm_service):
    state = State({
        "input": "IP licensing agreements",
        "agent_id": "test_agent",
        "user_id": "test_user",
        "company_id": "tech_corp"
    })
    
    # Mock setup
    mock_llm = Mock(spec=ChatOpenAI)
    mock_llm_service.get_llm.return_value = mock_llm
    
    mock_prompt = Mock()
    mock_prompt_service.custom_prompt_template.return_value = mock_prompt
    
    mock_response = Mock()
    mock_response.content = "IP licensing analysis result"
    
    mock_chain = Mock()
    mock_chain.ainvoke = AsyncMock(return_value=mock_response)
    mock_prompt.__or__ = Mock(return_value=mock_chain)
    
    # Execute
    result = await company_legal_researcher.interact(state)
    
    # Verify context was requested with correct collection
    mock_prompt_service.custom_prompt_template.assert_called_once_with(
        state=state,
        system_message=ANY,
        with_context=True,  # Verify context is enabled
        context_collection="tech_corp_company_docs"  # Verify dynamic collection name
    )
    
    assert result == "IP licensing analysis result"

@pytest.mark.asyncio
async def test_collection_name_generation(company_legal_researcher, mock_prompt_service, mock_llm_service):
    """Test that collection names are properly generated from company_id"""
    
    # Test different company IDs
    test_cases = [
        ("company_123", "company_123_company_docs"),
        ("acme-corp", "acme-corp_company_docs"),
        ("test_co", "test_co_company_docs")
    ]
    
    for company_id, expected_collection in test_cases:
        state = State({
            "input": f"Test query for {company_id}",
            "agent_id": "test_agent", 
            "user_id": "test_user",
            "company_id": company_id
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
        await company_legal_researcher.interact(state)
        
        # Verify collection name
        call_args = mock_prompt_service.custom_prompt_template.call_args
        assert call_args[1]['context_collection'] == expected_collection
        
        # Reset mocks for next iteration
        mock_prompt_service.reset_mock()
        mock_llm_service.reset_mock()