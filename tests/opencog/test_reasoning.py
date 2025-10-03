"""
Tests for Reasoning Engine implementation.
"""

import pytest
from app.opencog.atomspace import AtomSpaceManager
from app.opencog.reasoning import ReasoningEngine, Rule, InferenceResult


class TestReasoningEngine:
    """Test cases for ReasoningEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.atomspace = AtomSpaceManager()
        self.reasoning_engine = ReasoningEngine(atomspace=self.atomspace)
    
    def test_initialization(self):
        """Test reasoning engine initialization."""
        assert self.reasoning_engine.atomspace == self.atomspace
        assert len(self.reasoning_engine.rules) == 0
        assert self.reasoning_engine.max_iterations == 100
        assert self.reasoning_engine.min_confidence == 0.1
    
    def test_add_rule(self):
        """Test adding a reasoning rule."""
        premises = [{"type": "ConceptNode", "name": "$A"}]
        conclusion = {"type": "ConceptNode", "name": "$B"}
        
        self.reasoning_engine.add_rule("test_rule", premises, conclusion, 0.8)
        
        assert len(self.reasoning_engine.rules) == 1
        rule = self.reasoning_engine.rules[0]
        assert rule.name == "test_rule"
        assert rule.premises == premises
        assert rule.conclusion == conclusion
        assert rule.confidence == 0.8
    
    def test_add_default_rules(self):
        """Test adding default reasoning rules."""
        self.reasoning_engine.add_default_rules()
        
        assert len(self.reasoning_engine.rules) > 0
        
        # Check for specific default rules
        rule_names = [rule.name for rule in self.reasoning_engine.rules]
        assert "inheritance_transitivity" in rule_names
        assert "deduction" in rule_names
        assert "similarity_symmetry" in rule_names
    
    def test_forward_chain_no_rules(self):
        """Test forward chaining with no rules."""
        # Add some atoms
        self.atomspace.add_concept("AI")
        self.atomspace.add_concept("Technology")
        
        inferences = self.reasoning_engine.forward_chain(5)
        
        # Should return empty list when no rules are available
        assert len(inferences) == 0
    
    def test_query_knowledge(self):
        """Test querying knowledge base."""
        # Add some knowledge
        self.atomspace.add_concept("artificial intelligence")
        self.atomspace.add_concept("machine learning")
        self.atomspace.add_predicate("learns")
        
        # Query for AI-related knowledge
        results = self.reasoning_engine.query_knowledge("artificial")
        
        assert len(results) > 0
        assert any("artificial intelligence" in str(result) for result in results)
    
    def test_query_knowledge_no_matches(self):
        """Test querying with no matches."""
        self.atomspace.add_concept("AI")
        
        results = self.reasoning_engine.query_knowledge("nonexistent")
        
        assert len(results) == 0
    
    def test_explain_inference_existing_atom(self):
        """Test explaining an existing atom."""
        atom_id = self.atomspace.add_concept("AI")
        
        explanation = self.reasoning_engine.explain_inference(atom_id)
        
        assert "atom_id" in explanation
        assert explanation["atom_id"] == atom_id
        assert "type" in explanation
        assert "name" in explanation
    
    def test_explain_inference_nonexistent_atom(self):
        """Test explaining a nonexistent atom."""
        explanation = self.reasoning_engine.explain_inference(999)
        
        assert "error" in explanation
        assert explanation["error"] == "Atom not found"
    
    def test_pattern_exists(self):
        """Test checking if pattern exists in atomspace."""
        self.atomspace.add_concept("AI")
        
        # Pattern that should exist
        pattern = {"type": "ConceptNode", "name": "AI"}
        assert self.reasoning_engine._pattern_exists(pattern)
        
        # Pattern that shouldn't exist
        pattern = {"type": "ConceptNode", "name": "Nonexistent"}
        assert not self.reasoning_engine._pattern_exists(pattern)
    
    def test_atom_matches_pattern(self):
        """Test atom pattern matching."""
        atom_id = self.atomspace.add_concept("AI")
        atom = self.atomspace.get_atom(atom_id)
        
        # Exact match
        pattern = {"type": "ConceptNode", "name": "AI"}
        assert self.reasoning_engine._atom_matches_pattern(atom, pattern)
        
        # Type mismatch
        pattern = {"type": "PredicateNode", "name": "AI"}
        assert not self.reasoning_engine._atom_matches_pattern(atom, pattern)
        
        # Name mismatch
        pattern = {"type": "ConceptNode", "name": "ML"}
        assert not self.reasoning_engine._atom_matches_pattern(atom, pattern)
        
        # Variable pattern (should match)
        pattern = {"type": "ConceptNode", "name": "$X"}
        assert self.reasoning_engine._atom_matches_pattern(atom, pattern)
    
    def test_calculate_inference_confidence(self):
        """Test confidence calculation for inferences."""
        # Add atoms with truth values
        ai_id = self.atomspace.add_concept("AI", {"strength": 0.9, "confidence": 0.8})
        tech_id = self.atomspace.add_concept("Technology", {"strength": 0.7, "confidence": 0.9})
        
        # Test confidence calculation
        rule_confidence = 0.8
        premise_ids = [ai_id, tech_id]
        
        confidence = self.reasoning_engine._calculate_inference_confidence(
            rule_confidence, premise_ids
        )
        
        # Should be between 0 and 1, and incorporate both rule and premise confidences
        assert 0 <= confidence <= 1
        assert confidence <= rule_confidence  # Should not exceed rule confidence
    
    def test_instantiate_pattern(self):
        """Test pattern instantiation with variable bindings."""
        pattern = {
            "type": "ConceptNode",
            "name": "$X",
            "outgoing": ["$A", "$B"]
        }
        
        bindings = {
            "$X": "AI",
            "$A": 1,
            "$B": 2
        }
        
        instantiated = self.reasoning_engine._instantiate_pattern(pattern, bindings)
        
        assert instantiated["type"] == "ConceptNode"
        assert instantiated["name"] == "AI"
        assert instantiated["outgoing"] == [1, 2]


class TestRule:
    """Test cases for Rule class."""
    
    def test_rule_creation(self):
        """Test creating a Rule."""
        premises = [
            {"type": "ConceptNode", "name": "$A"},
            {"type": "ConceptNode", "name": "$B"}
        ]
        conclusion = {"type": "InheritanceLink", "outgoing": ["$A", "$B"]}
        
        rule = Rule(
            name="test_rule",
            premises=premises,
            conclusion=conclusion,
            confidence=0.9
        )
        
        assert rule.name == "test_rule"
        assert rule.premises == premises
        assert rule.conclusion == conclusion
        assert rule.confidence == 0.9


class TestInferenceResult:
    """Test cases for InferenceResult class."""
    
    def test_inference_result_creation(self):
        """Test creating an InferenceResult."""
        result = InferenceResult(
            atom_id=123,
            rule_name="test_rule",
            premises=[1, 2, 3],
            confidence=0.85
        )
        
        assert result.atom_id == 123
        assert result.rule_name == "test_rule"
        assert result.premises == [1, 2, 3]
        assert result.confidence == 0.85