"""
Cognitive Agent implementation using OpenCog systems for OpenManus.

Extends the ToolCallAgent with symbolic reasoning, knowledge representation,
and advanced pattern matching capabilities from OpenCog.
"""

from typing import Dict, List, Optional, Any
from pydantic import Field
from app.agent.toolcall import ToolCallAgent
from app.logger import logger
from app.opencog.atomspace import AtomSpaceManager
from app.opencog.reasoning import ReasoningEngine
from app.opencog.pattern_matcher import PatternMatcher
from app.tool import ToolCollection
from app.tool.python_execute import PythonExecute
from app.tool.str_replace_editor import StrReplaceEditor
from app.opencog.tools.atomspace_tool import AtomSpaceTool  
from app.opencog.tools.reasoning_tool import ReasoningTool
from app.opencog.tools.pattern_match_tool import PatternMatchTool
from app.opencog.tools.knowledge_query_tool import KnowledgeQueryTool
from app.prompt.opencog.cognitive_agent import COGNITIVE_AGENT_SYSTEM_PROMPT, COGNITIVE_AGENT_NEXT_STEP_PROMPT


class CognitiveAgent(ToolCallAgent):
    """
    Cognitive agent with OpenCog symbolic AI capabilities.
    
    This agent extends the base ToolCallAgent with OpenCog systems including:
    - AtomSpace for knowledge representation
    - Reasoning engine for symbolic inference
    - Pattern matcher for advanced queries
    - Cognitive tools for symbolic manipulation
    """
    
    name: str = "CognitiveAgent"
    description: str = "An advanced agent with symbolic reasoning and knowledge representation capabilities"
    system_prompt: str = COGNITIVE_AGENT_SYSTEM_PROMPT
    next_step_prompt: str = COGNITIVE_AGENT_NEXT_STEP_PROMPT
    
    # OpenCog components
    atomspace: AtomSpaceManager = Field(default_factory=AtomSpaceManager)
    reasoning_engine: ReasoningEngine = Field(default_factory=ReasoningEngine)
    pattern_matcher: PatternMatcher = Field(default_factory=PatternMatcher)
    
    # Configuration
    enable_auto_reasoning: bool = Field(
        default=True, 
        description="Automatically run reasoning after knowledge updates"
    )
    max_reasoning_iterations: int = Field(
        default=5,
        description="Maximum reasoning iterations per step"
    )
    knowledge_persistence: bool = Field(
        default=True,
        description="Persist knowledge between agent runs"
    )
    
    # Add cognitive tools to the tool collection
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            PythonExecute(),
            StrReplaceEditor(),
            AtomSpaceTool(),
            ReasoningTool(),
            PatternMatchTool(),
            KnowledgeQueryTool()
        )
    )
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_cognitive_systems()
        self._setup_tools()
    
    def _initialize_cognitive_systems(self):
        """Initialize and link OpenCog components."""
        # Connect components
        self.reasoning_engine.atomspace = self.atomspace
        self.pattern_matcher.atomspace = self.atomspace
        
        # Add default reasoning rules
        self.reasoning_engine.add_default_rules()
        
        # Initialize with basic knowledge if needed
        self._add_default_knowledge()
        
        logger.info("OpenCog Cognitive Agent initialized with symbolic AI capabilities")
        
        logger.info("Cognitive agent systems initialized")
    
    def _setup_tools(self):
        """Setup and configure OpenCog tools."""
        # Get tools from collection
        atomspace_tool = None
        reasoning_tool = None 
        pattern_match_tool = None
        knowledge_query_tool = None
        
        for tool in self.available_tools.tools:
            if isinstance(tool, AtomSpaceTool):
                atomspace_tool = tool
            elif isinstance(tool, ReasoningTool):
                reasoning_tool = tool
            elif isinstance(tool, PatternMatchTool):
                pattern_match_tool = tool
            elif isinstance(tool, KnowledgeQueryTool):
                knowledge_query_tool = tool
        
        # Connect tools to cognitive systems
        if atomspace_tool:
            atomspace_tool.set_atomspace(self.atomspace)
        if reasoning_tool:
            reasoning_tool.set_reasoning_engine(self.reasoning_engine)
        if pattern_match_tool:
            pattern_match_tool.set_pattern_matcher(self.pattern_matcher)
        if knowledge_query_tool:
            knowledge_query_tool.set_cognitive_agent(self)
        
        logger.debug("OpenCog tools configured")
    
    def _add_default_knowledge(self):
        """Add foundational knowledge to the AtomSpace."""
        # Add basic concepts
        self.atomspace.add_concept("Agent")
        self.atomspace.add_concept("Human")
        self.atomspace.add_concept("Task")
        self.atomspace.add_concept("Knowledge")
        self.atomspace.add_concept("Goal")
        
        # Add basic relationships
        self.atomspace.add_inheritance("CognitiveAgent", "Agent")
        self.atomspace.add_predicate("can_reason")
        self.atomspace.add_predicate("has_knowledge")
        self.atomspace.add_predicate("helps")
        
        # Add evaluations
        self.atomspace.add_evaluation("can_reason", "CognitiveAgent")
        self.atomspace.add_evaluation("has_knowledge", "CognitiveAgent", "Knowledge")
        self.atomspace.add_evaluation("helps", "CognitiveAgent", "Human")
        
        logger.debug("Added default knowledge to AtomSpace")
    
    async def think(self) -> bool:
        """Enhanced thinking process with symbolic reasoning."""
        # First do standard thinking
        should_continue = await super().think()
        
        if self.enable_auto_reasoning and should_continue:
            # Run reasoning on current knowledge
            await self._perform_cognitive_reasoning()
            
            # Extract insights from reasoning
            insights = self._extract_reasoning_insights()
            if insights:
                # Add insights to next step context
                self.next_step_prompt = f"{self.next_step_prompt}\n\nCognitive insights: {insights}"
        
        return should_continue
    
    async def _perform_cognitive_reasoning(self):
        """Perform symbolic reasoning on current knowledge."""
        try:
            # Run forward chaining
            inferences = self.reasoning_engine.forward_chain(
                max_inferences=self.max_reasoning_iterations
            )
            
            if inferences:
                logger.info(f"Generated {len(inferences)} new inferences")
                
                # Update AtomSpace with new inferences
                for inference in inferences:
                    atom = self.atomspace.get_atom(inference.atom_id)
                    if atom:
                        # Update truth value with inference confidence
                        self.atomspace.update_truth_value(
                            inference.atom_id,
                            {
                                "strength": atom.truth_value.get("strength", 1.0),
                                "confidence": inference.confidence
                            }
                        )
            
        except Exception as e:
            logger.error(f"Error during cognitive reasoning: {e}")
    
    def _extract_reasoning_insights(self) -> Optional[str]:
        """Extract actionable insights from recent reasoning."""
        insights = []
        
        # Look for high-confidence inferences about current goals
        goal_atoms = self.atomspace.find_atoms_by_name("Goal")
        for goal_id in goal_atoms:
            incoming = self.atomspace.get_incoming(goal_id)
            for link_id in incoming:
                link_atom = self.atomspace.get_atom(link_id)
                if link_atom and link_atom.truth_value:
                    confidence = link_atom.truth_value.get("confidence", 0.0)
                    if confidence > 0.8:  # High confidence threshold
                        insights.append(f"High confidence in: {link_atom.type} involving goals")
        
        return "; ".join(insights) if insights else None
    
    def add_knowledge(self, knowledge_type: str, subject: str, 
                     predicate: Optional[str] = None, object_: Optional[str] = None,
                     truth_value: Optional[Dict[str, float]] = None):
        """
        Add knowledge to the cognitive agent's knowledge base.
        
        Args:
            knowledge_type: Type of knowledge ('concept', 'relation', 'fact')
            subject: Subject of the knowledge
            predicate: Predicate (for relations and facts)
            object_: Object (for relations and facts)
            truth_value: Optional truth value
        """
        try:
            if knowledge_type == "concept":
                atom_id = self.atomspace.add_concept(subject, truth_value)
                logger.debug(f"Added concept: {subject}")
                
            elif knowledge_type == "relation":
                if predicate and object_:
                    atom_id = self.atomspace.add_inheritance(subject, object_, truth_value)
                    logger.debug(f"Added relation: {subject} -> {object_}")
                    
            elif knowledge_type == "fact":
                if predicate:
                    if object_:
                        atom_id = self.atomspace.add_evaluation(predicate, subject, object_, truth_value)
                    else:
                        atom_id = self.atomspace.add_evaluation(predicate, subject, truth_value)
                    logger.debug(f"Added fact: {predicate}({subject}, {object_ or ''})")
            
            # Trigger reasoning if enabled
            if self.enable_auto_reasoning:
                # Run a limited reasoning cycle
                inferences = self.reasoning_engine.forward_chain(max_inferences=3)
                if inferences:
                    logger.debug(f"Knowledge addition triggered {len(inferences)} inferences")
                    
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
    
    def query_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """
        Query the knowledge base.
        
        Args:
            query: Natural language or pattern query
            
        Returns:
            List of relevant knowledge items
        """
        try:
            # Try reasoning-based query first
            reasoning_results = self.reasoning_engine.query_knowledge(query)
            
            # Try pattern matching
            pattern_results = self.pattern_matcher.match_query(query)
            
            # Combine and deduplicate results
            all_results = reasoning_results.copy()
            
            for match in pattern_results:
                atom = self.atomspace.get_atom(match.atom_id)
                if atom:
                    result_item = {
                        "atom_id": match.atom_id,
                        "type": atom.type,
                        "name": atom.name,
                        "truth_value": atom.truth_value,
                        "relevance": match.score,
                        "bindings": match.bindings
                    }
                    
                    # Check for duplicates
                    if not any(r.get("atom_id") == match.atom_id for r in all_results):
                        all_results.append(result_item)
            
            # Sort by relevance
            all_results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
            
            return all_results[:20]  # Return top 20 results
            
        except Exception as e:
            logger.error(f"Error querying knowledge: {e}")
            return []
    
    def explain_reasoning(self, atom_id: int) -> Dict[str, Any]:
        """
        Explain how a piece of knowledge was derived.
        
        Args:
            atom_id: ID of atom to explain
            
        Returns:
            Explanation of reasoning chain
        """
        try:
            return self.reasoning_engine.explain_inference(atom_id)
        except Exception as e:
            logger.error(f"Error explaining reasoning: {e}")
            return {"error": str(e)}
    
    def get_cognitive_status(self) -> Dict[str, Any]:
        """Get status of cognitive systems."""
        return {
            "atomspace_size": self.atomspace.size(),
            "total_atoms": len(self.atomspace.atoms),
            "concept_nodes": len(self.atomspace.find_atoms_by_type("ConceptNode")),
            "predicate_nodes": len(self.atomspace.find_atoms_by_type("PredicateNode")),
            "inheritance_links": len(self.atomspace.find_atoms_by_type("InheritanceLink")),
            "evaluation_links": len(self.atomspace.find_atoms_by_type("EvaluationLink")),
            "reasoning_rules": len(self.reasoning_engine.rules),
            "auto_reasoning": self.enable_auto_reasoning,
            "knowledge_persistence": self.knowledge_persistence
        }
    
    def save_knowledge(self, filepath: str) -> bool:
        """
        Save current knowledge to file.
        
        Args:
            filepath: Path to save knowledge
            
        Returns:
            Success status
        """
        try:
            import json
            knowledge_data = self.atomspace.export_to_dict()
            
            with open(filepath, 'w') as f:
                json.dump(knowledge_data, f, indent=2)
            
            logger.info(f"Knowledge saved to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving knowledge: {e}")
            return False
    
    def load_knowledge(self, filepath: str) -> bool:
        """
        Load knowledge from file.
        
        Args:
            filepath: Path to load knowledge from
            
        Returns:
            Success status
        """
        try:
            import json
            
            with open(filepath, 'r') as f:
                knowledge_data = json.load(f)
            
            self.atomspace.import_from_dict(knowledge_data)
            
            # Reinitialize connected systems
            self.reasoning_engine.atomspace = self.atomspace
            self.pattern_matcher.atomspace = self.atomspace
            
            logger.info(f"Knowledge loaded from {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading knowledge: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup cognitive agent with optional knowledge persistence."""
        if self.knowledge_persistence:
            # Save knowledge to persistent storage
            try:
                self.save_knowledge("cognitive_agent_knowledge.json")
            except Exception as e:
                logger.warning(f"Could not persist knowledge: {e}")
        
        # Clear AtomSpace
        self.atomspace.clear()
        
        # Call parent cleanup
        await super().cleanup()
        
        logger.info("Cognitive agent cleanup completed")
    
    def validate_knowledge_consistency(self) -> Dict[str, Any]:
        """
        Validate consistency of current knowledge base.
        
        Returns:
            Dictionary with validation results and any inconsistencies found
        """
        try:
            validation_results = {
                "consistent": True,
                "issues": [],
                "statistics": {},
                "recommendations": []
            }
            
            # Basic statistics
            stats = self.get_cognitive_status()
            validation_results["statistics"] = stats
            
            # Check for circular inheritance
            inheritance_links = self.atomspace.find_atoms_by_type("InheritanceLink")
            circular_chains = []
            
            for link_id in inheritance_links:
                link_atom = self.atomspace.get_atom(link_id)
                if link_atom and len(link_atom.outgoing) == 2:
                    child_id, parent_id = link_atom.outgoing
                    
                    # Simple cycle detection (could be enhanced)
                    if self._has_inheritance_path(parent_id, child_id):
                        child_atom = self.atomspace.get_atom(child_id)
                        parent_atom = self.atomspace.get_atom(parent_id)
                        if child_atom and parent_atom:
                            circular_chains.append(f"{child_atom.name} -> {parent_atom.name}")
            
            if circular_chains:
                validation_results["consistent"] = False
                validation_results["issues"].append({
                    "type": "circular_inheritance",
                    "description": "Circular inheritance detected",
                    "items": circular_chains
                })
            
            # Check for conflicting truth values
            concept_nodes = self.atomspace.find_atoms_by_type("ConceptNode")
            low_confidence_items = []
            
            for atom_id in concept_nodes:
                atom = self.atomspace.get_atom(atom_id)
                if atom and atom.truth_value:
                    confidence = atom.truth_value.get("confidence", 1.0)
                    if confidence < 0.3:
                        low_confidence_items.append(f"{atom.name} (conf: {confidence:.2f})")
            
            if low_confidence_items:
                validation_results["recommendations"].append({
                    "type": "low_confidence",
                    "description": "Consider reviewing low-confidence items",
                    "items": low_confidence_items[:5]  # Show first 5
                })
            
            # Performance recommendations
            if stats["total_atoms"] > 1000:
                validation_results["recommendations"].append({
                    "type": "performance", 
                    "description": "Large knowledge base - consider periodic cleanup",
                    "suggestion": "Use atomspace clear or export/import for optimization"
                })
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating knowledge consistency: {e}")
            return {
                "consistent": False,
                "error": str(e),
                "issues": [{"type": "validation_error", "description": str(e)}]
            }
    
    def _has_inheritance_path(self, start_id: int, target_id: int, visited: Optional[set] = None) -> bool:
        """Check if there's an inheritance path from start to target (for cycle detection)."""
        if visited is None:
            visited = set()
        
        if start_id in visited:
            return False
        
        if start_id == target_id:
            return True
        
        visited.add(start_id)
        
        # Find inheritance links where start_id is the child
        incoming_links = self.atomspace.get_incoming(start_id)
        for link_id in incoming_links:
            link_atom = self.atomspace.get_atom(link_id)
            if (link_atom and link_atom.type == "InheritanceLink" and 
                len(link_atom.outgoing) == 2 and link_atom.outgoing[0] == start_id):
                parent_id = link_atom.outgoing[1]
                if self._has_inheritance_path(parent_id, target_id, visited.copy()):
                    return True
        
        return False
    
    def generate_knowledge_insights(self) -> Dict[str, Any]:
        """
        Generate insights about the current knowledge base.
        
        Returns:
            Dictionary with various insights and suggestions
        """
        try:
            insights = {
                "knowledge_graph_analysis": {},
                "concept_rankings": [],
                "knowledge_gaps": [],
                "learning_suggestions": []
            }
            
            # Analyze knowledge graph structure
            concepts = self.atomspace.find_atoms_by_type("ConceptNode")
            predicates = self.atomspace.find_atoms_by_type("PredicateNode")
            
            # Find most connected concepts
            concept_connections = {}
            for concept_id in concepts:
                concept_atom = self.atomspace.get_atom(concept_id)
                if concept_atom:
                    incoming = len(self.atomspace.get_incoming(concept_id))
                    outgoing = len(concept_atom.outgoing)
                    total_connections = incoming + outgoing
                    concept_connections[concept_atom.name] = total_connections
            
            # Sort by connectivity
            sorted_concepts = sorted(concept_connections.items(), key=lambda x: x[1], reverse=True)
            insights["concept_rankings"] = [
                {"concept": name, "connections": count} 
                for name, count in sorted_concepts[:10]
            ]
            
            # Knowledge base maturity assessment
            total_atoms = len(self.atomspace.atoms)
            relationship_ratio = len(self.atomspace.find_atoms_by_type("InheritanceLink")) / max(len(concepts), 1)
            
            if total_atoms < 10:
                maturity = "beginner"
            elif total_atoms < 50:
                maturity = "developing"  
            elif total_atoms < 200:
                maturity = "intermediate"
            else:
                maturity = "advanced"
            
            insights["knowledge_graph_analysis"]["maturity"] = {
                "level": maturity,
                "total_atoms": total_atoms,
                "relationship_ratio": relationship_ratio
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating knowledge insights: {e}")
            return {"error": str(e)}