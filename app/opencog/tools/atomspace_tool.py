"""
AtomSpace tool for OpenManus framework.

Provides tool interface for AtomSpace operations including adding concepts,
relations, and querying the knowledge base.
"""

from typing import Any, Dict, List, Optional
from app.tool.base import BaseTool, ToolResult
from app.logger import logger


class AtomSpaceTool(BaseTool):
    """Tool for manipulating AtomSpace knowledge base."""
    
    name: str = "atomspace"
    description: str = """
    Manipulate the AtomSpace knowledge base. Available operations:
    - add_concept: Add a concept to the knowledge base
    - add_relation: Add an inheritance relation between concepts
    - add_fact: Add a factual statement
    - query: Query the knowledge base
    - get_atom: Get details of a specific atom
    - list_atoms: List atoms by type
    - clear: Clear the AtomSpace
    - export: Export knowledge to JSON
    - import: Import knowledge from JSON
    """
    
    parameters: dict = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": [
                    "add_concept", "add_relation", "add_fact", "query", 
                    "get_atom", "list_atoms", "clear", "export", "import"
                ],
                "description": "Operation to perform on the AtomSpace"
            },
            "concept": {
                "type": "string",
                "description": "Concept name (for add_concept)"
            },
            "subject": {
                "type": "string", 
                "description": "Subject of relation or fact"
            },
            "predicate": {
                "type": "string",
                "description": "Predicate for facts or relation type"
            },
            "object": {
                "type": "string",
                "description": "Object of relation or fact"
            },
            "atom_type": {
                "type": "string",
                "description": "Type of atoms to list (for list_atoms)"
            },
            "atom_id": {
                "type": "integer",
                "description": "Atom ID (for get_atom)"
            },
            "query_text": {
                "type": "string",
                "description": "Query text (for query operation)"
            },
            "truth_strength": {
                "type": "number",
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Truth value strength (optional, default 1.0)"
            },
            "truth_confidence": {
                "type": "number", 
                "minimum": 0.0,
                "maximum": 1.0,
                "description": "Truth value confidence (optional, default 1.0)"
            },
            "json_data": {
                "type": "string",
                "description": "JSON data for import operation"
            }
        },
        "required": ["operation"]
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        self._atomspace = None
    
    def set_atomspace(self, atomspace):
        """Set the AtomSpace instance to operate on."""
        self._atomspace = atomspace
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute AtomSpace operation."""
        if not self._atomspace:
            return ToolResult(error="AtomSpace not initialized")
        
        operation = kwargs.get("operation")
        
        try:
            if operation == "add_concept":
                return await self._add_concept(kwargs)
            elif operation == "add_relation":
                return await self._add_relation(kwargs)
            elif operation == "add_fact":
                return await self._add_fact(kwargs)
            elif operation == "query":
                return await self._query(kwargs)
            elif operation == "get_atom":
                return await self._get_atom(kwargs)
            elif operation == "list_atoms":
                return await self._list_atoms(kwargs)
            elif operation == "clear":
                return await self._clear(kwargs)
            elif operation == "export":
                return await self._export(kwargs)
            elif operation == "import":
                return await self._import(kwargs)
            else:
                return ToolResult(error=f"Unknown operation: {operation}")
                
        except Exception as e:
            logger.error(f"AtomSpace tool error: {e}")
            return ToolResult(error=str(e))
    
    async def _add_concept(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Add a concept to the AtomSpace."""
        concept = kwargs.get("concept")
        if not concept:
            return ToolResult(error="concept parameter required")
        
        truth_value = self._get_truth_value(kwargs)
        atom_id = self._atomspace.add_concept(concept, truth_value)
        
        return ToolResult(output=f"Added concept '{concept}' with ID {atom_id}")
    
    async def _add_relation(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Add an inheritance relation to the AtomSpace."""
        subject = kwargs.get("subject")
        object_ = kwargs.get("object")
        
        if not subject or not object_:
            return ToolResult(error="subject and object parameters required")
        
        truth_value = self._get_truth_value(kwargs)
        atom_id = self._atomspace.add_inheritance(subject, object_, truth_value)
        
        return ToolResult(output=f"Added relation '{subject}' inherits '{object_}' with ID {atom_id}")
    
    async def _add_fact(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Add a fact to the AtomSpace."""
        predicate = kwargs.get("predicate")
        subject = kwargs.get("subject")
        
        if not predicate or not subject:
            return ToolResult(error="predicate and subject parameters required")
        
        truth_value = self._get_truth_value(kwargs)
        object_ = kwargs.get("object")
        
        if object_:
            atom_id = self._atomspace.add_evaluation(predicate, subject, object_, truth_value)
            output_msg = f"Added fact '{predicate}({subject}, {object_})' with ID {atom_id}"
        else:
            atom_id = self._atomspace.add_evaluation(predicate, subject, truth_value)
            output_msg = f"Added fact '{predicate}({subject})' with ID {atom_id}"
        
        return ToolResult(output=output_msg)
    
    async def _query(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Query the AtomSpace."""
        query_text = kwargs.get("query_text")
        if not query_text:
            return ToolResult(error="query_text parameter required")
        
        # Simple query implementation
        results = []
        
        # Search by name
        matching_atoms = self._atomspace.name_index.get(query_text, set())
        for atom_id in matching_atoms:
            atom = self._atomspace.get_atom(atom_id)
            if atom:
                results.append({
                    "id": atom_id,
                    "type": atom.type,
                    "name": atom.name,
                    "truth_value": atom.truth_value
                })
        
        # Search by partial name match
        for name, atom_ids in self._atomspace.name_index.items():
            if query_text.lower() in name.lower() and name != query_text:
                for atom_id in atom_ids:
                    atom = self._atomspace.get_atom(atom_id)
                    if atom and not any(r["id"] == atom_id for r in results):
                        results.append({
                            "id": atom_id,
                            "type": atom.type,
                            "name": atom.name,
                            "truth_value": atom.truth_value
                        })
        
        if results:
            return ToolResult(output=f"Found {len(results)} matching atoms:\n" + 
                            "\n".join([f"- {r['type']}('{r['name']}') [ID: {r['id']}]" 
                                     for r in results[:10]]))
        else:
            return ToolResult(output=f"No atoms found matching '{query_text}'")
    
    async def _get_atom(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Get details of a specific atom."""
        atom_id = kwargs.get("atom_id")
        if atom_id is None:
            return ToolResult(error="atom_id parameter required")
        
        atom = self._atomspace.get_atom(atom_id)
        if not atom:
            return ToolResult(error=f"Atom with ID {atom_id} not found")
        
        details = {
            "id": atom_id,
            "type": atom.type,
            "name": atom.name,
            "truth_value": atom.truth_value,
            "incoming_count": len(atom.incoming),
            "outgoing_count": len(atom.outgoing),
            "outgoing_ids": atom.outgoing
        }
        
        return ToolResult(output=f"Atom {atom_id} details:\n" + 
                         f"Type: {details['type']}\n" +
                         f"Name: '{details['name']}'\n" +
                         f"Truth Value: {details['truth_value']}\n" +
                         f"Incoming Links: {details['incoming_count']}\n" +
                         f"Outgoing Links: {details['outgoing_count']}")
    
    async def _list_atoms(self, kwargs: Dict[str, Any]) -> ToolResult:
        """List atoms by type."""
        atom_type = kwargs.get("atom_type")
        
        if atom_type:
            atom_ids = self._atomspace.find_atoms_by_type(atom_type)
            atoms_info = []
            
            for atom_id in atom_ids[:20]:  # Limit to first 20
                atom = self._atomspace.get_atom(atom_id)
                if atom:
                    atoms_info.append(f"{atom_id}: {atom.type}('{atom.name}')")
            
            if atoms_info:
                return ToolResult(output=f"Found {len(atom_ids)} atoms of type '{atom_type}':\n" +
                                "\n".join(atoms_info))
            else:
                return ToolResult(output=f"No atoms found of type '{atom_type}'")
        else:
            # List all atom types
            type_counts = {}
            for atom in self._atomspace.atoms.values():
                type_counts[atom.type] = type_counts.get(atom.type, 0) + 1
            
            output = f"AtomSpace contains {len(self._atomspace.atoms)} atoms:\n"
            for atom_type, count in sorted(type_counts.items()):
                output += f"- {atom_type}: {count}\n"
            
            return ToolResult(output=output)
    
    async def _clear(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Clear the AtomSpace."""
        self._atomspace.clear()
        return ToolResult(output="AtomSpace cleared")
    
    async def _export(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Export AtomSpace to JSON."""
        import json
        data = self._atomspace.export_to_dict()
        json_str = json.dumps(data, indent=2)
        return ToolResult(output=f"AtomSpace exported:\n{json_str}")
    
    async def _import(self, kwargs: Dict[str, Any]) -> ToolResult:
        """Import AtomSpace from JSON."""
        json_data = kwargs.get("json_data")
        if not json_data:
            return ToolResult(error="json_data parameter required")
        
        try:
            import json
            data = json.loads(json_data)
            self._atomspace.import_from_dict(data)
            return ToolResult(output=f"Successfully imported {len(data.get('atoms', {}))} atoms")
        except json.JSONDecodeError as e:
            return ToolResult(error=f"Invalid JSON data: {e}")
    
    def _get_truth_value(self, kwargs: Dict[str, Any]) -> Dict[str, float]:
        """Extract truth value from parameters."""
        strength = kwargs.get("truth_strength", 1.0)
        confidence = kwargs.get("truth_confidence", 1.0)
        return {"strength": strength, "confidence": confidence}