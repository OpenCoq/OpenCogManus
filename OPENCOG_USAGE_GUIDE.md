# OpenCog Integration Usage Guide

This guide provides comprehensive instructions for using the OpenCog symbolic AI integration with the OpenManus framework.

## Overview

The OpenCog integration provides three core capabilities:

1. **Knowledge Representation** - Store and manipulate symbolic knowledge using AtomSpace
2. **Symbolic Reasoning** - Perform forward/backward chaining inference with logical rules  
3. **Pattern Matching** - Find patterns, similarities, and connections in knowledge graphs

## Quick Start

### Installation

Ensure you have the required dependencies:

```bash
pip install pydantic loguru
```

### Basic Usage

```python
import asyncio
from app.opencog.cognitive_agent import CognitiveAgent

async def main():
    # Create cognitive agent with OpenCog capabilities
    agent = CognitiveAgent(
        enable_auto_reasoning=True,
        knowledge_persistence=True,
        max_reasoning_iterations=5
    )
    
    # Build knowledge base
    agent.add_knowledge("concept", "Artificial Intelligence")
    agent.add_knowledge("concept", "Machine Learning")
    agent.add_knowledge("relation", "Machine Learning", object_="Artificial Intelligence")
    agent.add_knowledge("fact", "Machine Learning", "learns_from", "data")
    
    # Query and analyze
    results = agent.query_knowledge("machine learning")
    print(f"Found {len(results)} relevant items")
    
    # Use cognitive capabilities
    response = await agent.run("Explain the relationship between AI and Machine Learning using symbolic reasoning")
    print(response)

asyncio.run(main())
```

## Component Details

### 1. AtomSpace - Knowledge Representation

The AtomSpace provides the foundation for symbolic knowledge representation:

#### Core Concepts

- **Atoms**: Basic units of knowledge (concepts, predicates, relationships)
- **Truth Values**: Uncertainty representation with strength and confidence  
- **Links**: Relationships between atoms (inheritance, evaluation, etc.)
- **Indices**: Fast lookup by name and type

#### Usage Examples

```python
from app.opencog.atomspace import AtomSpaceManager

atomspace = AtomSpaceManager()

# Add concepts
ai_id = atomspace.add_concept("AI")
ml_id = atomspace.add_concept("Machine Learning")

# Add relationships  
inheritance_id = atomspace.add_inheritance("Machine Learning", "AI")

# Add facts
fact_id = atomspace.add_evaluation("processes", "Machine Learning", "data")

# Add with uncertainty
uncertain_id = atomspace.add_concept("Hypothesis", 
                                   truth_value={"strength": 0.7, "confidence": 0.6})

# Query
concepts = atomspace.find_atoms_by_type("ConceptNode")
ai_atoms = atomspace.find_atoms_by_name("AI")

# Export/Import
data = atomspace.export_to_dict()
new_atomspace = AtomSpaceManager()
new_atomspace.import_from_dict(data)
```

### 2. Reasoning Engine - Symbolic Inference

The reasoning engine performs logical inference to derive new knowledge:

#### Reasoning Modes

- **Forward Chaining**: Derive new facts from existing knowledge
- **Backward Chaining**: Prove goals by working backwards from conclusions
- **Rule-Based**: Apply logical rules (transitivity, deduction, etc.)

#### Usage Examples

```python
from app.opencog.reasoning import ReasoningEngine

reasoning = ReasoningEngine()
reasoning.atomspace = atomspace

# Add default logical rules
reasoning.add_default_rules()

# Forward chaining inference
inferences = reasoning.forward_chain(max_inferences=10)
for inference in inferences:
    print(f"Inferred atom {inference.atom_id} using rule {inference.rule_name}")

# Backward chaining to prove goals
goal_pattern = {"type": "ConceptNode", "name": "Target"}
proofs = reasoning.backward_chain(goal_pattern, max_depth=5)

# Add custom rules
reasoning.add_rule(
    "custom_rule",
    premises=[{"type": "ConceptNode", "name": "$X"}],
    conclusion={"type": "ConceptNode", "name": "${X}_derived"},
    confidence=0.8
)

# Query with reasoning
results = reasoning.query_knowledge("artificial intelligence")
```

