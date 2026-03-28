"""
Agent System Tests

Tests for the Research Agent (Phase 0) and placeholders for future agents.
Verifies that agents use environment variables for LLM configuration.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.agent.graph import create_research_graph
from app.agent.state import AgentState
from app.config import get_settings


class TestResearchAgent:
    """Tests for Research Agent (Phase 0 - currently implemented)"""
    
    @pytest.mark.asyncio
    async def test_research_agent_uses_environment_variables(self):
        """Verify Research Agent uses environment variables for LLM configuration"""
        settings = get_settings()
        
        # Verify required environment variables are set
        assert settings.OLLAMA_URL is not None, "OLLAMA_URL must be set"
        assert settings.LITELLM_URL is not None or settings.OLLAMA_URL is not None, \
            "Either LITELLM_URL or OLLAMA_URL must be set"
        
        # Verify agent can be created with environment configuration
        graph = create_research_graph()
        assert graph is not None, "Research graph should be created successfully"
    
    @pytest.mark.asyncio
    async def test_research_agent_basic_query(self):
        """Test Research Agent with a sample query"""
        # Mock the search and reranker to avoid actual API requests
        with patch('app.agent.nodes.embedder') as mock_embedder, \
             patch('app.agent.nodes._perform_search') as mock_search, \
             patch('app.agent.nodes.reranker') as mock_reranker:
            
            # Mock embedder
            mock_embedder.embed_text = AsyncMock(return_value=[0.1] * 384)
            
            # Mock search results
            mock_search.return_value = []
            
            # Mock reranker
            mock_reranker.rerank = AsyncMock(return_value=[])
            
            graph = create_research_graph()
            
            # Create initial state
            initial_state = AgentState(
                question="What is the capital of France?",
                tenant_id="test-tenant",
                retrieved_docs=[],
                reranked_docs=[],
                final_answer=""
            )
            
            # Run the graph
            result = await graph.ainvoke(initial_state)
            
            # Verify result structure
            assert "final_answer" in result
            assert isinstance(result["final_answer"], str)
    
    @pytest.mark.asyncio
    async def test_research_agent_environment_configuration(self):
        """Verify agent respects environment configuration"""
        settings = get_settings()
        
        # Check that agent configuration uses settings
        assert settings.ENVIRONMENT in ["local", "development", "staging", "production"]
        assert settings.LOG_LEVEL in ["DEBUG", "INFO", "WARNING", "ERROR"]
        
        # Verify simulation mode flag
        assert isinstance(settings.COOP_SIMULATION_MODE, bool)


class TestFutureAgents:
    """Placeholder tests for Phase 2 agents"""
    
    @pytest.mark.skip(reason="Lead Scout not implemented in Phase 0")
    @pytest.mark.asyncio
    async def test_lead_scout_agent(self):
        """Test Lead Scout Agent (Phase 2)"""
        # Placeholder for future implementation
        pass
    
    @pytest.mark.skip(reason="Proposal Writer not implemented in Phase 0")
    @pytest.mark.asyncio
    async def test_proposal_writer_agent(self):
        """Test Proposal Writer Agent (Phase 2)"""
        # Placeholder for future implementation
        pass
    
    @pytest.mark.skip(reason="Finance Manager not implemented in Phase 0")
    @pytest.mark.asyncio
    async def test_finance_manager_agent(self):
        """Test Finance Manager Agent (Phase 2)"""
        # Placeholder for future implementation
        pass


class TestAgentConfiguration:
    """Tests for agent configuration and environment variables"""
    
    def test_agent_uses_correct_llm_url(self):
        """Verify agents use correct LLM URL from environment"""
        settings = get_settings()
        
        # Check LiteLLM URL if configured
        if settings.LITELLM_URL:
            assert "http" in settings.LITELLM_URL.lower()
        
        # Check Ollama URL
        assert "http" in settings.OLLAMA_URL.lower()
        assert "ollama" in settings.OLLAMA_URL.lower() or "11434" in settings.OLLAMA_URL
    
    def test_agent_configuration_validation(self):
        """Verify agent configuration is valid"""
        settings = get_settings()
        
        # Verify required settings for agents
        assert settings.DATABASE_URL is not None
        assert settings.REDIS_URL is not None
        
        # Verify optional agent settings
        if settings.ENVIRONMENT == "production":
            assert settings.OLLAMA_URL is not None
            assert settings.API_BASE_URL is not None
