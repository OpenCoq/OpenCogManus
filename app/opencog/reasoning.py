"""
Reasoning engine for OpenCog integration with OpenManus.

Provides symbolic reasoning capabilities including forward chaining,
backward chaining, and probabilistic logic networks (PLN) style reasoning.
"""

import math
from typing import Dict, List, Optional, Set, Tuple, Any
from pydantic import BaseModel, Field
from app.logger import logger
from app.opencog.atomspace import AtomSpaceManager, Atom


class Rule(BaseModel):
    """Represents a reasoning rule with premises and conclusions."""
    
    name: str = Field(..., description="Rule name")
    premises: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="List of premise patterns"
    )
    conclusion: Dict[str, Any] = Field(..., description="Conclusion pattern")
    confidence: float = Field(default=1.0, description="Rule confidence")
    
    class Config:
        arbitrary_types_allowed = True


class InferenceResult(BaseModel):
    """Result of an inference operation."""
    
    atom_id: int = Field(..., description="ID of inferred atom")
    rule_name: str = Field(..., description="Name of rule used")
    premises: List[int] = Field(default_factory=list, description="Premise atom IDs")
    confidence: float = Field(..., description="Confidence in inference")
    
    class Config:
        arbitrary_types_allowed = True


class ReasoningEngine(BaseModel):
    """
    Symbolic reasoning engine optimized for OpenManus agents.
    
    Provides forward chaining, backward chaining, and PLN-style probabilistic
    reasoning capabilities integrated with the AtomSpace.
    """
    
    atomspace: AtomSpaceManager = Field(default_factory=AtomSpaceManager)
    rules: List[Rule] = Field(default_factory=list)
    max_iterations: int = Field(default=100, description="Max inference iterations")
    min_confidence: float = Field(default=0.1, description="Minimum confidence threshold")
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_rule(self, name: str, premises: List[Dict[str, Any]], 
                 conclusion: Dict[str, Any], confidence: float = 1.0):
        """Add a reasoning rule to the engine."""
        rule = Rule(
            name=name,
            premises=premises,
            conclusion=conclusion,
            confidence=confidence
        )
        self.rules.append(rule)
        logger.debug(f"Added reasoning rule: {name}")
    
    def add_default_rules(self):
        """Add common reasoning rules to the engine."""
        
        # Inheritance transitivity: If A inherits B and B inherits C, then A inherits C
        self.add_rule(
            "inheritance_transitivity",
            [
                {"type": "InheritanceLink", "outgoing": ["$A", "$B"]},
                {"type": "InheritanceLink", "outgoing": ["$B", "$C"]}
            ],
            {"type": "InheritanceLink", "outgoing": ["$A", "$C"]},
            confidence=0.9
        )
        
        # Deduction: If A implies B and A is true, then B is true
        self.add_rule(
            "deduction",
            [
                {"type": "ImplicationLink", "outgoing": ["$A", "$B"]},
                {"type": "EvaluationLink", "outgoing": ["$A"]}
            ],
            {"type": "EvaluationLink", "outgoing": ["$B"]},
            confidence=0.8
        )
        
        # Similarity symmetry: If A is similar to B, then B is similar to A
        self.add_rule(
            "similarity_symmetry",
            [{"type": "SimilarityLink", "outgoing": ["$A", "$B"]}],
            {"type": "SimilarityLink", "outgoing": ["$B", "$A"]},
            confidence=1.0
        )
        
        logger.info("Added default reasoning rules")
    
    def forward_chain(self, max_inferences: int = 10) -> List[InferenceResult]:
        """
        Perform forward chaining inference.
        
        Args:
            max_inferences: Maximum number of new inferences to make
            
        Returns:
            List of inference results
        """
        inferences = []
        iteration = 0
        
        while len(inferences) < max_inferences and iteration < self.max_iterations:
            iteration += 1
            new_inferences = []
            
            for rule in self.rules:
                rule_inferences = self._apply_rule_forward(rule)
                new_inferences.extend(rule_inferences)
            
            if not new_inferences:
                break  # No new inferences possible
            
            inferences.extend(new_inferences)
            
            if len(inferences) >= max_inferences:
                inferences = inferences[:max_inferences]
                break
        
        logger.info(f"Forward chaining completed: {len(inferences)} inferences in {iteration} iterations")
        return inferences
    
    def backward_chain(self, goal_pattern: Dict[str, Any], max_depth: int = 5) -> List[InferenceResult]:
        """
        Perform backward chaining to prove a goal.
        
        Args:
            goal_pattern: Pattern to prove
            max_depth: Maximum search depth
            
        Returns:
            List of inference results that support the goal
        """
        return self._backward_chain_recursive(goal_pattern, max_depth, set())
    
    def _backward_chain_recursive(self, goal: Dict[str, Any], depth: int, 
                                 visited: Set[str]) -> List[InferenceResult]:
        """Recursive backward chaining implementation."""
        if depth <= 0:
            return []
        
        goal_str = str(goal)
        if goal_str in visited:
            return []  # Avoid cycles
        
        visited.add(goal_str)
        results = []
        
        # Check if goal already exists in atomspace
        if self._pattern_exists(goal):
            return []  # Goal already proven
        
        # Try to find rules that conclude the goal
        for rule in self.rules:
            if self._pattern_matches(rule.conclusion, goal):
                # Try to prove all premises
                premise_results = []
                all_premises_proven = True
                
                for premise in rule.premises:
                    premise_inferences = self._backward_chain_recursive(
                        premise, depth - 1, visited.copy()
                    )
                    if not premise_inferences and not self._pattern_exists(premise):
                        all_premises_proven = False
                        break
                    premise_results.extend(premise_inferences)
                
                if all_premises_proven:
                    # Apply the rule
                    inference = self._create_inference_from_rule(rule, premise_results)
                    if inference:
                        results.append(inference)
        
        return results
    
    def _apply_rule_forward(self, rule: Rule) -> List[InferenceResult]:
        """Apply a rule in forward chaining mode."""
        inferences = []
        
        # Find all possible variable bindings for the premises
        bindings_list = self._find_variable_bindings(rule.premises)
        
        for bindings in bindings_list:
            # Check if conclusion would be new
            instantiated_conclusion = self._instantiate_pattern(rule.conclusion, bindings)
            
            if not self._pattern_exists(instantiated_conclusion):
                # Create new atom from conclusion
                atom_id = self._create_atom_from_pattern(instantiated_conclusion)
                
                if atom_id:
                    # Calculate confidence based on premises
                    premise_ids = [
                        self._find_atom_from_pattern(self._instantiate_pattern(p, bindings))
                        for p in rule.premises
                    ]
                    premise_ids = [pid for pid in premise_ids if pid is not None]
                    
                    confidence = self._calculate_inference_confidence(
                        rule.confidence, premise_ids
                    )
                    
                    if confidence >= self.min_confidence:
                        inference = InferenceResult(
                            atom_id=atom_id,
                            rule_name=rule.name,
                            premises=premise_ids,
                            confidence=confidence
                        )
                        inferences.append(inference)
        
        return inferences
    
    def _find_variable_bindings(self, premises: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find all possible variable bindings for a set of premises."""
        # Simplified implementation - extend for more complex patterns
        if not premises:
            return [{}]
        
        # For now, return empty list for complex pattern matching
        # In a full implementation, this would use sophisticated pattern matching
        return []
    
    def _pattern_matches(self, pattern1: Dict[str, Any], pattern2: Dict[str, Any]) -> bool:
        """Check if two patterns match (considering variables)."""
        # Simplified pattern matching
        if pattern1.get("type") != pattern2.get("type"):
            return False
        
        # For now, just check type - extend for full pattern matching
        return True
    
    def _pattern_exists(self, pattern: Dict[str, Any]) -> bool:
        """Check if a pattern exists in the atomspace."""
        atom_type = pattern.get("type")
        if not atom_type:
            return False
        
        candidates = self.atomspace.find_atoms_by_type(atom_type)
        
        # Simplified existence check
        for atom_id in candidates:
            atom = self.atomspace.get_atom(atom_id)
            if atom and self._atom_matches_pattern(atom, pattern):
                return True
        
        return False
    
    def _atom_matches_pattern(self, atom: Atom, pattern: Dict[str, Any]) -> bool:
        """Check if an atom matches a pattern."""
        if atom.type != pattern.get("type"):
            return False
        
        pattern_name = pattern.get("name")
        if pattern_name and not pattern_name.startswith("$") and atom.name != pattern_name:
            return False
        
        # Could extend for outgoing pattern matching
        return True
    
    def _instantiate_pattern(self, pattern: Dict[str, Any], bindings: Dict[str, Any]) -> Dict[str, Any]:
        """Instantiate a pattern with variable bindings."""
        instantiated = pattern.copy()
        
        # Replace variables in name
        if "name" in instantiated and isinstance(instantiated["name"], str):
            for var, value in bindings.items():
                if instantiated["name"] == var:
                    instantiated["name"] = str(value)
        
        # Replace variables in outgoing
        if "outgoing" in instantiated and isinstance(instantiated["outgoing"], list):
            new_outgoing = []
            for item in instantiated["outgoing"]:
                if isinstance(item, str) and item in bindings:
                    new_outgoing.append(bindings[item])
                else:
                    new_outgoing.append(item)
            instantiated["outgoing"] = new_outgoing
        
        return instantiated
    
    def _create_atom_from_pattern(self, pattern: Dict[str, Any]) -> Optional[int]:
        """Create an atom in the atomspace from a pattern."""
        atom_type = pattern.get("type")
        name = pattern.get("name", "")
        outgoing = pattern.get("outgoing", [])
        
        if atom_type:
            return self.atomspace.add_atom(atom_type, name, outgoing=outgoing)
        
        return None
    
    def _find_atom_from_pattern(self, pattern: Dict[str, Any]) -> Optional[int]:
        """Find an atom ID that matches a pattern."""
        atom_type = pattern.get("type")
        if not atom_type:
            return None
        
        candidates = self.atomspace.find_atoms_by_type(atom_type)
        for atom_id in candidates:
            atom = self.atomspace.get_atom(atom_id)
            if atom and self._atom_matches_pattern(atom, pattern):
                return atom_id
        
        return None
    
    def _calculate_inference_confidence(self, rule_confidence: float, 
                                      premise_ids: List[int]) -> float:
        """Calculate confidence for an inference based on premises and rule."""
        if not premise_ids:
            return rule_confidence
        
        # Get premise confidences
        premise_confidences = []
        for atom_id in premise_ids:
            atom = self.atomspace.get_atom(atom_id)
            if atom and atom.truth_value:
                confidence = atom.truth_value.get("confidence", 1.0)
                strength = atom.truth_value.get("strength", 1.0)
                premise_confidences.append(confidence * strength)
            else:
                premise_confidences.append(1.0)
        
        # Simple confidence calculation - geometric mean of premises * rule confidence
        if premise_confidences:
            premise_conf = math.pow(
                math.prod(premise_confidences), 
                1.0 / len(premise_confidences)
            )
            return rule_confidence * premise_conf
        
        return rule_confidence
    
    def _create_inference_from_rule(self, rule: Rule, 
                                   premise_results: List[InferenceResult]) -> Optional[InferenceResult]:
        """Create an inference result from applying a rule."""
        # Simplified implementation
        return None
    
    def query_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """
        Query the knowledge base using natural language.
        
        Args:
            query: Natural language query
            
        Returns:
            List of relevant knowledge items
        """
        results = []
        
        # Simple keyword-based matching
        query_lower = query.lower()
        
        for atom_id, atom in self.atomspace.atoms.items():
            if query_lower in atom.name.lower():
                results.append({
                    "atom_id": atom_id,
                    "type": atom.type,
                    "name": atom.name,
                    "truth_value": atom.truth_value,
                    "relevance": 1.0  # Could implement more sophisticated relevance scoring
                })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        
        return results[:10]  # Return top 10 results
    
    def explain_inference(self, atom_id: int) -> Dict[str, Any]:
        """
        Explain how an atom was inferred.
        
        Args:
            atom_id: ID of atom to explain
            
        Returns:
            Explanation dictionary
        """
        atom = self.atomspace.get_atom(atom_id)
        if not atom:
            return {"error": "Atom not found"}
        
        # For a full implementation, we would track inference chains
        # For now, return basic information
        return {
            "atom_id": atom_id,
            "type": atom.type,
            "name": atom.name,
            "truth_value": atom.truth_value,
            "explanation": "Direct assertion or inference (detailed tracking not implemented)"
        }