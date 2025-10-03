"""
Tests for AtomSpace implementation.
"""

import pytest
from app.opencog.atomspace import AtomSpaceManager, Atom


class TestAtomSpaceManager:
    """Test cases for AtomSpaceManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.atomspace = AtomSpaceManager()
    
    def test_add_concept(self):
        """Test adding a concept to the AtomSpace."""
        atom_id = self.atomspace.add_concept("AI")
        
        assert atom_id == 1
        assert self.atomspace.size() == 1
        
        atom = self.atomspace.get_atom(atom_id)
        assert atom is not None
        assert atom.type == "ConceptNode"
        assert atom.name == "AI"
        assert atom.truth_value["strength"] == 1.0
        assert atom.truth_value["confidence"] == 1.0
    
    def test_add_concept_with_truth_value(self):
        """Test adding a concept with custom truth value."""
        truth_value = {"strength": 0.8, "confidence": 0.9}
        atom_id = self.atomspace.add_concept("Uncertain", truth_value)
        
        atom = self.atomspace.get_atom(atom_id)
        assert atom.truth_value["strength"] == 0.8
        assert atom.truth_value["confidence"] == 0.9
    
    def test_add_duplicate_concept(self):
        """Test that duplicate concepts return the same ID."""
        id1 = self.atomspace.add_concept("AI")
        id2 = self.atomspace.add_concept("AI")
        
        assert id1 == id2
        assert self.atomspace.size() == 1
    
    def test_add_predicate(self):
        """Test adding a predicate to the AtomSpace."""
        atom_id = self.atomspace.add_predicate("can_think")
        
        atom = self.atomspace.get_atom(atom_id)
        assert atom.type == "PredicateNode"
        assert atom.name == "can_think"
    
    def test_add_inheritance(self):
        """Test adding an inheritance relationship."""
        atom_id = self.atomspace.add_inheritance("AI", "Technology")
        
        atom = self.atomspace.get_atom(atom_id)
        assert atom.type == "InheritanceLink"
        assert len(atom.outgoing) == 2
        
        # Check that child and parent concepts were created
        ai_atoms = self.atomspace.find_atoms_by_name("AI")
        tech_atoms = self.atomspace.find_atoms_by_name("Technology")
        
        assert len(ai_atoms) == 1
        assert len(tech_atoms) == 1
        assert atom.outgoing == [ai_atoms[0], tech_atoms[0]]
    
    def test_add_evaluation_single_arg(self):
        """Test adding an evaluation with single argument."""
        atom_id = self.atomspace.add_evaluation("exists", "AI")
        
        atom = self.atomspace.get_atom(atom_id)
        assert atom.type == "EvaluationLink"
        assert len(atom.outgoing) == 2
    
    def test_add_evaluation_multiple_args(self):
        """Test adding an evaluation with multiple arguments."""
        atom_id = self.atomspace.add_evaluation("helps", "AI", "Human")
        
        atom = self.atomspace.get_atom(atom_id)
        assert atom.type == "EvaluationLink"
        assert len(atom.outgoing) == 2
        
        # Second outgoing should be a ListLink
        list_atom = self.atomspace.get_atom(atom.outgoing[1])
        assert list_atom.type == "ListLink"
        assert len(list_atom.outgoing) == 2
    
    def test_find_atoms_by_name(self):
        """Test finding atoms by name."""
        self.atomspace.add_concept("AI")
        self.atomspace.add_concept("ML")
        self.atomspace.add_concept("AI")  # Duplicate
        
        ai_atoms = self.atomspace.find_atoms_by_name("AI")
        ml_atoms = self.atomspace.find_atoms_by_name("ML")
        missing_atoms = self.atomspace.find_atoms_by_name("Missing")
        
        assert len(ai_atoms) == 1
        assert len(ml_atoms) == 1
        assert len(missing_atoms) == 0
    
    def test_find_atoms_by_type(self):
        """Test finding atoms by type."""
        self.atomspace.add_concept("AI")
        self.atomspace.add_predicate("can_think")
        self.atomspace.add_inheritance("AI", "Technology")
        
        concepts = self.atomspace.find_atoms_by_type("ConceptNode")
        predicates = self.atomspace.find_atoms_by_type("PredicateNode")
        inheritances = self.atomspace.find_atoms_by_type("InheritanceLink")
        
        assert len(concepts) == 2  # AI and Technology
        assert len(predicates) == 1
        assert len(inheritances) == 1
    
    def test_get_incoming_outgoing(self):
        """Test getting incoming and outgoing atom sets."""
        # Create inheritance: AI -> Technology
        inheritance_id = self.atomspace.add_inheritance("AI", "Technology")
        ai_atoms = self.atomspace.find_atoms_by_name("AI")
        ai_id = ai_atoms[0]
        
        # AI should have the inheritance link in its incoming set
        incoming = self.atomspace.get_incoming(ai_id)
        assert inheritance_id in incoming
        
        # The inheritance link should have AI in its outgoing set
        outgoing = self.atomspace.get_outgoing(inheritance_id)
        assert ai_id in outgoing
    
    def test_update_truth_value(self):
        """Test updating truth values."""
        atom_id = self.atomspace.add_concept("AI")
        
        new_truth_value = {"strength": 0.7, "confidence": 0.8}
        self.atomspace.update_truth_value(atom_id, new_truth_value)
        
        atom = self.atomspace.get_atom(atom_id)
        assert atom.truth_value["strength"] == 0.7
        assert atom.truth_value["confidence"] == 0.8
    
    def test_export_import(self):
        """Test exporting and importing AtomSpace."""
        # Add some atoms
        self.atomspace.add_concept("AI")
        self.atomspace.add_inheritance("AI", "Technology")
        
        # Export
        data = self.atomspace.export_to_dict()
        assert "atoms" in data
        assert "next_id" in data
        
        # Create new AtomSpace and import
        new_atomspace = AtomSpaceManager()
        new_atomspace.import_from_dict(data)
        
        # Verify import
        assert new_atomspace.size() == self.atomspace.size()
        assert len(new_atomspace.find_atoms_by_name("AI")) == 1
        assert len(new_atomspace.find_atoms_by_type("InheritanceLink")) == 1
    
    def test_clear(self):
        """Test clearing the AtomSpace."""
        self.atomspace.add_concept("AI")
        self.atomspace.add_concept("ML")
        
        assert self.atomspace.size() == 2
        
        self.atomspace.clear()
        
        assert self.atomspace.size() == 0
        assert len(self.atomspace.atoms) == 0
        assert len(self.atomspace.name_index) == 0
        assert len(self.atomspace.type_index) == 0
        assert self.atomspace.next_id == 1


class TestAtom:
    """Test cases for Atom class."""
    
    def test_atom_creation(self):
        """Test creating an Atom."""
        atom = Atom(
            type="ConceptNode",
            name="AI",
            truth_value={"strength": 0.9, "confidence": 0.8}
        )
        
        assert atom.type == "ConceptNode"
        assert atom.name == "AI"
        assert atom.truth_value["strength"] == 0.9
        assert atom.truth_value["confidence"] == 0.8
        assert atom.incoming == []
        assert atom.outgoing == []
    
    def test_atom_with_connections(self):
        """Test creating an Atom with connections."""
        atom = Atom(
            type="InheritanceLink",
            name="",
            outgoing=[1, 2],
            incoming=[3, 4]
        )
        
        assert atom.outgoing == [1, 2]
        assert atom.incoming == [3, 4]