from typing import Dict, Any
from app.rag.retriever import rag_retriever

class RAGAgent:
    """
    Agent 3 — RAG Retrieval Agent
    Responsibilities:
    - Query vector DB based on ticket message and category.
    - Retrieve top-k relevant documentation chunks and source metadata.
    """
    async def process(self, ticket: Dict[str, Any], classification: Dict[str, Any]) -> Dict[str, Any]:
        message = ticket.get("customer_message", "")
        category = classification.get("category", "")
        search_query = f"{category}: {message}"
        
        retrieved_result = rag_retriever.retrieve(query=search_query)
        return retrieved_result

rag_agent = RAGAgent()
