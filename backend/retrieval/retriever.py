"""
Retriever — Semantic search interface for agents.

Provides a simple function to retrieve relevant knowledge chunks
before generating explanations. Used primarily by the Tutor agent.
"""

from typing import List, Dict, Any, Optional


def retrieve_context(
    query: str,
    topic: Optional[str] = None,
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant knowledge chunks for a given query.
    
    Args:
        query: The student's question or topic to search for.
        topic: Optional topic filter to narrow results.
        top_k: Number of results to return.
    
    Returns:
        List of relevant document chunks with content, title, topic, and score.
    """
    from .vector_store import get_vector_store
    
    store = get_vector_store()
    
    if store.size == 0:
        return []
    
    # Enhance query with topic context if available
    search_query = query
    if topic and topic != "General":
        search_query = f"{topic}: {query}"
    
    results = store.search(search_query, top_k=top_k)
    
    # Filter by topic if specified
    if topic and topic != "General":
        topic_lower = topic.lower()
        topic_results = [r for r in results if topic_lower in r.get("topic", "").lower()]
        if topic_results:
            results = topic_results
    
    return results


def format_context_for_prompt(results: List[Dict[str, Any]]) -> str:
    """
    Format retrieved documents into a context string for LLM prompts.
    
    Args:
        results: List of search results from retrieve_context.
    
    Returns:
        Formatted string to include in the system/user prompt.
    """
    if not results:
        return ""
    
    context_parts = ["RETRIEVED KNOWLEDGE (use to enhance your explanation):"]
    
    for i, result in enumerate(results, 1):
        title = result.get("title", "Unknown")
        content = result.get("content", "")
        score = result.get("score", 0)
        
        context_parts.append(
            f"\n[{i}] {title} (relevance: {score:.2f})\n{content}"
        )
    
    return "\n".join(context_parts)