### 3. Pattern Matcher - Structural Matching

The pattern matcher finds patterns and similarities in the knowledge graph:

#### Pattern Types

- **Exact Matching**: Find atoms matching specific patterns
- **Variable Binding**: Use variables in patterns for flexible matching
- **Similarity Search**: Find conceptually similar atoms
- **Graph Traversal**: Explore connected knowledge

#### Usage Examples

```python
from app.opencog.pattern_matcher import PatternMatcher

matcher = PatternMatcher()
matcher.atomspace = atomspace

# Create patterns with variables
var_x = matcher.create_variable("X", type_constraint="ConceptNode")
pattern = matcher.create_pattern("InheritanceLink", outgoing=["$X", "AI"])

# Pattern matching
matches = matcher.match_pattern(pattern)
for match in matches:
    print(f"Match: atom {match.atom_id}, bindings: {match.bindings}")

# Query-based matching
results = matcher.match_query("ConceptNode(AI)")

# Similarity search
similar_atoms = matcher.find_similar_atoms(ai_id, similarity_threshold=0.7)

# Find connected atoms  
connected = matcher.find_connected_atoms(ai_id, max_depth=3)

# Explain matches
for match in matches[:3]:
    explanation = matcher.explain_match(match)
    print(explanation)
```

## Cognitive Agent Integration

### Tool System

The cognitive agent exposes OpenCog functionality through tools:

#### AtomSpace Tool

```python
# Available via agent tools
await agent.call_tool("atomspace", {
    "operation": "add_concept",
    "concept": "New Concept"
})

await agent.call_tool("atomspace", {
    "operation": "query", 
    "query_text": "artificial intelligence"
})
```

#### Reasoning Tool

```python
await agent.call_tool("reasoning", {
    "operation": "forward_chain",
    "max_inferences": 10
})

await agent.call_tool("reasoning", {
    "operation": "explain",
    "atom_id": 42
})
```

#### Pattern Match Tool

```python
await agent.call_tool("pattern_match", {
    "operation": "match_query",
    "query": "ConceptNode($X)"
})

await agent.call_tool("pattern_match", {
    "operation": "find_similar",
    "target_atom_id": 42,
    "similarity_threshold": 0.8
})
```

### Advanced Agent Methods

```python
# Knowledge management
agent.add_knowledge("concept", "New Topic")
results = agent.query_knowledge("search term")

# Reasoning control
await agent._perform_cognitive_reasoning()
insights = agent._extract_reasoning_insights()

# Knowledge analysis
status = agent.get_cognitive_status()
validation = agent.validate_knowledge_consistency()
insights = agent.generate_knowledge_insights()

# Persistence
agent.save_knowledge("knowledge_base.json")
agent.load_knowledge("knowledge_base.json")
```

## Configuration Options

### Agent Configuration

```python
agent = CognitiveAgent(
    enable_auto_reasoning=True,           # Automatic reasoning after knowledge updates
    max_reasoning_iterations=5,           # Maximum inference cycles per step
    knowledge_persistence=True,           # Save knowledge between sessions
)
```

### Component Configuration

```python
# AtomSpace settings  
atomspace = AtomSpaceManager()
# (Currently uses default configuration)

# Reasoning engine settings
reasoning = ReasoningEngine(
    max_iterations=100,                   # Maximum inference iterations
    min_confidence=0.1                    # Minimum confidence threshold
)

# Pattern matcher settings
matcher = PatternMatcher(
    max_results=100,                      # Maximum results to return
    enable_fuzzy_matching=True,           # Enable approximate matching
    fuzzy_threshold=0.8                   # Minimum similarity for fuzzy matches
)
```

## Best Practices

### 1. Knowledge Organization

```python
# Start with core concepts
agent.add_knowledge("concept", "Domain")
agent.add_knowledge("concept", "Subdomain") 

# Build hierarchies
agent.add_knowledge("relation", "Subdomain", object_="Domain")

# Add specific facts
agent.add_knowledge("fact", "Subdomain", "property", "value")
```

### 2. Truth Value Management

