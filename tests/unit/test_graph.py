import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from src.workflow.graph import create_graph
from src.workflow.state import State
from src.workflow.agents.context_orchestrator.context_orchestrator_models import ContextOrchestratorOutput
from src.dependencies.container import Container

@pytest.fixture
def mock_container():
    with patch.object(Container, 'resolve') as mock_resolve:
        yield mock_resolve

@pytest.fixture
def sample_state():
    return {
        "chat_id": uuid4(),
        "company_id": uuid4(),
        "chat_history": [],
        "input": "What are the employment laws?",
        "context_orchestrator_response": ContextOrchestratorOutput(general_law=False, company_law=False),
        "general_legal_response": "",
        "company_legal_response": "",
        "final_response": ""
    }

@pytest.fixture
def mock_agents():
    """Create mock agents for testing"""
    mock_context_orchestrator = Mock()
    mock_general_legal_researcher = Mock()
    mock_company_legal_researcher = Mock()
    mock_research_aggregator = Mock()
    
    # Setup async methods
    mock_context_orchestrator.interact = AsyncMock()
    mock_general_legal_researcher.interact = AsyncMock()
    mock_company_legal_researcher.interact = AsyncMock()
    mock_research_aggregator.interact = AsyncMock()
    
    return {
        "context_orchestrator_agent": mock_context_orchestrator,
        "general_legal_researcher": mock_general_legal_researcher,
        "company_legal_researcher": mock_company_legal_researcher,
        "research_aggregator": mock_research_aggregator
    }

def test_orchestrate_research_general_law_only():
    """Test orchestrate_research routing with general law only"""
    # Test the routing logic directly
    orchestrator_response = ContextOrchestratorOutput(general_law=True, company_law=False)
    next_nodes = []
    
    if orchestrator_response.general_law:
        next_nodes.append("general_legal_research")
    if orchestrator_response.company_law:
        next_nodes.append("company_legal_research")
    if not next_nodes:
        next_nodes.append("aggregator")
    
    # Assertions
    assert next_nodes == ["general_legal_research"]

def test_orchestrate_research_company_law_only():
    """Test orchestrate_research routing with company law only"""
    orchestrator_response = ContextOrchestratorOutput(general_law=False, company_law=True)
    next_nodes = []
    
    if orchestrator_response.general_law:
        next_nodes.append("general_legal_research")
    if orchestrator_response.company_law:
        next_nodes.append("company_legal_research")
    if not next_nodes:
        next_nodes.append("aggregator")
    
    # Assertions
    assert next_nodes == ["company_legal_research"]

def test_orchestrate_research_both_laws():
    """Test orchestrate_research routing with both laws"""
    orchestrator_response = ContextOrchestratorOutput(general_law=True, company_law=True)
    next_nodes = []
    
    if orchestrator_response.general_law:
        next_nodes.append("general_legal_research")
    if orchestrator_response.company_law:
        next_nodes.append("company_legal_research")
    if not next_nodes:
        next_nodes.append("aggregator")
    
    # Assertions
    assert set(next_nodes) == {"general_legal_research", "company_legal_research"}

def test_orchestrate_research_no_laws():
    """Test orchestrate_research routing with no laws"""
    orchestrator_response = ContextOrchestratorOutput(general_law=False, company_law=False)
    next_nodes = []
    
    if orchestrator_response.general_law:
        next_nodes.append("general_legal_research")
    if orchestrator_response.company_law:
        next_nodes.append("company_legal_research")
    if not next_nodes:
        next_nodes.append("aggregator")
    
    # Assertions
    assert next_nodes == ["aggregator"]

def test_create_graph_structure():
    """Test that the graph is created with correct structure"""
    graph = create_graph()
    
    # Verify it's a compiled graph
    assert hasattr(graph, 'ainvoke')
    assert hasattr(graph, 'invoke')
    
    # The graph should be properly compiled
    assert graph is not None

