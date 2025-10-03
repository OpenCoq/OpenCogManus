"""
Pattern matching engine for OpenCog integration with OpenManus.

Provides advanced pattern matching capabilities for symbolic query processing
and knowledge retrieval from the AtomSpace.
"""

import re
from typing import Dict, List, Optional, Set, Any, Union
from pydantic import BaseModel, Field
from app.logger import logger
from app.opencog.atomspace import AtomSpaceManager, Atom


class Variable(BaseModel):
    """Represents a pattern matching variable."""
    
    name: str = Field(..., description="Variable name")
    type_constraint: Optional[str] = Field(
        default=None, 
        description="Optional type constraint for the variable"
    )
    value_constraint: Optional[str] = Field(
        default=None,
        description="Optional value constraint (regex pattern)"
    )
    
    class Config:
        arbitrary_types_allowed = True


class Pattern(BaseModel):
    """Represents a pattern for matching against atoms."""
    
    type: Optional[str] = Field(default=None, description="Atom type to match")
    name: Optional[Union[str, Variable]] = Field(
        default=None, 
        description="Atom name to match (can be variable)"
    )
    outgoing: Optional[List[Union[int, str, "Pattern", Variable]]] = Field(
        default=None,
        description="Outgoing atoms to match"
    )
    variables: Dict[str, Variable] = Field(
        default_factory=dict,
        description="Variables used in this pattern"
    )
    
    class Config:
        arbitrary_types_allowed = True


class MatchResult(BaseModel):
    """Result of a pattern matching operation."""
    
    atom_id: int = Field(..., description="ID of matched atom")
    bindings: Dict[str, Any] = Field(
        default_factory=dict,
        description="Variable bindings from the match"
    )
    score: float = Field(default=1.0, description="Match quality score")
    
    class Config:
        arbitrary_types_allowed = True


