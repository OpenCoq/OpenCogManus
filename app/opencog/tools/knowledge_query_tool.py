"""
Knowledge query tool for OpenManus framework.

Provides tool interface for high-level knowledge queries combining reasoning
and pattern matching capabilities.
"""

import json
from typing import Any, Dict, List, Optional
from app.tool.base import BaseTool, ToolResult
from app.logger import logger


class KnowledgeQueryTool(BaseTool):
    """Tool for high-level knowledge queries and insights."""
    
    name: str = "knowledge_query"
    description: str = """
    Perform high-level knowledge queries and analysis. Available operations:
    - query: Query knowledge using natural language
    - analyze_concept: Analyze relationships and properties of a concept
    - find_paths: Find reasoning paths between concepts
    - get_insights: Get AI-driven insights from knowledge base
    - summarize_knowledge: Summarize knowledge about a topic
    - check_consistency: Check for logical inconsistencies
    - get_statistics: Get knowledge base statistics
    """
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": [
                    "query", "analyze_concept", "find_paths", "get_insights", 
                    "summarize_knowledge", "check_consistency", "get_statistics"
                ],
                "description": "Knowledge query operation to perform"
            },
            "query_text": {
                "type": "string",
                "description": "Natural language query or concept name"
            },
            "concept": {
                "type": "string",
                "description": "Concept to analyze"
            },
            "source_concept": {
                "type": "string",
                "description": "Source concept for path finding"
            },
            "target_concept": {
                "type": "string",
                "description": "Target concept for path finding"
            },
            "max_path_length": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Maximum path length for path finding"
            },
            "topic": {
                "type": "string",
                "description": "Topic to summarize knowledge about"
            },
            "insight_type": {
                "type": "string",
                "enum": ["patterns", "gaps", "conflicts", "opportunities"],
                "description": "Type of insights to generate"
            },
            "include_reasoning": {
                "type": "boolean",
                "description": "Include reasoning in results"
            },
            "max_results": {
                "type": "integer",
                "minimum": 1,
                "maximum": 50,
                "description": "Maximum results to return"
            }
        },
        "required": ["operation"]
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        self._cognitive_agent = None
    
    def set_cognitive_agent(self, cognitive_agent):
        """Set the cognitive agent instance to operate on."""
        self._cognitive_agent = cognitive_agent
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute knowledge query operation."""
        if not self._cognitive_agent:
            return ToolResult(error="Cognitive agent not initialized")
        
        operation = kwargs.get("operation")
        
        try:
            if operation == "query":
                return await self._query(kwargs)
            elif operation == "analyze_concept":
                return await self._analyze_concept(kwargs)
            elif operation == "find_paths":
                return await self._find_paths(kwargs)
            elif operation == "get_insights":
                return await self._get_insights(kwargs)
            elif operation == "summarize_knowledge":
                return await self._summarize_knowledge(kwargs)
            elif operation == "check_consistency":
                return await self._check_consistency(kwargs)
            elif operation == "get_statistics":
                return await self._get_statistics(kwargs)
            else:
                return ToolResult(error=f"Unknown operation: {operation}")
                
        except Exception as e:
            logger.error(f"Knowledge query tool error: {e}")
            return ToolResult(error=str(e))
    
    async def _query(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Query knowledge using natural language."""
        query_text = kwargs.get("query_text")
        if not query_text:
            return ToolResult(error="query_text parameter required")
        
        include_reasoning = kwargs.get("include_reasoning", True)
        max_results = kwargs.get("max_results", 10)
        
        # Use cognitive agent's query method
        results = self._cognitive_agent.query_knowledge(query_text)
        
        if results:
            # Limit results
            results = results[:max_results]
            
            output = f"Knowledge query results for '{query_text}':\n\n"
            
            for i, result in enumerate(results, 1):
                output += f"{i}. {result.get('type', 'Unknown')}('{result.get('name', '')}')\n"
                
                # Add truth value info
                truth_value = result.get('truth_value', {})
                if truth_value:
                    strength = truth_value.get('strength', 1.0)
                    confidence = truth_value.get('confidence', 1.0)
                    output += f"   Truth: strength={strength:.3f}, confidence={confidence:.3f}\n"
                
                # Add relevance
                relevance = result.get('relevance', 1.0)
                output += f"   Relevance: {relevance:.3f}\n"
                
                # Add bindings if available
                bindings = result.get('bindings', {})
                if bindings:
                    output += f"   Bindings: {bindings}\n"
                
                # Add reasoning explanation if requested
                if include_reasoning:
                    atom_id = result.get('atom_id')
                    if atom_id:
                        explanation = self._cognitive_agent.explain_reasoning(atom_id)
                        if not explanation.get('error'):
                            exp_text = explanation.get('explanation', '')
                            if len(exp_text) > 100:
                                exp_text = exp_text[:100] + "..."
                            output += f"   Reasoning: {exp_text}\n"
                
                output += "\n"
            
            return ToolResult(output=output)
        else:
            return ToolResult(output=f"No knowledge found for query '{query_text}'")
    
    async def _analyze_concept(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Analyze relationships and properties of a concept."""
        concept = kwargs.get("concept")
        if not concept:
            return ToolResult(error="concept parameter required")
        
        atomspace = self._cognitive_agent.atomspace
        pattern_matcher = self._cognitive_agent.pattern_matcher
        
        # Find the concept atom
        concept_atoms = atomspace.find_atoms_by_name(concept)
        if not concept_atoms:
            return ToolResult(output=f"Concept '{concept}' not found in knowledge base")
        
        concept_id = concept_atoms[0]  # Use first match
        concept_atom = atomspace.get_atom(concept_id)
        
        output = f"Analysis of concept '{concept}':\n\n"
        output += f"Atom ID: {concept_id}\n"
        output += f"Type: {concept_atom.type}\n"
        
        if concept_atom.truth_value:
            tv = concept_atom.truth_value
            output += f"Truth Value: strength={tv.get('strength', 1.0):.3f}, "
            output += f"confidence={tv.get('confidence', 1.0):.3f}\n"
        
        output += "\n"
        
        # Find relationships
        incoming_links = atomspace.get_incoming(concept_id)
        outgoing_links = atomspace.get_outgoing(concept_id)
        
        output += f"Relationships:\n"
        output += f"- Incoming links: {len(incoming_links)}\n"
        output += f"- Outgoing links: {len(outgoing_links)}\n\n"
        
        # Analyze incoming relationships
        if incoming_links:
            output += "Incoming relationships (what relates to this concept):\n"
            for i, link_id in enumerate(incoming_links[:5], 1):  # Show first 5
                link_atom = atomspace.get_atom(link_id)
                if link_atom:
                    output += f"{i}. {link_atom.type}: {link_atom.name}\n"
            if len(incoming_links) > 5:
                output += f"... and {len(incoming_links) - 5} more\n"
            output += "\n"
        
        # Find similar concepts
        similar_atoms = pattern_matcher.find_similar_atoms(concept_id, 0.5)
        if similar_atoms:
            output += "Similar concepts:\n"
            for i, match in enumerate(similar_atoms[:3], 1):  # Show top 3
                similar_atom = atomspace.get_atom(match.atom_id)
                if similar_atom:
                    output += f"{i}. {similar_atom.name} (similarity: {match.score:.3f})\n"
            output += "\n"
        
        # Find connected concepts
        connected_atoms = pattern_matcher.find_connected_atoms(concept_id, 2)
        if connected_atoms:
            output += "Connected concepts (within 2 hops):\n"
            for i, match in enumerate(connected_atoms[:5], 1):  # Show first 5
                connected_atom = atomspace.get_atom(match.atom_id)
                if connected_atom:
                    depth = match.bindings.get("depth", "?")
                    output += f"{i}. {connected_atom.name} (depth: {depth})\n"
            if len(connected_atoms) > 5:
                output += f"... and {len(connected_atoms) - 5} more\n"
        
        return ToolResult(output=output)
    
    async def _find_paths(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Find reasoning paths between concepts."""
        source_concept = kwargs.get("source_concept")
        target_concept = kwargs.get("target_concept")
        
        if not source_concept or not target_concept:
            return ToolResult(error="source_concept and target_concept parameters required")
        
        max_path_length = kwargs.get("max_path_length", 5)
        
        atomspace = self._cognitive_agent.atomspace
        pattern_matcher = self._cognitive_agent.pattern_matcher
        
        # Find concept atoms
        source_atoms = atomspace.find_atoms_by_name(source_concept)
        target_atoms = atomspace.find_atoms_by_name(target_concept)
        
        if not source_atoms:
            return ToolResult(error=f"Source concept '{source_concept}' not found")
        if not target_atoms:
            return ToolResult(error=f"Target concept '{target_concept}' not found")
        
        source_id = source_atoms[0]
        target_id = target_atoms[0]
        
        # Find paths using connected atoms search
        connected_from_source = pattern_matcher.find_connected_atoms(source_id, max_path_length)
        
        # Check if target is reachable
        paths_found = []
        for match in connected_from_source:
            if match.atom_id == target_id:
                paths_found.append(match)
        
        if paths_found:
            output = f"Found {len(paths_found)} path(s) from '{source_concept}' to '{target_concept}':\n\n"
            
            for i, path in enumerate(paths_found, 1):
                depth = path.bindings.get("depth", "?")
                output += f"Path {i}: Length {depth}, Score: {path.score:.3f}\n"
                
                # For detailed path, we would need to implement path reconstruction
                # For now, just show that a path exists
                output += f"  Connection found within {depth} hops\n\n"
        else:
            output = f"No paths found from '{source_concept}' to '{target_concept}' "
            output += f"within {max_path_length} hops"
        
        return ToolResult(output=output)
    
    async def _get_insights(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Get AI-driven insights from knowledge base."""
        insight_type = kwargs.get("insight_type", "patterns")
        
        atomspace = self._cognitive_agent.atomspace
        
        output = f"Knowledge Base Insights ({insight_type}):\n\n"
        
        if insight_type == "patterns":
            # Analyze common patterns
            type_counts = {}
            for atom in atomspace.atoms.values():
                type_counts[atom.type] = type_counts.get(atom.type, 0) + 1
            
            output += "Most common atom types:\n"
            for atom_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                output += f"- {atom_type}: {count} atoms\n"
            output += "\n"
            
            # Find highly connected concepts
            connection_counts = {}
            for atom_id, atom in atomspace.atoms.items():
                if atom.type == "ConceptNode":
                    connections = len(atom.incoming) + len(atom.outgoing)
                    if connections > 0:
                        connection_counts[atom.name] = connections
            
            if connection_counts:
                output += "Most connected concepts:\n"
                for concept, count in sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
                    output += f"- {concept}: {count} connections\n"
        
        elif insight_type == "gaps":
            # Find concepts with few connections (potential knowledge gaps)
            isolated_concepts = []
            for atom_id, atom in atomspace.atoms.items():
                if atom.type == "ConceptNode":
                    connections = len(atom.incoming) + len(atom.outgoing)
                    if connections <= 1:
                        isolated_concepts.append(atom.name)
            
            if isolated_concepts:
                output += f"Potentially under-developed concepts ({len(isolated_concepts)} found):\n"
                for concept in isolated_concepts[:10]:
                    output += f"- {concept}\n"
                if len(isolated_concepts) > 10:
                    output += f"... and {len(isolated_concepts) - 10} more\n"
            else:
                output += "No isolated concepts found - knowledge appears well-connected\n"
        
        elif insight_type == "conflicts":
            # Look for potential conflicts (simplified)
            conflicts = []
            # This would need more sophisticated conflict detection
            output += "Conflict analysis not fully implemented - placeholder\n"
            output += "Would check for contradictory truth values and logical inconsistencies\n"
        
        elif insight_type == "opportunities":
            # Suggest areas for knowledge expansion
            output += "Knowledge expansion opportunities:\n"
            output += "- Add more detailed relationships between existing concepts\n"
            output += "- Develop isolated concepts with more connections\n"
            output += "- Add temporal and causal relationships\n"
        
        return ToolResult(output=output)
    
    async def _summarize_knowledge(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Summarize knowledge about a topic."""
        topic = kwargs.get("topic")
        if not topic:
            return ToolResult(error="topic parameter required")
        
        # Query for topic-related knowledge
        results = self._cognitive_agent.query_knowledge(topic)
        
        if not results:
            return ToolResult(output=f"No knowledge found about topic '{topic}'")
        
        output = f"Knowledge Summary for '{topic}':\n\n"
        
        # Categorize results
        concepts = [r for r in results if r.get('type') == 'ConceptNode']
        predicates = [r for r in results if r.get('type') == 'PredicateNode'] 
        evaluations = [r for r in results if r.get('type') == 'EvaluationLink']
        inheritances = [r for r in results if r.get('type') == 'InheritanceLink']
        
        if concepts:
            output += f"Related Concepts ({len(concepts)}):\n"
            for concept in concepts[:5]:
                output += f"- {concept.get('name', '')}\n"
            if len(concepts) > 5:
                output += f"... and {len(concepts) - 5} more\n"
            output += "\n"
        
        if predicates:
            output += f"Related Predicates ({len(predicates)}):\n"
            for predicate in predicates[:5]:
                output += f"- {predicate.get('name', '')}\n"
            if len(predicates) > 5:
                output += f"... and {len(predicates) - 5} more\n"
            output += "\n"
        
        if evaluations:
            output += f"Facts and Evaluations ({len(evaluations)}):\n"
            for eval_item in evaluations[:3]:
                truth_value = eval_item.get('truth_value', {})
                strength = truth_value.get('strength', 1.0)
                output += f"- Evaluation (strength: {strength:.3f})\n"
            if len(evaluations) > 3:
                output += f"... and {len(evaluations) - 3} more\n"
            output += "\n"
        
        if inheritances:
            output += f"Inheritance Relationships ({len(inheritances)}):\n"
            for inherit in inheritances[:3]:
                output += f"- Inheritance relationship\n"
            if len(inheritances) > 3:
                output += f"... and {len(inheritances) - 3} more\n"
        
        return ToolResult(output=output)
    
    async def _check_consistency(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Check for logical inconsistencies."""
        atomspace = self._cognitive_agent.atomspace
        
        output = "Knowledge Base Consistency Check:\n\n"
        
        # Check for truth value inconsistencies
        inconsistencies = []
        
        # Look for atoms with very low confidence
        low_confidence_atoms = []
        for atom_id, atom in atomspace.atoms.items():
            if atom.truth_value:
                confidence = atom.truth_value.get('confidence', 1.0)
                if confidence < 0.3:
                    low_confidence_atoms.append((atom_id, atom, confidence))
        
        if low_confidence_atoms:
            output += f"Atoms with low confidence ({len(low_confidence_atoms)} found):\n"
            for atom_id, atom, confidence in low_confidence_atoms[:5]:
                output += f"- {atom.type}('{atom.name}') confidence: {confidence:.3f}\n"
            if len(low_confidence_atoms) > 5:
                output += f"... and {len(low_confidence_atoms) - 5} more\n"
            output += "\n"
        
        # Check for contradictory inheritance chains (simplified)
        output += "Inheritance consistency: Analysis not fully implemented\n"
        output += "Would check for cycles and contradictions in inheritance hierarchy\n\n"
        
        # Summary
        if not low_confidence_atoms:
            output += "No major consistency issues detected.\n"
        else:
            output += f"Found {len(low_confidence_atoms)} potential consistency issues.\n"
        
        return ToolResult(output=output)
    
    async def _get_statistics(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Get knowledge base statistics."""
        status = self._cognitive_agent.get_cognitive_status()
        
        output = "Knowledge Base Statistics:\n\n"
        output += f"Total atoms: {status['total_atoms']}\n"
        output += f"AtomSpace size: {status['atomspace_size']}\n\n"
        
        output += "Atom type breakdown:\n"
        output += f"- Concept nodes: {status['concept_nodes']}\n"
        output += f"- Predicate nodes: {status['predicate_nodes']}\n"
        output += f"- Inheritance links: {status['inheritance_links']}\n"
        output += f"- Evaluation links: {status['evaluation_links']}\n\n"
        
        output += "Reasoning system:\n"
        output += f"- Reasoning rules: {status['reasoning_rules']}\n"
        output += f"- Auto reasoning: {status['auto_reasoning']}\n"
        output += f"- Knowledge persistence: {status['knowledge_persistence']}\n"
        
        return ToolResult(output=output)