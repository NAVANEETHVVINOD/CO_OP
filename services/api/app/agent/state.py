from typing import TypedDict, List, Dict, Any

class AgentState(TypedDict):
    tenant_id: str
    question: str
    chat_history: List[Dict[str, str]]
    retrieved_docs: List[Dict[str, Any]]
    reranked_docs: List[Dict[str, Any]]
    final_answer: str