class PatternMatcher(BaseModel):
    """
    Advanced pattern matching engine for OpenCog AtomSpace.
    
    Provides sophisticated pattern matching capabilities including variable
    binding, constraint satisfaction, and fuzzy matching.
    """
    
    atomspace: AtomSpaceManager = Field(default_factory=AtomSpaceManager)
    max_results: int = Field(default=100, description="Maximum results to return")
    enable_fuzzy_matching: bool = Field(
        default=True, 
        description="Enable approximate string matching"
    )
    fuzzy_threshold: float = Field(
        default=0.8, 
        description="Minimum similarity for fuzzy matching"
    )
    
    class Config:
        arbitrary_types_allowed = True
    
    def create_variable(self, name: str, type_constraint: Optional[str] = None,
                       value_constraint: Optional[str] = None) -> Variable:
        """Create a pattern matching variable."""
        return Variable(
            name=name,
            type_constraint=type_constraint,
            value_constraint=value_constraint
        )
    
    def create_pattern(self, atom_type: Optional[str] = None,
                      name: Optional[Union[str, Variable]] = None,
                      outgoing: Optional[List[Union[int, str, Pattern, Variable]]] = None) -> Pattern:
        """Create a pattern for matching."""
        variables = {}
        
        # Collect variables from name
        if isinstance(name, Variable):
            variables[name.name] = name
        
        # Collect variables from outgoing
        if outgoing:
            for item in outgoing:
                if isinstance(item, Variable):
                    variables[item.name] = item
                elif isinstance(item, Pattern):
                    variables.update(item.variables)
        
        return Pattern(
            type=atom_type,
            name=name,
            outgoing=outgoing,
            variables=variables
        )
    
    def match_pattern(self, pattern: Pattern) -> List[MatchResult]:
        """
        Match a pattern against the AtomSpace.
        
        Args:
            pattern: Pattern to match
            
        Returns:
            List of match results with variable bindings
        """
        results = []
        
        # Get candidate atoms based on type constraint
        if pattern.type:
            candidates = self.atomspace.find_atoms_by_type(pattern.type)
        else:
            candidates = list(self.atomspace.atoms.keys())
        
        for atom_id in candidates:
            atom = self.atomspace.get_atom(atom_id)
            if not atom:
                continue
            
            match_result = self._match_atom_against_pattern(atom, atom_id, pattern)
            if match_result:
                results.append(match_result)
        
        # Sort by match score
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Limit results
        if len(results) > self.max_results:
            results = results[:self.max_results]
        
        logger.debug(f"Pattern matching found {len(results)} matches")
        return results
    
    def match_query(self, query_str: str) -> List[MatchResult]:
        """
        Match a string query pattern against the AtomSpace.
        
        Args:
            query_str: String representation of query pattern
            
        Returns:
            List of match results
        """
        pattern = self._parse_query_string(query_str)
        if pattern:
            return self.match_pattern(pattern)
        else:
            return []
    
    def find_similar_atoms(self, target_atom_id: int, 
                          similarity_threshold: float = 0.7) -> List[MatchResult]:
        """
        Find atoms similar to a target atom.
        
        Args:
            target_atom_id: ID of atom to find similarities for
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of similar atoms with similarity scores
        """
        target_atom = self.atomspace.get_atom(target_atom_id)
        if not target_atom:
            return []
        
        results = []
        
        for atom_id, atom in self.atomspace.atoms.items():
            if atom_id == target_atom_id:
                continue
            
            similarity = self._calculate_atom_similarity(target_atom, atom)
            if similarity >= similarity_threshold:
                results.append(MatchResult(
                    atom_id=atom_id,
                    bindings={},
                    score=similarity
                ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:self.max_results]
    
    def find_connected_atoms(self, start_atom_id: int, 
                           max_depth: int = 3,
                           connection_types: Optional[List[str]] = None) -> List[MatchResult]:
        """
        Find atoms connected to a starting atom through links.
        
        Args:
            start_atom_id: Starting atom ID
            max_depth: Maximum traversal depth
            connection_types: Optional list of link types to follow
            
        Returns:
            List of connected atoms
        """
        visited = set()
        results = []
        
        def traverse(atom_id: int, depth: int):
            if depth > max_depth or atom_id in visited:
                return
            
            visited.add(atom_id)
            atom = self.atomspace.get_atom(atom_id)
            if not atom:
                return
            
            # Add current atom to results (except starting atom)
            if atom_id != start_atom_id:
                results.append(MatchResult(
                    atom_id=atom_id,
                    bindings={"depth": depth},
                    score=1.0 / depth  # Closer atoms have higher score
                ))
            
            # Traverse incoming and outgoing connections
            for connected_id in atom.incoming + atom.outgoing:
                connected_atom = self.atomspace.get_atom(connected_id)
                if connected_atom:
                    # Check connection type filter
                    if connection_types is None or connected_atom.type in connection_types:
                        traverse(connected_id, depth + 1)
        
        traverse(start_atom_id, 0)
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:self.max_results]
    
    def _match_atom_against_pattern(self, atom: Atom, atom_id: int, 
                                   pattern: Pattern) -> Optional[MatchResult]:
        """Match a single atom against a pattern."""
        bindings = {}
        score = 1.0
        
        # Check type constraint
        if pattern.type and atom.type != pattern.type:
            return None
        
        # Check name constraint
        if pattern.name is not None:
            if isinstance(pattern.name, Variable):
                var = pattern.name
                if var.type_constraint and atom.type != var.type_constraint:
                    return None
                if var.value_constraint and not re.match(var.value_constraint, atom.name):
                    return None
                bindings[var.name] = atom.name
            elif isinstance(pattern.name, str):
                if pattern.name.startswith("$"):
                    # Variable reference
                    var_name = pattern.name[1:]
                    if var_name in pattern.variables:
                        var = pattern.variables[var_name]
                        if var.type_constraint and atom.type != var.type_constraint:
                            return None
                        if var.value_constraint and not re.match(var.value_constraint, atom.name):
                            return None
                    bindings[var_name] = atom.name
                else:
                    # Exact match required
                    if self.enable_fuzzy_matching:
                        similarity = self._calculate_string_similarity(pattern.name, atom.name)
                        if similarity < self.fuzzy_threshold:
                            return None
                        score *= similarity
                    else:
                        if atom.name != pattern.name:
                            return None
        
        # Check outgoing constraints
        if pattern.outgoing is not None:
            if len(pattern.outgoing) != len(atom.outgoing):
                return None
            
            for i, pattern_out in enumerate(pattern.outgoing):
                atom_out_id = atom.outgoing[i]
                
                if isinstance(pattern_out, int):
                    # Exact atom ID match
                    if atom_out_id != pattern_out:
                        return None
                elif isinstance(pattern_out, str):
                    if pattern_out.startswith("$"):
                        # Variable binding
                        var_name = pattern_out[1:]
                        bindings[var_name] = atom_out_id
                    else:
                        # Match by name
                        out_atom = self.atomspace.get_atom(atom_out_id)
                        if not out_atom or out_atom.name != pattern_out:
                            return None
                elif isinstance(pattern_out, Variable):
                    # Variable with constraints
                    out_atom = self.atomspace.get_atom(atom_out_id)
                    if not out_atom:
                        return None
                    
                    if pattern_out.type_constraint and out_atom.type != pattern_out.type_constraint:
                        return None
                    if pattern_out.value_constraint and not re.match(pattern_out.value_constraint, out_atom.name):
                        return None
                    
                    bindings[pattern_out.name] = atom_out_id
                elif isinstance(pattern_out, Pattern):
                    # Recursive pattern match
                    out_atom = self.atomspace.get_atom(atom_out_id)
                    if not out_atom:
                        return None
                    
                    sub_match = self._match_atom_against_pattern(out_atom, atom_out_id, pattern_out)
                    if not sub_match:
                        return None
                    
                    # Merge bindings
                    bindings.update(sub_match.bindings)
                    score *= sub_match.score
        
        return MatchResult(
            atom_id=atom_id,
            bindings=bindings,
            score=score
        )
    
    def _parse_query_string(self, query_str: str) -> Optional[Pattern]:
        """Parse a string query into a pattern."""
        # Simplified query parsing - extend for more complex syntax
        query_str = query_str.strip()
        
        # Simple pattern: Type(name)
        match = re.match(r"(\w+)\(([^)]+)\)", query_str)
        if match:
            atom_type, name = match.groups()
            
            if name.startswith("$"):
                # Variable
                var = self.create_variable(name[1:])
                return self.create_pattern(atom_type, var)
            else:
                # Literal name
                return self.create_pattern(atom_type, name)
        
        # Simple concept search: just a name
        if query_str and not query_str.startswith("$"):
            return self.create_pattern(name=query_str)
        
        return None
    
    def _calculate_atom_similarity(self, atom1: Atom, atom2: Atom) -> float:
        """Calculate similarity between two atoms."""
        if atom1.type != atom2.type:
            return 0.0
        
        # Name similarity
        name_sim = self._calculate_string_similarity(atom1.name, atom2.name)
        
        # Structure similarity (simplified)
        structure_sim = 1.0
        if len(atom1.outgoing) != len(atom2.outgoing):
            structure_sim = 0.5
        
        # Truth value similarity
        tv_sim = 1.0
        if atom1.truth_value and atom2.truth_value:
            str1 = atom1.truth_value.get("strength", 1.0)
            str2 = atom2.truth_value.get("strength", 1.0)
            conf1 = atom1.truth_value.get("confidence", 1.0)
            conf2 = atom2.truth_value.get("confidence", 1.0)
            
            tv_sim = 1.0 - (abs(str1 - str2) + abs(conf1 - conf2)) / 2.0
        
        # Weighted combination
        return 0.5 * name_sim + 0.3 * structure_sim + 0.2 * tv_sim
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings using Levenshtein distance."""
        if str1 == str2:
            return 1.0
        
        if not str1 or not str2:
            return 0.0
        
        # Simple Levenshtein distance implementation
        len1, len2 = len(str1), len(str2)
        
        if len1 > len2:
            str1, str2 = str2, str1
            len1, len2 = len2, len1
        
        current_row = list(range(len1 + 1))
        
        for i in range(1, len2 + 1):
            previous_row, current_row = current_row, [i] + [0] * len1
            for j in range(1, len1 + 1):
                add, delete, change = (
                    previous_row[j] + 1,
                    current_row[j - 1] + 1,
                    previous_row[j - 1]
                )
                if str1[j - 1] != str2[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)
        
        max_len = max(len(str1), len(str2))
        return 1.0 - (current_row[len1] / max_len) if max_len > 0 else 1.0
    
    def explain_match(self, match_result: MatchResult) -> Dict[str, Any]:
        """
        Explain how a match was found.
        
        Args:
            match_result: Result to explain
            
        Returns:
            Explanation dictionary
        """
        atom = self.atomspace.get_atom(match_result.atom_id)
        if not atom:
            return {"error": "Atom not found"}
        
        return {
            "atom_id": match_result.atom_id,
            "atom_type": atom.type,
            "atom_name": atom.name,
            "match_score": match_result.score,
            "variable_bindings": match_result.bindings,
            "explanation": f"Matched atom {atom.type}('{atom.name}') with score {match_result.score:.3f}"
        }