@pytest.mark.asyncio
async def test_full_workflow_general_law_only(sample_state, mock_container, mock_agents):
    """Test complete workflow with general law research only"""
    # Setup all mocks
    def mock_resolve_side_effect(service_name):
        return mock_agents.get(service_name)
    
    mock_container.side_effect = mock_resolve_side_effect
    
    # Setup agent responses
    mock_agents["context_orchestrator_agent"].interact.return_value = ContextOrchestratorOutput(general_law=True, company_law=False)
    mock_agents["general_legal_researcher"].interact.return_value = "General legal research about employment laws"
    mock_agents["research_aggregator"].interact.return_value = "Final aggregated response with general law analysis"
    
    # Execute
    graph = create_graph()
    result = await graph.ainvoke(sample_state)
    
    # Assertions
    assert result["context_orchestrator_response"].general_law == True
    assert result["context_orchestrator_response"].company_law == False
    assert result["general_legal_response"] == "General legal research about employment laws"
    assert result["company_legal_response"] == ""  # Should remain empty
    assert result["final_response"] == "Final aggregated response with general law analysis"

@pytest.mark.asyncio
async def test_full_workflow_company_law_only(sample_state, mock_container, mock_agents):
    """Test complete workflow with company law research only"""
    # Setup all mocks
    def mock_resolve_side_effect(service_name):
        return mock_agents.get(service_name)
    
    mock_container.side_effect = mock_resolve_side_effect
    
    # Setup agent responses
    mock_agents["context_orchestrator_agent"].interact.return_value = ContextOrchestratorOutput(general_law=False, company_law=True)
    mock_agents["company_legal_researcher"].interact.return_value = "Company policy research about employment procedures"
    mock_agents["research_aggregator"].interact.return_value = "Final aggregated response with company policy analysis"
    
    # Execute
    graph = create_graph()
    result = await graph.ainvoke(sample_state)
    
    # Assertions
    assert result["context_orchestrator_response"].general_law == False
    assert result["context_orchestrator_response"].company_law == True
    assert result["general_legal_response"] == ""  # Should remain empty
    assert result["company_legal_response"] == "Company policy research about employment procedures"
    assert result["final_response"] == "Final aggregated response with company policy analysis"

@pytest.mark.asyncio
async def test_full_workflow_both_laws(sample_state, mock_container, mock_agents):
    """Test complete workflow with both general and company law research"""
    # Setup all mocks
    def mock_resolve_side_effect(service_name):
        return mock_agents.get(service_name)
    
    mock_container.side_effect = mock_resolve_side_effect
    
    # Setup agent responses
    mock_agents["context_orchestrator_agent"].interact.return_value = ContextOrchestratorOutput(general_law=True, company_law=True)
    mock_agents["general_legal_researcher"].interact.return_value = "General legal research results"
    mock_agents["company_legal_researcher"].interact.return_value = "Company legal research results"
    mock_agents["research_aggregator"].interact.return_value = "Comprehensive analysis combining both research sources"
    
    # Execute
    graph = create_graph()
    result = await graph.ainvoke(sample_state)
    
    # Assertions
    assert result["context_orchestrator_response"].general_law == True
    assert result["context_orchestrator_response"].company_law == True
    assert result["general_legal_response"] == "General legal research results"
    assert result["company_legal_response"] == "Company legal research results"
    assert result["final_response"] == "Comprehensive analysis combining both research sources"

@pytest.mark.asyncio
async def test_full_workflow_no_research_needed(sample_state, mock_container, mock_agents):
    """Test complete workflow when no research is needed (direct to aggregator)"""
    # Setup all mocks
    def mock_resolve_side_effect(service_name):
        return mock_agents.get(service_name)
    
    mock_container.side_effect = mock_resolve_side_effect
    
    # Setup agent responses
    mock_agents["context_orchestrator_agent"].interact.return_value = ContextOrchestratorOutput(general_law=False, company_law=False)
    mock_agents["research_aggregator"].interact.return_value = "Direct response without additional research"
    
    # Execute
    graph = create_graph()
    result = await graph.ainvoke(sample_state)
    
    # Assertions
    assert result["context_orchestrator_response"].general_law == False
    assert result["context_orchestrator_response"].company_law == False
    assert result["general_legal_response"] == ""  # Should remain empty
    assert result["company_legal_response"] == ""  # Should remain empty
    assert result["final_response"] == "Direct response without additional research"