```python
# Use appropriate certainty levels
agent.add_knowledge("concept", "Certain Fact", 
                   truth_value={"strength": 1.0, "confidence": 1.0})

agent.add_knowledge("concept", "Hypothesis",
                   truth_value={"strength": 0.7, "confidence": 0.5})
```

### 3. Reasoning Strategy

```python
# Build knowledge incrementally
for concept in core_concepts:
    agent.add_knowledge("concept", concept)

# Run reasoning periodically  
await agent._perform_cognitive_reasoning()

# Validate consistency
validation = agent.validate_knowledge_consistency()
if not validation["consistent"]:
    handle_inconsistencies(validation["issues"])
```

### 4. Performance Optimization

```python
# Monitor knowledge base size
status = agent.get_cognitive_status()
if status["total_atoms"] > 1000:
    # Consider archiving or restructuring

# Use specific queries
results = agent.query_knowledge("specific term")  # Better than general queries

# Limit reasoning iterations
inferences = reasoning.forward_chain(max_inferences=5)  # Prevent runaway inference
```

## Command Line Interface

### Basic Usage

```bash
# Interactive demonstration
python run_cognitive_agent.py --demo

# Custom prompts
python run_cognitive_agent.py --prompt "Build knowledge about space exploration"

# Persistence
python run_cognitive_agent.py --persist-knowledge --prompt "Continue previous session"
```

### Knowledge Management

```bash
# Save knowledge
python run_cognitive_agent.py --save-knowledge my_knowledge.json

# Load knowledge  
python run_cognitive_agent.py --load-knowledge my_knowledge.json --prompt "Query loaded knowledge"

# Combined operations
python run_cognitive_agent.py --load-knowledge ai_kb.json --prompt "Expand AI knowledge" --save-knowledge ai_kb_expanded.json
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure project root is in Python path
2. **Dependency Issues**: Install required packages (pydantic, loguru)
3. **Memory Usage**: Monitor AtomSpace size for large knowledge bases
4. **Reasoning Loops**: Set appropriate max_iterations to prevent infinite loops

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check system status
status = agent.get_cognitive_status()
print(f"Total atoms: {status['total_atoms']}")
print(f"Reasoning rules: {status['reasoning_rules']}")

# Validate knowledge
validation = agent.validate_knowledge_consistency()
for issue in validation.get("issues", []):
    print(f"Issue: {issue['type']} - {issue['description']}")

# Generate insights
insights = agent.generate_knowledge_insights()
print(f"Knowledge maturity: {insights['knowledge_graph_analysis']['maturity']['level']}")
```

## Advanced Use Cases

### 1. Research Analysis

```python
# Build domain knowledge
for topic in research_topics:
    agent.add_knowledge("concept", topic)
    
# Add relationships and evidence
for relationship in domain_relationships:
    agent.add_knowledge("relation", relationship[0], object_=relationship[1])

# Discover insights through reasoning
await agent.run("Analyze the research domain and identify potential connections and gaps")
```

### 2. Educational Systems

```python
# Build curriculum knowledge
agent.add_knowledge("concept", "Machine Learning")
agent.add_knowledge("concept", "Prerequisites") 
agent.add_knowledge("relation", "Machine Learning", object_="Prerequisites")

# Adaptive learning
student_knowledge = get_student_knowledge()
response = await agent.run(f"Given student knowledge {student_knowledge}, recommend next learning steps")
```

### 3. Decision Support

```python
# Model decision factors
for factor in decision_factors:
    agent.add_knowledge("concept", factor)
    agent.add_knowledge("fact", factor, "impacts", decision_outcome)

# Analyze options
await agent.run("Analyze decision factors and recommend the best course of action")
```

## Integration with Other Systems

The OpenCog integration works seamlessly with:

- **OpenManus Agent Framework**: Cognitive agent extends ToolCallAgent
- **MCP Protocol**: Tools can be exposed via Model Context Protocol
- **Other AI Systems**: Knowledge can be exported/imported as JSON
- **Databases**: AtomSpace data can be persisted to various storage systems

This provides a powerful foundation for symbolic AI applications within the broader OpenManus ecosystem.