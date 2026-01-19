"""
Agentic RAG System with ReAct Pattern.

Implements a true agent that:
1. THINKS about what information is needed
2. ACTS by calling tools (graph, vector, entity lookup)
3. OBSERVES the results
4. REFLECTS on whether the answer is complete
5. Iterates until confident in the answer
"""

from typing import List, Dict, Any, Optional, TypedDict, Annotated
import operator

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from src.core.config import settings
from src.core.logging import get_logger
from src.agents.tools import ALL_TOOLS

logger = get_logger(__name__)

# Maximum iterations to prevent infinite loops
MAX_ITERATIONS = 5


# Agent state definition
class AgentState(TypedDict):
    """State maintained throughout agent execution."""
    messages: Annotated[List, operator.add]  # Conversation history
    question: str  # Original question
    iteration: int  # Current iteration count
    thoughts: List[str]  # Agent's reasoning trace
    final_answer: Optional[str]  # Final synthesized answer


# System prompt for the agent
AGENT_SYSTEM_PROMPT = """You are an intelligent knowledge base assistant with access to tools.

Your goal is to answer user questions by:
1. THINKING about what information you need
2. Using the appropriate tools to gather information
3. Combining information from multiple sources if needed
4. Providing a comprehensive, accurate answer

Available Tools:
- graph_search: Query the knowledge graph for employees, projects, departments
- vector_search: Search documents for contextual information
- entity_lookup: Look up specific entities by name and type
- get_relationships: Find how entities are connected

Strategy:
- For factual questions about entities → use graph_search or entity_lookup
- For questions about documents/policies → use vector_search  
- For complex questions → combine multiple tools
- Always verify your answer is complete before responding

When you have enough information, provide your final answer directly without calling more tools.
"""


class RAGAgent:
    """ReAct Agent for Agentic RAG."""
    
    def __init__(self):
        self._llm = None
        self._graph = None
        self.tools = ALL_TOOLS
    
    def _get_llm(self):
        """Get LLM with tool binding."""
        if self._llm is None:
            llm_config = settings.get_llm_config()
            
            if llm_config["provider"] == "openai":
                base_llm = ChatOpenAI(
                    api_key=llm_config["api_key"],
                    model=llm_config["model"],
                    temperature=0,
                )
            else:
                base_llm = ChatGroq(
                    api_key=llm_config["api_key"],
                    model_name=llm_config["model"],
                    temperature=0,
                )
            
            # Bind tools to LLM
            self._llm = base_llm.bind_tools(self.tools)
        
        return self._llm
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph execution graph."""
        
        # Create tool node
        tool_node = ToolNode(self.tools)
        
        # Define the agent node
        def agent_node(state: AgentState) -> Dict:
            """Agent reasoning node."""
            messages = state["messages"]
            iteration = state.get("iteration", 0)
            
            # Check iteration limit
            if iteration >= MAX_ITERATIONS:
                logger.warning("Max iterations reached, forcing answer")
                return {
                    "messages": [AIMessage(content="I've gathered the available information. Let me provide my answer based on what I found.")],
                    "iteration": iteration + 1,
                    "thoughts": state.get("thoughts", []) + ["Max iterations reached, providing best answer"]
                }
            
            # Call LLM
            llm = self._get_llm()
            response = llm.invoke(messages)
            
            # Track thinking
            thoughts = state.get("thoughts", [])
            if response.content:
                thoughts.append(f"Iteration {iteration + 1}: {response.content[:200]}")
            
            return {
                "messages": [response],
                "iteration": iteration + 1,
                "thoughts": thoughts
            }
        
        # Define routing logic
        def should_continue(state: AgentState) -> str:
            """Decide whether to continue or end."""
            messages = state["messages"]
            last_message = messages[-1]
            
            # If no tool calls, we're done
            if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
                return "end"
            
            # Continue to tools
            return "tools"
        
        # Build graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", agent_node)
        workflow.add_node("tools", tool_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add edges
        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        workflow.add_edge("tools", "agent")
        
        return workflow.compile()
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Execute agentic query with full reasoning trace.
        
        Args:
            question: User's question
            
        Returns:
            Dict with answer, thoughts, tools_used, etc.
        """
        logger.info(f"[AGENT] Starting agentic query: {question}")
        
        # Build graph if needed
        if self._graph is None:
            self._graph = self._build_graph()
        
        # Initial state
        initial_state = {
            "messages": [
                SystemMessage(content=AGENT_SYSTEM_PROMPT),
                HumanMessage(content=question)
            ],
            "question": question,
            "iteration": 0,
            "thoughts": [],
            "final_answer": None
        }
        
        try:
            # Execute graph
            result = self._graph.invoke(initial_state)
            
            # Extract final answer
            messages = result["messages"]
            final_message = messages[-1]
            answer = final_message.content if hasattr(final_message, "content") else str(final_message)
            
            # Extract tool calls
            tools_used = []
            for msg in messages:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tools_used.append({
                            "tool": tc["name"],
                            "args": tc["args"]
                        })
            
            response = {
                "question": question,
                "answer": answer,
                "agentic": True,
                "metadata": {
                    "iterations": result.get("iteration", 0),
                    "thoughts": result.get("thoughts", []),
                    "tools_used": tools_used,
                    "tool_count": len(tools_used),
                }
            }
            
            logger.info(f"[AGENT] Completed in {result.get('iteration', 0)} iterations, used {len(tools_used)} tools")
            return response
            
        except Exception as e:
            logger.error(f"[AGENT] Query failed: {e}")
            return {
                "question": question,
                "answer": f"Agent error: {str(e)}",
                "agentic": True,
                "metadata": {
                    "error": str(e)
                }
            }
    
    async def stream_query(self, question: str):
        """
        Stream agentic query with SSE events.
        
        Yields:
            SSE events for thoughts, tool calls, and answer
        """
        import json
        
        logger.info(f"[AGENT] Starting streaming query: {question}")
        
        yield f"event: start\ndata: {json.dumps({'question': question})}\n\n"
        
        # Build graph if needed
        if self._graph is None:
            self._graph = self._build_graph()
        
        initial_state = {
            "messages": [
                SystemMessage(content=AGENT_SYSTEM_PROMPT),
                HumanMessage(content=question)
            ],
            "question": question,
            "iteration": 0,
            "thoughts": [],
            "final_answer": None
        }
        
        try:
            # Stream through graph
            for event in self._graph.stream(initial_state):
                for node_name, node_output in event.items():
                    if node_name == "agent" and node_output.get("thoughts"):
                        thoughts = node_output["thoughts"]
                        if thoughts:
                            yield f"event: thought\ndata: {json.dumps({'thought': thoughts[-1]})}\n\n"
                    
                    if node_name == "tools":
                        for msg in node_output.get("messages", []):
                            if isinstance(msg, ToolMessage):
                                yield f"event: tool\ndata: {json.dumps({'tool': msg.name, 'result': msg.content[:200]})}\n\n"
            
            # Final answer
            result = self._graph.invoke(initial_state)
            final_message = result["messages"][-1]
            answer = final_message.content if hasattr(final_message, "content") else str(final_message)
            
            yield f"event: answer\ndata: {json.dumps({'answer': answer})}\n\n"
            yield f"event: done\ndata: {json.dumps({'iterations': result.get('iteration', 0)})}\n\n"
            
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


# Global instance
rag_agent = RAGAgent()
