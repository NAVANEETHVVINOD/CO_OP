from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState
from app.agent.nodes import retrieve_docs, rerank_results, generate_answer

def create_research_graph() -> StateGraph:
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("retrieve_docs", retrieve_docs)
    workflow.add_node("rerank_results", rerank_results)
    workflow.add_node("generate_answer", generate_answer)
    
    # Add edges
    workflow.add_edge(START, "retrieve_docs")
    workflow.add_edge("retrieve_docs", "rerank_results")
    workflow.add_edge("rerank_results", "generate_answer")
    workflow.add_edge("generate_answer", END)
    
    # Compile graph
    app = workflow.compile()
    
    return app

research_agent = create_research_graph()
