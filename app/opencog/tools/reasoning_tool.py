"""
Reasoning tool for OpenManus framework.

Provides tool interface for OpenCog reasoning operations including forward
chaining, backward chaining, and rule management.
"""

import json
from typing import Any, Dict, List, Optional
from app.tool.base import BaseTool, ToolResult
from app.logger import logger


class ReasoningTool(BaseTool):
    """Tool for performing symbolic reasoning operations."""
    
    name: str = "reasoning"
    description: str = """
    Perform symbolic reasoning operations. Available operations:
    - forward_chain: Perform forward chaining inference
    - backward_chain: Perform backward chaining to prove a goal
    - add_rule: Add a custom reasoning rule
    - list_rules: List all reasoning rules
    - query_knowledge: Query knowledge with reasoning
    - explain: Explain how knowledge was derived
    - set_confidence_threshold: Set minimum confidence for inferences
    """
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": [
                    "forward_chain", "backward_chain", "add_rule", "list_rules",
                    "query_knowledge", "explain", "set_confidence_threshold"
                ],
                "description": "Reasoning operation to perform"
            },
            "max_inferences": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Maximum number of inferences for forward chaining"
            },
            "goal_pattern": {
                "type": "string",
                "description": "Goal pattern for backward chaining (JSON format)"
            },
            "max_depth": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Maximum search depth for backward chaining"
            },
            "rule_name": {
                "type": "string",
                "description": "Name of the reasoning rule"
            },
            "premises": {
                "type": "string",
                "description": "Rule premises (JSON array format)"
            },
            "conclusion": {
                "type": "string", 
                "description": "Rule conclusion (JSON object format)"
            },
            "rule_confidence": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Confidence in the rule"
            },
            "query": {
                "type": "string",
                "description": "Knowledge query text"
            },
            "atom_id": {
                "type": "integer",
                "description": "Atom ID to explain"
            },
            "confidence_threshold": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Minimum confidence threshold"
            }
        },
        "required": ["operation"]
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        self._reasoning_engine = None
    
    def set_reasoning_engine(self, reasoning_engine):
        """Set the reasoning engine instance to operate on."""
        self._reasoning_engine = reasoning_engine
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute reasoning operation."""
        if not self._reasoning_engine:
            return ToolResult(error="Reasoning engine not initialized")
        
        operation = kwargs.get("operation")
        
        try:
            if operation == "forward_chain":
                return await self._forward_chain(kwargs)
            elif operation == "backward_chain":
                return await self._backward_chain(kwargs)
            elif operation == "add_rule":
                return await self._add_rule(kwargs)
            elif operation == "list_rules":
                return await self._list_rules(kwargs)
            elif operation == "query_knowledge":
                return await self._query_knowledge(kwargs)
            elif operation == "explain":
                return await self._explain(kwargs)
            elif operation == "set_confidence_threshold":
                return await self._set_confidence_threshold(kwargs)
            else:
                return ToolResult(error=f"Unknown operation: {operation}")
                
        except Exception as e:
            logger.error(f"Reasoning tool error: {e}")
            return ToolResult(error=str(e))
    
    async def _forward_chain(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Perform forward chaining inference."""
        max_inferences = kwargs.get("max_inferences", 10)
        
        inferences = self._reasoning_engine.forward_chain(max_inferences)
        
        if inferences:
            output = f"Forward chaining completed: {len(inferences)} new inferences\n\n"
            
            for i, inference in enumerate(inferences[:10], 1):  # Show first 10
                atom = self._reasoning_engine.atomspace.get_atom(inference.atom_id)
                if atom:
                    output += f"{i}. {atom.type}('{atom.name}') "
                    output += f"[Rule: {inference.rule_name}, Confidence: {inference.confidence:.3f}]\n"
            
            if len(inferences) > 10:
                output += f"... and {len(inferences) - 10} more inferences"
                
            return ToolResult(output=output)
        else:
            return ToolResult(output="No new inferences generated")
    
    async def _backward_chain(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Perform backward chaining to prove a goal."""
        goal_pattern_str = kwargs.get("goal_pattern")
        if not goal_pattern_str:
            return ToolResult(error="goal_pattern parameter required")
        
        max_depth = kwargs.get("max_depth", 5)
        
        try:
            goal_pattern = json.loads(goal_pattern_str)
        except json.JSONDecodeError as e:
            return ToolResult(error=f"Invalid goal pattern JSON: {e}")
        
        results = self._reasoning_engine.backward_chain(goal_pattern, max_depth)
        
        if results:
            output = f"Backward chaining found {len(results)} proof steps:\n\n"
            
            for i, result in enumerate(results, 1):
                atom = self._reasoning_engine.atomspace.get_atom(result.atom_id)
                if atom:
                    output += f"{i}. {atom.type}('{atom.name}') "
                    output += f"[Rule: {result.rule_name}, Confidence: {result.confidence:.3f}]\n"
            
            return ToolResult(output=output)
        else:
            return ToolResult(output="Goal could not be proven with available knowledge")
    
    async def _add_rule(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Add a custom reasoning rule."""
        rule_name = kwargs.get("rule_name")
        premises_str = kwargs.get("premises")
        conclusion_str = kwargs.get("conclusion")
        
        if not all([rule_name, premises_str, conclusion_str]):
            return ToolResult(error="rule_name, premises, and conclusion parameters required")
        
        rule_confidence = kwargs.get("rule_confidence", 1.0)
        
        try:
            premises = json.loads(premises_str)
            conclusion = json.loads(conclusion_str)
        except json.JSONDecodeError as e:
            return ToolResult(error=f"Invalid JSON in rule definition: {e}")
        
        self._reasoning_engine.add_rule(rule_name, premises, conclusion, rule_confidence)
        
        return ToolResult(output=f"Added reasoning rule '{rule_name}' with confidence {rule_confidence}")
    
    async def _list_rules(self, kwargs: Dict[str, Any]) -> ToolResult:
        """List all reasoning rules."""
        rules = self._reasoning_engine.rules
        
        if not rules:
            return ToolResult(output="No reasoning rules defined")
        
        output = f"Reasoning rules ({len(rules)} total):\n\n"
        
        for i, rule in enumerate(rules, 1):
            output += f"{i}. {rule.name} (confidence: {rule.confidence})\n"
            output += f"   Premises: {len(rule.premises)} conditions\n"
            output += f"   Conclusion: {rule.conclusion.get('type', 'Unknown')}\n\n"
        
        return ToolResult(output=output)
    
    async def _query_knowledge(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Query knowledge with reasoning."""
        query = kwargs.get("query")
        if not query:
            return ToolResult(error="query parameter required")
        
        results = self._reasoning_engine.query_knowledge(query)
        
        if results:
            output = f"Knowledge query results for '{query}':\n\n"
            
            for i, result in enumerate(results[:10], 1):
                output += f"{i}. {result.get('type', 'Unknown')}('{result.get('name', '')}')\n"
                truth_value = result.get('truth_value', {})
                if truth_value:
                    output += f"   Truth: strength={truth_value.get('strength', 1.0):.3f}, "
                    output += f"confidence={truth_value.get('confidence', 1.0):.3f}\n"
                output += f"   Relevance: {result.get('relevance', 1.0):.3f}\n\n"
            
            if len(results) > 10:
                output += f"... and {len(results) - 10} more results"
                
            return ToolResult(output=output)
        else:
            return ToolResult(output=f"No knowledge found for query '{query}'")
    
    async def _explain(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Explain how knowledge was derived."""
        atom_id = kwargs.get("atom_id")
        if atom_id is None:
            return ToolResult(error="atom_id parameter required")
        
        explanation = self._reasoning_engine.explain_inference(atom_id)
        
        if "error" in explanation:
            return ToolResult(error=explanation["error"])
        
        output = f"Explanation for atom {atom_id}:\n\n"
        output += f"Type: {explanation.get('type', 'Unknown')}\n"
        output += f"Name: '{explanation.get('name', '')}'\n"
        
        truth_value = explanation.get('truth_value', {})
        if truth_value:
            output += f"Truth Value: strength={truth_value.get('strength', 1.0):.3f}, "
            output += f"confidence={truth_value.get('confidence', 1.0):.3f}\n"
        
        output += f"\nExplanation: {explanation.get('explanation', 'No explanation available')}"
        
        return ToolResult(output=output)
    
    async def _set_confidence_threshold(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Set minimum confidence threshold for inferences."""
        threshold = kwargs.get("confidence_threshold")
        if threshold is None:
            return ToolResult(error="confidence_threshold parameter required")
        
        self._reasoning_engine.min_confidence = threshold
        
        return ToolResult(output=f"Set confidence threshold to {threshold}")