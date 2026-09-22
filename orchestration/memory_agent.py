#!/usr/bin/env python3
"""
Memory Agent - Episodic Memory with Mem0
Provides long-term memory for agents to learn from past interactions
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

try:
    from mem0 import Memory
except ImportError:
    Memory = None


@dataclass
class MemoryEntry:
    """Represents a memory entry"""
    id: str
    content: str
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    importance: float = 1.0  # 0.0 to 1.0


class MemoryAgent:
    """
    Episodic Memory Agent using Mem0
    Provides long-term memory for agents to learn from past interactions
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize Memory Agent
        
        Args:
            config: Mem0 configuration dict with:
                - vector_store: "chromadb", "qdrant", "faiss", "pinecone"
                - llm: LLM config for memory extraction
                - embedder: Embedding model config
        """
        if not Memory:
            raise ImportError("mem0ai not installed. Run: pip install mem0ai")
        
        self.config = config or {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "url": "http://localhost:6333",
                    "collection_name": "jarvis_memory"
                }
            },
            "llm": {
                "provider": "ollama",
                "config": {
                    "model": "qwen3:8b",
                    "temperature": 0,
                    "ollama_base_url": "http://127.0.0.1:11434",
                    "max_tokens": 1000
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {
                    "model": "nomic-embed-text",
                    "ollama_base_url": "http://127.0.0.1:11434"
                }
            }
        }
        
        self.memory = Memory.from_config(self.config)
        self.user_id = "jarvis_research"
    
    def add_memory(self, content: str, metadata: Dict = None, tags: List[str] = None, 
                   importance: float = 1.0, user_id: str = None) -> str:
        """
        Add a memory entry
        
        Args:
            content: The memory content
            metadata: Additional metadata
            tags: Tags for categorization
            importance: Importance score (0.0 to 1.0)
            user_id: User identifier (defaults to self.user_id)
            
        Returns:
            Memory ID
        """
        user_id = user_id or self.user_id
        metadata = metadata or {}
        
        # Add system metadata
        metadata.update({
            "timestamp": datetime.now().isoformat(),
            "importance": importance,
            "tags": tags or []
        })
        
        result = self.memory.add(
            content,
            user_id=user_id,
            metadata=metadata,
            infer=False  # Disable LLM extraction for speed
        )
        
        memory_id = result.get("results", [{}])[0].get("id", "") if result.get("results") else ""
        print(f"Memory added: {memory_id[:8]}... - {content[:50]}...")
        return memory_id
    
    def search_memories(self, query: str, limit: int = 5, 
                       user_id: str = None, tags: List[str] = None) -> List[Dict]:
        """
        Search memories by semantic similarity
        
        Args:
            query: Search query
            limit: Maximum results
            user_id: User identifier
            tags: Filter by tags
            
        Returns:
            List of memory entries with scores
        """
        user_id = user_id or self.user_id
        
        filters = {}
        if tags:
            filters["tags"] = {"$in": tags}
        filters["user_id"] = user_id
        
        results = self.memory.search(
            query=query,
            limit=limit,
            filters=filters
        )
        
        return results.get("results", [])
    
    def get_all_memories(self, user_id: str = None, limit: int = 100) -> List[Dict]:
        """Get all memories for a user"""
        user_id = user_id or self.user_id
        return self.memory.get_all(user_id=user_id, limit=limit)
    
    def delete_memory(self, memory_id: str, user_id: str = None) -> bool:
        """Delete a specific memory"""
        user_id = user_id or self.user_id
        try:
            self.memory.delete(memory_id, user_id=user_id)
            return True
        except Exception as e:
            print(f"Delete error: {e}")
            return False
    
    def update_memory(self, memory_id: str, content: str = None, 
                     metadata: Dict = None, user_id: str = None) -> bool:
        """Update a memory entry"""
        user_id = user_id or self.user_id
        try:
            updates = {}
            if content:
                updates["content"] = content
            if metadata:
                updates["metadata"] = metadata
            
            self.memory.update(memory_id, user_id=user_id or self.user_id, **updates)
            return True
        except Exception as e:
            print(f"Update error: {e}")
            return False
    
    def get_stats(self, user_id: str = None) -> Dict:
        """Get memory statistics"""
        user_id = user_id or self.user_id
        memories = self.get_all_memories(user_id=user_id, limit=1000)
        
        return {
            "total_memories": len(memories),
            "tags_used": self._get_all_tags(memories),
            "avg_importance": sum(m.get("metadata", {}).get("importance", 1) for m in memories) / max(len(memories), 1)
        }
    
    def _get_all_tags(self, memories: List[Dict]) -> List[str]:
        tags = set()
        for m in memories:
            tags.update(m.get("metadata", {}).get("tags", []))
        return sorted(tags)
    
    def record_error(self, error: str, context: str, resolution: str = None):
        """Record an error for learning"""
        content = f"Error in {context}: {error}"
        if resolution:
            content += f"\nResolution: {resolution}"
        
        return self.add_memory(
            content=content,
            metadata={"type": "error", "context": context, "resolution": resolution},
            tags=["error", "learning"],
            importance=0.9
        )
    
    def record_insight(self, insight: str, context: str, tags: List[str] = None):
        """Record a research insight"""
        content = f"Insight in {context}: {insight}"
        tags = tags or ["insight", "research"]
        
        return self.add_memory(
            content=content,
            metadata={"type": "insight", "context": context},
            tags=tags,
            importance=0.95
        )


class EpisodicMemoryAgent:
    """
    Higher-level agent that uses MemoryAgent for episodic memory
    Handles memory consolidation, retrieval strategies, and learning
    """
    
    def __init__(self, memory_agent: "MemoryAgent" = None):
        if memory_agent is None:
            memory_agent = MemoryAgent()
        self.memory = memory_agent
        self.interaction_history = []
    
    def record_interaction(self, user_input: str, agent_response: str, 
                          outcome: str = "success", tags: List[str] = None):
        """Record an interaction episode"""
        content = f"User: {user_input}\nAgent: {agent_response}\nOutcome: {outcome}"
        tags = tags or ["interaction"]
        tags.append(outcome)
        
        return self.memory.add_memory(
            content=content,
            metadata={"type": "interaction", "user_input": user_input, "agent_response": agent_response},
            tags=tags,
            importance=0.8
        )
    
    def record_error(self, error: str, context: str, resolution: str = None):
        """Record an error for learning"""
        content = f"Error in {context}: {error}"
        if resolution:
            content += f"\nResolution: {resolution}"
        
        return self.memory.add_memory(
            content=content,
            metadata={"type": "error", "context": context, "resolution": resolution},
            tags=["error", "learning"],
            importance=0.9
        )
    
    def record_insight(self, insight: str, context: str, tags: List[str] = None):
        """Record a research insight"""
        content = f"Insight in {context}: {insight}"
        tags = tags or ["insight", "research"]
        
        return self.memory.add_memory(
            content=content,
            metadata={"type": "insight", "context": context},
            tags=tags,
            importance=0.95
        )
    
    def retrieve_relevant_context(self, query: str, limit: int = 5) -> str:
        """Retrieve relevant past context for a query"""
        results = self.memory.search_memories(query, limit=limit)
        
        if not results:
            return "No relevant past experiences found."
        
        context_parts = []
        for r in results:
            content = r.get("memory", "")
            score = r.get("score", 0)
            context_parts.append(f"[Relevance: {score:.2f}] {content}")
        
        return "\n---\n".join(context_parts)
    
    def get_context_for_task(self, task: str) -> str:
        """Get relevant context for a task"""
        return self.retrieve_relevant_context(task)
    
    def learn_from_error(self, error: str, context: str, resolution: str = None):
        """Learn from an error"""
        return self.memory.record_error(error, context, resolution)
    
    def record_insight(self, insight: str, context: str, tags: List[str] = None):
        """Record a research insight"""
        return self.memory.record_insight(insight, context, tags)
    
    def get_lessons_learned(self, topic: str = None, limit: int = 10) -> str:
        """Get lessons learned on a topic"""
        query = topic or "lessons learned errors solutions"
        results = self.memory.search_memories(query, limit=limit, tags=["error", "learning"])
        
        lessons = []
        for r in results:
            content = r.get("memory", "")
            if "Resolution:" in content or "resolution" in content.lower():
                lessons.append(content)
        
        if not lessons:
            return "No specific lessons recorded yet."
        
        return "\n---\n".join(lessons[:5])


# ============================================================
# Memory-Enhanced Agent Base Class
# ============================================================

class MemoryEnhancedAgent:
    """Base class for agents with episodic memory"""
    
    def __init__(self, name: str, memory_agent: EpisodicMemoryAgent):
        self.name = name
        self.memory = memory_agent
    
    def remember(self, content: str, importance: float = 0.5, tags: List[str] = None):
        """Store a memory"""
        tags = tags or [self.name]
        return self.memory.memory.add_memory(
            content=content,
            metadata={"agent": self.name},
            tags=tags,
            importance=importance
        )
    
    def recall(self, query: str, limit: int = 5) -> List[Dict]:
        """Recall relevant memories"""
        return self.memory.search_memories(query, limit=limit)
    
    def retrieve_relevant_context(self, query: str, limit: int = 5) -> str:
        """Retrieve relevant context for a query"""
        results = self.memory.search_memories(query, limit=limit)
        
        if not results:
            return "No relevant past experiences found."
        
        context_parts = []
        for r in results:
            content = r.get("memory", "")
            score = r.get("score", 0)
            context_parts.append(f"[Relevance: {score:.2f}] {content}")
        
        return "\n---\n".join(context_parts)
    
    def get_context_for_task(self, task: str) -> str:
        """Get relevant context for a task"""
        return self.memory.retrieve_relevant_context(task)
    
    def learn_from_error(self, error: str, context: str, resolution: str):
        """Learn from an error"""
        return self.memory.record_error(error, context, resolution)
    
    def record_insight(self, insight: str, context: str):
        """Record a research insight"""
        return self.memory.record_insight(insight, context)


# ============================================================
# Example Usage
# ============================================================

def create_memory_agent(config: Dict = None) -> MemoryAgent:
    """Factory to create MemoryAgent"""
    return MemoryAgent(config)


def create_episodic_agent(memory_agent: MemoryAgent = None) -> EpisodicMemoryAgent:
    """Factory to create EpisodicMemoryAgent"""
    if memory_agent is None:
        memory_agent = MemoryAgent()
    return EpisodicMemoryAgent(memory_agent)


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    print("Testing Mem0 Memory Agent...")
    
    # Create memory agent
    memory = create_memory_agent()
    
    # Add some memories
    memory.add_memory(
        "MARL for WiFi scheduling works best with centralized training and decentralized execution (CTDE)",
        tags=["marl", "wifi", "insight"],
        importance=0.9
    )
    
    memory.add_memory(
        "arXiv timeout fixed by adding 60s timeout and 3 retries with exponential backoff",
        tags=["arxiv", "fix", "timeout"],
        importance=0.8
    )
    
    # Search memories
    results = memory.search_memories("MARL wifi", limit=3)
    print(f"Found {len(results)} memories about MARL wifi")
    
    for r in results:
        print(f"  - {r.get('memory', '')[:80]}... (score: {r.get('score', 0):.2f})")
    
    # Test episodic agent
    episodic = create_episodic_agent(MemoryAgent())
    
    # Record an interaction
    episodic.record_interaction(
        "How to fix arXiv timeout?",
        "Increase timeout to 60s and add 3 retries with exponential backoff",
        "success",
        tags=["arxiv", "timeout", "fix"]
    )
    
    # Get context for a task
    context = episodic.get_context_for_task("Fix arXiv timeout in PaperQA2")
    print(f"Context for task: {context[:200]}...")
    
    print("\nMem0 integration test completed!")