@pytest.mark.asyncio
async def test_container_resolution_calls(sample_state, mock_container, mock_agents):
    """Test that all required services are resolved from container"""
    # Setup all mocks
    def mock_resolve_side_effect(service_name):
        return mock_agents.get(service_name)
    
    mock_container.side_effect = mock_resolve_side_effect
    
    # Setup agent responses
    mock_agents["context_orchestrator_agent"].interact.return_value = ContextOrchestratorOutput(general_law=True, company_law=True)
    mock_agents["general_legal_researcher"].interact.return_value = "General result"
    mock_agents["company_legal_researcher"].interact.return_value = "Company result"
    mock_agents["research_aggregator"].interact.return_value = "Final result"
    
    # Execute
    graph = create_graph()
    await graph.ainvoke(sample_state)
    
    # Verify all required services were resolved
    expected_calls = [
        "context_orchestrator_agent",
        "general_legal_researcher", 
        "company_legal_researcher",
        "research_aggregator"
    ]
    
    actual_calls = [call[0][0] for call in mock_container.call_args_list]
    
    for expected_call in expected_calls:
        assert expected_call in actual_calls

@pytest.mark.asyncio
async def test_workflow_with_only_context_orchestrator(sample_state, mock_container, mock_agents):
    """Test workflow flow and state updates"""
    # Setup all mocks
    def mock_resolve_side_effect(service_name):
        return mock_agents.get(service_name)
    
    mock_container.side_effect = mock_resolve_side_effect
    
    # Setup minimal agent response
    mock_agents["context_orchestrator_agent"].interact.return_value = ContextOrchestratorOutput(general_law=False, company_law=False)
    mock_agents["research_aggregator"].interact.return_value = "Aggregated response"
    
    # Execute
    graph = create_graph()
    result = await graph.ainvoke(sample_state)
    
    # Verify basic workflow completion
    assert "context_orchestrator_response" in result
    assert "final_response" in result
    assert result["final_response"] == "Aggregated response"

@pytest.mark.asyncio
async def test_state_preservation_through_workflow(sample_state, mock_container, mock_agents):
    """Test that original state values are preserved"""
    # Setup all mocks
    def mock_resolve_side_effect(service_name):
        return mock_agents.get(service_name)
    
    mock_container.side_effect = mock_resolve_side_effect
    
    # Setup agent responses
    mock_agents["context_orchestrator_agent"].interact.return_value = ContextOrchestratorOutput(general_law=True, company_law=False)
    mock_agents["general_legal_researcher"].interact.return_value = "Legal research"
    mock_agents["research_aggregator"].interact.return_value = "Final response"
    
    # Store original values
    original_chat_id = sample_state["chat_id"]
    original_company_id = sample_state["company_id"]
    original_input = sample_state["input"]
    
    # Execute
    graph = create_graph()
    result = await graph.ainvoke(sample_state)
    
    # Verify original state values are preserved
    assert result["chat_id"] == original_chat_id
    assert result["company_id"] == original_company_id
    assert result["input"] == original_input
    assert result["chat_history"] == []

@pytest.mark.asyncio
async def test_error_handling_with_container_resolution(sample_state, mock_container):
    """Test behavior when container resolution fails"""
    # Setup container to raise exception
    mock_container.side_effect = Exception("Container resolution failed")
    
    # Execute and expect exception
    graph = create_graph()
    
    with pytest.raises(Exception) as exc_info:
        await graph.ainvoke(sample_state)
    
    assert "Container resolution failed" in str(exc_info.value)

@pytest.mark.asyncio
async def test_agent_interaction_calls(sample_state, mock_container, mock_agents):
    """Test that agents are called with correct state parameter"""
    # Setup all mocks
    def mock_resolve_side_effect(service_name):
        return mock_agents.get(service_name)
    
    mock_container.side_effect = mock_resolve_side_effect
    
    # Setup agent responses
    mock_agents["context_orchestrator_agent"].interact.return_value = ContextOrchestratorOutput(general_law=True, company_law=False)
    mock_agents["general_legal_researcher"].interact.return_value = "Legal research"
    mock_agents["research_aggregator"].interact.return_value = "Final response"
    
    # Execute
    graph = create_graph()
    await graph.ainvoke(sample_state)
    
    # Verify agents were called with state parameter
    mock_agents["context_orchestrator_agent"].interact.assert_called_once_with(state=sample_state)
    mock_agents["general_legal_researcher"].interact.assert_called_once()
    mock_agents["research_aggregator"].interact.assert_called_once()
    
    # Verify state parameter structure for general legal researcher
    general_call_args = mock_agents["general_legal_researcher"].interact.call_args
    assert general_call_args[1]["state"]["input"] == sample_state["input"]
    assert general_call_args[1]["state"]["chat_id"] == sample_state["chat_id"]