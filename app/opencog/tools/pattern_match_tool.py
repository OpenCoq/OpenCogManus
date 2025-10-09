"""
Pattern matching tool for OpenManus framework.

Provides tool interface for advanced pattern matching operations on the AtomSpace.
"""

import json
from typing import Any, Dict, List, Optional
from app.tool.base import BaseTool, ToolResult
from app.logger import logger


class PatternMatchTool(BaseTool):
    """Tool for advanced pattern matching operations."""
    
    name: str = "pattern_match"
    description: str = """
    Perform advanced pattern matching on the AtomSpace. Available operations:
    - match_pattern: Match a structured pattern against atoms
    - match_query: Match a string query pattern
    - find_similar: Find atoms similar to a target atom
    - find_connected: Find atoms connected through links
    - create_variable: Create a pattern matching variable
    - explain_match: Explain how a match was found
    """
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": [
                    "match_pattern", "match_query", "find_similar", 
                    "find_connected", "create_variable", "explain_match"
                ],
                "description": "Pattern matching operation to perform"
            },
            "pattern": {
                "type": "string",
                "description": "Pattern to match (JSON format)"
            },
            "query": {
                "type": "string",
                "description": "String query pattern"
            },
            "target_atom_id": {
                "type": "integer",
                "description": "Target atom ID for similarity or connection search"
            },
            "similarity_threshold": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Minimum similarity threshold"
            },
            "max_depth": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Maximum depth for connection traversal"
            },
            "connection_types": {
                "type": "string",
                "description": "Connection types to follow (JSON array)"
            },
            "variable_name": {
                "type": "string", 
                "description": "Name for pattern variable"
            },
            "type_constraint": {
                "type": "string",
                "description": "Type constraint for variable"
            },
            "value_constraint": {
                "type": "string",
                "description": "Value constraint (regex) for variable"
            },
            "match_result": {
                "type": "string",
                "description": "Match result to explain (JSON format)"
            },
            "max_results": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "description": "Maximum number of results to return"
            }
        },
        "required": ["operation"]
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        self._pattern_matcher = None
    
    def set_pattern_matcher(self, pattern_matcher):
        """Set the pattern matcher instance to operate on."""
        self._pattern_matcher = pattern_matcher
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute pattern matching operation."""
        if not self._pattern_matcher:
            return ToolResult(error="Pattern matcher not initialized")
        
        operation = kwargs.get("operation")
        
        # Set max_results if provided
        max_results = kwargs.get("max_results")
        if max_results:
            original_max = self._pattern_matcher.max_results
            self._pattern_matcher.max_results = max_results
        
        try:
            if operation == "match_pattern":
                result = await self._match_pattern(kwargs)
            elif operation == "match_query":
                result = await self._match_query(kwargs)
            elif operation == "find_similar":
                result = await self._find_similar(kwargs)
            elif operation == "find_connected":
                result = await self._find_connected(kwargs)
            elif operation == "create_variable":
                result = await self._create_variable(kwargs)
            elif operation == "explain_match":
                result = await self._explain_match(kwargs)
            else:
                result = ToolResult(error=f"Unknown operation: {operation}")
            
            # Restore original max_results
            if max_results:
                self._pattern_matcher.max_results = original_max
                
            return result
                
        except Exception as e:
            logger.error(f"Pattern match tool error: {e}")
            if max_results:
                self._pattern_matcher.max_results = original_max
            return ToolResult(error=str(e))
    
    async def _match_pattern(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Match a structured pattern against atoms."""
        pattern_str = kwargs.get("pattern")
        if not pattern_str:
            return ToolResult(error="pattern parameter required")
        
        try:
            pattern_dict = json.loads(pattern_str)
        except json.JSONDecodeError as e:
            return ToolResult(error=f"Invalid pattern JSON: {e}")
        
        # Convert dictionary to Pattern object
        pattern = self._dict_to_pattern(pattern_dict)
        if not pattern:
            return ToolResult(error="Could not create pattern from dictionary")
        
        matches = self._pattern_matcher.match_pattern(pattern)
        
        if matches:
            output = f"Pattern matching found {len(matches)} matches:\n\n"
            
            for i, match in enumerate(matches, 1):
                atom = self._pattern_matcher.atomspace.get_atom(match.atom_id)
                if atom:
                    output += f"{i}. {atom.type}('{atom.name}') [ID: {match.atom_id}]\n"
                    output += f"   Score: {match.score:.3f}\n"
                    
                    if match.bindings:
                        output += f"   Bindings: {match.bindings}\n"
                    output += "\n"
            
            return ToolResult(output=output)
        else:
            return ToolResult(output="No matches found for the pattern")
    
    async def _match_query(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Match a string query pattern."""
        query = kwargs.get("query")
        if not query:
            return ToolResult(error="query parameter required")
        
        matches = self._pattern_matcher.match_query(query)
        
        if matches:
            output = f"Query '{query}' found {len(matches)} matches:\n\n"
            
            for i, match in enumerate(matches, 1):
                atom = self._pattern_matcher.atomspace.get_atom(match.atom_id)
                if atom:
                    output += f"{i}. {atom.type}('{atom.name}') [ID: {match.atom_id}]\n"
                    output += f"   Score: {match.score:.3f}\n"
                    
                    if match.bindings:
                        output += f"   Bindings: {match.bindings}\n"
                    output += "\n"
            
            return ToolResult(output=output)
        else:
            return ToolResult(output=f"No matches found for query '{query}'")
    
    async def _find_similar(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Find atoms similar to a target atom."""
        target_atom_id = kwargs.get("target_atom_id")
        if target_atom_id is None:
            return ToolResult(error="target_atom_id parameter required")
        
        similarity_threshold = kwargs.get("similarity_threshold", 0.7)
        
        target_atom = self._pattern_matcher.atomspace.get_atom(target_atom_id)
        if not target_atom:
            return ToolResult(error=f"Target atom {target_atom_id} not found")
        
        similar_atoms = self._pattern_matcher.find_similar_atoms(
            target_atom_id, similarity_threshold
        )
        
        if similar_atoms:
            output = f"Found {len(similar_atoms)} atoms similar to "
            output += f"{target_atom.type}('{target_atom.name}'):\n\n"
            
            for i, match in enumerate(similar_atoms, 1):
                atom = self._pattern_matcher.atomspace.get_atom(match.atom_id)
                if atom:
                    output += f"{i}. {atom.type}('{atom.name}') [ID: {match.atom_id}]\n"
                    output += f"   Similarity: {match.score:.3f}\n\n"
            
            return ToolResult(output=output)
        else:
            return ToolResult(output=f"No similar atoms found (threshold: {similarity_threshold})")
    
    async def _find_connected(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Find atoms connected through links."""
        target_atom_id = kwargs.get("target_atom_id")
        if target_atom_id is None:
            return ToolResult(error="target_atom_id parameter required")
        
        max_depth = kwargs.get("max_depth", 3)
        connection_types_str = kwargs.get("connection_types")
        
        connection_types = None
        if connection_types_str:
            try:
                connection_types = json.loads(connection_types_str)
            except json.JSONDecodeError as e:
                return ToolResult(error=f"Invalid connection_types JSON: {e}")
        
        target_atom = self._pattern_matcher.atomspace.get_atom(target_atom_id)
        if not target_atom:
            return ToolResult(error=f"Target atom {target_atom_id} not found")
        
        connected_atoms = self._pattern_matcher.find_connected_atoms(
            target_atom_id, max_depth, connection_types
        )
        
        if connected_atoms:
            output = f"Found {len(connected_atoms)} atoms connected to "
            output += f"{target_atom.type}('{target_atom.name}'):\n\n"
            
            for i, match in enumerate(connected_atoms, 1):
                atom = self._pattern_matcher.atomspace.get_atom(match.atom_id)
                if atom:
                    output += f"{i}. {atom.type}('{atom.name}') [ID: {match.atom_id}]\n"
                    output += f"   Distance Score: {match.score:.3f}\n"
                    
                    depth = match.bindings.get("depth")
                    if depth:
                        output += f"   Depth: {depth}\n"
                    output += "\n"
            
            return ToolResult(output=output)
        else:
            return ToolResult(output=f"No connected atoms found within depth {max_depth}")
    
    async def _create_variable(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Create a pattern matching variable."""
        variable_name = kwargs.get("variable_name")
        if not variable_name:
            return ToolResult(error="variable_name parameter required")
        
        type_constraint = kwargs.get("type_constraint")
        value_constraint = kwargs.get("value_constraint")
        
        variable = self._pattern_matcher.create_variable(
            variable_name, type_constraint, value_constraint
        )
        
        output = f"Created pattern variable: ${variable.name}\n"
        if variable.type_constraint:
            output += f"Type constraint: {variable.type_constraint}\n"
        if variable.value_constraint:
            output += f"Value constraint: {variable.value_constraint}\n"
        
        # Return variable as JSON for use in other operations
        variable_json = {
            "name": variable.name,
            "type_constraint": variable.type_constraint,
            "value_constraint": variable.value_constraint
        }
        
        output += f"\nVariable JSON: {json.dumps(variable_json)}"
        
        return ToolResult(output=output)
    
    async def _explain_match(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Explain how a match was found."""
        match_result_str = kwargs.get("match_result")
        if not match_result_str:
            return ToolResult(error="match_result parameter required")
        
        try:
            match_data = json.loads(match_result_str)
            # Create a mock MatchResult for explanation
            from app.opencog.pattern_matcher import MatchResult
            match_result = MatchResult(
                atom_id=match_data["atom_id"],
                bindings=match_data.get("bindings", {}),
                score=match_data.get("score", 1.0)
            )
        except (json.JSONDecodeError, KeyError) as e:
            return ToolResult(error=f"Invalid match_result format: {e}")
        
        explanation = self._pattern_matcher.explain_match(match_result)
        
        if "error" in explanation:
            return ToolResult(error=explanation["error"])
        
        output = "Match Explanation:\n\n"
        output += f"Atom: {explanation['atom_type']}('{explanation['atom_name']}')\n"
        output += f"ID: {explanation['atom_id']}\n"
        output += f"Match Score: {explanation['match_score']:.3f}\n"
        
        if explanation['variable_bindings']:
            output += f"Variable Bindings: {explanation['variable_bindings']}\n"
        
        output += f"\nExplanation: {explanation['explanation']}"
        
        return ToolResult(output=output)
    
    def _dict_to_pattern(self, pattern_dict: Dict[str, Any]):
        """Convert a dictionary to a Pattern object."""
        try:
            atom_type = pattern_dict.get("type")
            name = pattern_dict.get("name")
            outgoing = pattern_dict.get("outgoing")
            
            # Handle variables in name
            if isinstance(name, dict) and name.get("variable"):
                var_data = name["variable"]
                name = self._pattern_matcher.create_variable(
                    var_data["name"],
                    var_data.get("type_constraint"),
                    var_data.get("value_constraint")
                )
            
            # Handle variables in outgoing
            if outgoing:
                processed_outgoing = []
                for item in outgoing:
                    if isinstance(item, dict):
                        if item.get("variable"):
                            var_data = item["variable"]
                            var = self._pattern_matcher.create_variable(
                                var_data["name"],
                                var_data.get("type_constraint"),
                                var_data.get("value_constraint")
                            )
                            processed_outgoing.append(var)
                        else:
                            # Recursive pattern
                            sub_pattern = self._dict_to_pattern(item)
                            if sub_pattern:
                                processed_outgoing.append(sub_pattern)
                    else:
                        processed_outgoing.append(item)
                outgoing = processed_outgoing
            
            return self._pattern_matcher.create_pattern(atom_type, name, outgoing)
            
        except Exception as e:
            logger.error(f"Error converting dict to pattern: {e}")
            return None