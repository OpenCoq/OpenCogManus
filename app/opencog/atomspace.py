"""
AtomSpace integration for OpenManus framework.

Provides a simplified interface to OpenCog's AtomSpace for knowledge representation
and symbolic manipulation optimized for agent workflows.
"""

import json
from typing import Any, Dict, List, Optional, Set, Union
from pydantic import BaseModel, Field
from app.logger import logger


class Atom(BaseModel):
    """Represents an OpenCog atom with type, name, and truth value."""
    
    type: str = Field(..., description="Atom type (e.g., ConceptNode, PredicateNode)")
    name: str = Field(..., description="Atom name/value")
    truth_value: Optional[Dict[str, float]] = Field(
        default=None, 
        description="Truth value with strength and confidence"
    )
    incoming: List[int] = Field(default_factory=list, description="Incoming atom IDs")
    outgoing: List[int] = Field(default_factory=list, description="Outgoing atom IDs")
    
    class Config:
        arbitrary_types_allowed = True


class AtomSpaceManager(BaseModel):
    """
    Manages an in-memory AtomSpace for symbolic knowledge representation.
    
    This is a simplified implementation optimized for OpenManus agent workflows,
    providing core AtomSpace functionality including atom creation, querying,
    and basic reasoning operations.
    """
    
    atoms: Dict[int, Atom] = Field(default_factory=dict)
    name_index: Dict[str, Set[int]] = Field(default_factory=dict)
    type_index: Dict[str, Set[int]] = Field(default_factory=dict)
    next_id: int = Field(default=1)
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_atom(self, atom_type: str, name: str, 
                 truth_value: Optional[Dict[str, float]] = None,
                 outgoing: Optional[List[int]] = None) -> int:
        """
        Add an atom to the AtomSpace.
        
        Args:
            atom_type: Type of atom (e.g., 'ConceptNode', 'PredicateNode')
            name: Name/value of the atom
            truth_value: Optional truth value dict with 'strength' and 'confidence'
            outgoing: Optional list of outgoing atom IDs for link atoms
            
        Returns:
            ID of the created atom
        """
        # Check if atom already exists
        existing_id = self._find_existing_atom(atom_type, name, outgoing or [])
        if existing_id:
            return existing_id
            
        atom_id = self.next_id
        self.next_id += 1
        
        atom = Atom(
            type=atom_type,
            name=name,
            truth_value=truth_value or {"strength": 1.0, "confidence": 1.0},
            outgoing=outgoing or []
        )
        
        self.atoms[atom_id] = atom
        
        # Update indices
        if name not in self.name_index:
            self.name_index[name] = set()
        self.name_index[name].add(atom_id)
        
        if atom_type not in self.type_index:
            self.type_index[atom_type] = set()
        self.type_index[atom_type].add(atom_id)
        
        # Update incoming sets for outgoing atoms
        for out_id in atom.outgoing:
            if out_id in self.atoms:
                self.atoms[out_id].incoming.append(atom_id)
        
        logger.debug(f"Added atom {atom_id}: {atom_type}({name})")
        return atom_id
    
    def get_atom(self, atom_id: int) -> Optional[Atom]:
        """Get an atom by ID."""
        return self.atoms.get(atom_id)
    
    def find_atoms_by_name(self, name: str) -> List[int]:
        """Find all atoms with the given name."""
        return list(self.name_index.get(name, set()))
    
    def find_atoms_by_type(self, atom_type: str) -> List[int]:
        """Find all atoms of the given type."""
        return list(self.type_index.get(atom_type, set()))
    
    def add_concept(self, concept: str, 
                   truth_value: Optional[Dict[str, float]] = None) -> int:
        """Add a ConceptNode to the AtomSpace."""
        return self.add_atom("ConceptNode", concept, truth_value)
    
    def add_predicate(self, predicate: str,
                     truth_value: Optional[Dict[str, float]] = None) -> int:
        """Add a PredicateNode to the AtomSpace."""
        return self.add_atom("PredicateNode", predicate, truth_value)
    
    def add_inheritance(self, child: str, parent: str,
                       truth_value: Optional[Dict[str, float]] = None) -> int:
        """Add an InheritanceLink between child and parent concepts."""
        child_id = self.add_concept(child)
        parent_id = self.add_concept(parent)
        return self.add_atom("InheritanceLink", "", truth_value, [child_id, parent_id])
    
    def add_evaluation(self, predicate: str, *args: str,
                      truth_value: Optional[Dict[str, float]] = None) -> int:
        """Add an EvaluationLink for a predicate applied to arguments."""
        pred_id = self.add_predicate(predicate)
        arg_ids = [self.add_concept(arg) for arg in args]
        
        if len(arg_ids) == 1:
            # Single argument - direct evaluation
            return self.add_atom("EvaluationLink", "", truth_value, [pred_id, arg_ids[0]])
        else:
            # Multiple arguments - use ListLink
            list_id = self.add_atom("ListLink", "", None, arg_ids)
            return self.add_atom("EvaluationLink", "", truth_value, [pred_id, list_id])
    
    def query_pattern(self, pattern: Dict[str, Any]) -> List[Dict[str, int]]:
        """
        Simple pattern matching for atoms.
        
        Args:
            pattern: Dict specifying pattern to match
            
        Returns:
            List of variable bindings that satisfy the pattern
        """
        # Simplified pattern matching - extend as needed
        matches = []
        
        if pattern.get("type") == "ConceptNode":
            atom_ids = self.find_atoms_by_type("ConceptNode")
            for atom_id in atom_ids:
                atom = self.atoms[atom_id]
                if pattern.get("name") is None or atom.name == pattern["name"]:
                    matches.append({"atom_id": atom_id})
        
        return matches
    
    def get_incoming(self, atom_id: int) -> List[int]:
        """Get atoms that have this atom in their outgoing set."""
        atom = self.atoms.get(atom_id)
        return atom.incoming if atom else []
    
    def get_outgoing(self, atom_id: int) -> List[int]:
        """Get the outgoing set of an atom."""
        atom = self.atoms.get(atom_id)
        return atom.outgoing if atom else []
    
    def update_truth_value(self, atom_id: int, truth_value: Dict[str, float]):
        """Update the truth value of an atom."""
        if atom_id in self.atoms:
            self.atoms[atom_id].truth_value = truth_value
            logger.debug(f"Updated truth value for atom {atom_id}: {truth_value}")
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export AtomSpace to a dictionary for serialization."""
        return {
            "atoms": {str(k): v.dict() for k, v in self.atoms.items()},
            "next_id": self.next_id
        }
    
    def import_from_dict(self, data: Dict[str, Any]):
        """Import AtomSpace from a dictionary."""
        self.atoms = {}
        self.name_index = {}
        self.type_index = {}
        
        for atom_id_str, atom_data in data["atoms"].items():
            atom_id = int(atom_id_str)
            atom = Atom(**atom_data)
            self.atoms[atom_id] = atom
            
            # Rebuild indices
            if atom.name not in self.name_index:
                self.name_index[atom.name] = set()
            self.name_index[atom.name].add(atom_id)
            
            if atom.type not in self.type_index:
                self.type_index[atom.type] = set()
            self.type_index[atom.type].add(atom_id)
        
        self.next_id = data["next_id"]
        logger.info(f"Imported AtomSpace with {len(self.atoms)} atoms")
    
    def _find_existing_atom(self, atom_type: str, name: str, outgoing: List[int]) -> Optional[int]:
        """Find existing atom with same type, name, and outgoing set."""
        candidates = self.type_index.get(atom_type, set())
        
        for atom_id in candidates:
            atom = self.atoms[atom_id]
            if atom.name == name and atom.outgoing == outgoing:
                return atom_id
        
        return None
    
    def size(self) -> int:
        """Return the number of atoms in the AtomSpace."""
        return len(self.atoms)
    
    def clear(self):
        """Clear all atoms from the AtomSpace."""
        self.atoms.clear()
        self.name_index.clear()
        self.type_index.clear()
        self.next_id = 1
        logger.info("AtomSpace cleared")