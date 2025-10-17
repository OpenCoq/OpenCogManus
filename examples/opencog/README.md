# OpenCog Integration Examples

This directory contains examples and demonstrations of the OpenCog symbolic AI integration with the OpenManus framework.

## Quick Start

### Basic Usage

```python
import asyncio
from app.opencog.cognitive_agent import CognitiveAgent

async def main():
    # Create cognitive agent
    agent = CognitiveAgent(
        enable_auto_reasoning=True,
        knowledge_persistence=True
    )
    
    # Add some knowledge
    agent.add_knowledge("concept", "Artificial Intelligence")
    agent.add_knowledge("concept", "Machine Learning")
    agent.add_knowledge("relation", "Machine Learning", object_="Artificial Intelligence")
    
    # Query and reason
    results = agent.query_knowledge("AI")
    await agent.run("Explain the relationship between AI and Machine Learning")

asyncio.run(main())
```

### Command Line Demo

```bash
# Run interactive demonstration
python run_cognitive_agent.py --demo

# Run with specific prompt
python run_cognitive_agent.py --prompt "Build knowledge about space exploration"

# Persist knowledge between runs  
python run_cognitive_agent.py --persist-knowledge --prompt "Continue learning about AI"

# Load/save knowledge
python run_cognitive_agent.py --load-knowledge ai_kb.json --prompt "Query existing knowledge"
python run_cognitive_agent.py --save-knowledge ai_kb.json
```

## Core Components

### AtomSpace
- **Purpose**: Symbolic knowledge representation
- **Features**: Concepts, predicates, relationships with truth values
- **Usage**: Store and retrieve structured knowledge

```python
from app.opencog.atomspace import AtomSpaceManager

atomspace = AtomSpaceManager()
ai_id = atomspace.add_concept("AI", truth_value={"strength": 0.9, "confidence": 0.8})
ml_id = atomspace.add_concept("Machine Learning") 
relation_id = atomspace.add_inheritance("Machine Learning", "AI")
```

### Reasoning Engine
- **Purpose**: Symbolic inference and rule-based reasoning
- **Features**: Forward chaining, backward chaining, custom rules
- **Usage**: Derive new knowledge from existing facts

```python
from app.opencog.reasoning import ReasoningEngine

engine = ReasoningEngine()
engine.atomspace = atomspace
engine.add_default_rules()

# Forward chaining to discover new knowledge
inferences = engine.forward_chain(max_inferences=10)

# Backward chaining to prove goals
goal = {"type": "ConceptNode", "name": "Target"}
proofs = engine.backward_chain(goal, max_depth=5)
```

### Pattern Matcher
- **Purpose**: Advanced structural pattern matching
- **Features**: Variable binding, fuzzy matching, graph traversal
- **Usage**: Find patterns and similarities in knowledge

```python
from app.opencog.pattern_matcher import PatternMatcher

matcher = PatternMatcher()
matcher.atomspace = atomspace

# Query-based pattern matching
results = matcher.match_query("ConceptNode(AI)")

# Similarity search
similar = matcher.find_similar_atoms(ai_id, similarity_threshold=0.7)

# Connection analysis
connected = matcher.find_connected_atoms(ai_id, max_depth=3)
```

## Available Tools

The cognitive agent exposes OpenCog functionality through tools:

### AtomSpace Tool (`atomspace`)

Operations:
- `add_concept`: Add concepts to knowledge base
- `add_relation`: Add inheritance relationships
- `add_fact`: Add factual statements  
- `query`: Search knowledge base
- `list_atoms`: Browse atoms by type
- `export`/`import`: Save/load knowledge

### Reasoning Tool (`reasoning`)

Operations:
- `forward_chain`: Perform forward inference
- `backward_chain`: Prove goals with backward reasoning
- `add_rule`: Add custom reasoning rules
- `query_knowledge`: Knowledge-aware querying
- `explain`: Explain reasoning chains

### Pattern Match Tool (`pattern_match`)

Operations:
- `match_pattern`: Structural pattern matching
- `match_query`: String-based pattern queries
- `find_similar`: Discover similar concepts
- `find_connected`: Graph traversal and connections

### Knowledge Query Tool (`knowledge_query`)

Operations:
- `query`: High-level knowledge analysis
- `summarize`: Generate knowledge summaries
- `insights`: Extract knowledge insights  
- `validate`: Check knowledge consistency

## Configuration Examples

See `cognitive_config.py` for detailed configuration options:

- **Basic Config**: General purpose usage
- **Research Config**: Enhanced reasoning for analysis
- **Educational Config**: Optimized for learning/teaching
- **Production Config**: Performance and reliability focused

## Knowledge Domains

Pre-defined knowledge domains for quick initialization:

- **Artificial Intelligence**: ML, DL, NLP, CV, Robotics
- **Science**: Physics, Chemistry, Biology, Mathematics

```python
from examples.opencog.cognitive_config import initialize_knowledge_domain

initialize_knowledge_domain(agent, "artificial_intelligence")
```

## Advanced Features

### Knowledge Validation

```python
# Check knowledge consistency
validation = agent.validate_knowledge_consistency()
print(f"Knowledge is consistent: {validation['consistent']}")
for issue in validation['issues']:
    print(f"Issue: {issue['type']} - {issue['description']}")
```

### Knowledge Insights

```python
# Generate insights about knowledge base
insights = agent.generate_knowledge_insights()
print(f"Knowledge maturity: {insights['knowledge_graph_analysis']['maturity']['level']}")
for concept in insights['concept_rankings'][:5]:
    print(f"  {concept['concept']}: {concept['connections']} connections")
```

### Truth Value Reasoning

```python
# Add knowledge with uncertainty
agent.add_knowledge("concept", "Uncertain Concept", 
                   truth_value={"strength": 0.7, "confidence": 0.5})

# Reasoning propagates uncertainty
inferences = agent.reasoning_engine.forward_chain()
for inf in inferences:
    print(f"Inferred with confidence: {inf.confidence}")
```

## Best Practices

1. **Incremental Knowledge Building**: Start with core concepts, add relationships gradually
2. **Truth Value Management**: Use appropriate strength/confidence for uncertain information
3. **Regular Reasoning**: Run inference after significant knowledge additions
4. **Validation**: Periodically check for logical consistency
5. **Knowledge Persistence**: Save valuable knowledge bases for reuse
6. **Performance Monitoring**: Monitor atom count and reasoning complexity

## Troubleshooting

### Common Issues

1. **Missing Dependencies**: Ensure pydantic, loguru are installed
2. **Import Errors**: Check Python path includes project root
3. **Memory Usage**: Large knowledge bases may require optimization
4. **Circular References**: Use validation to detect logical inconsistencies

### Debug Mode

```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check cognitive system status
status = agent.get_cognitive_status()
print(f"AtomSpace size: {status['total_atoms']}")
print(f"Reasoning rules: {status['reasoning_rules']}")
```

## Integration with OpenManus

The OpenCog integration seamlessly works with other OpenManus components:

- **Tool System**: OpenCog tools work alongside other agent tools
- **Agent Framework**: Cognitive agent extends standard ToolCallAgent
- **Logging**: Integrated with OpenManus logging system
- **Configuration**: Uses OpenManus configuration patterns

This provides a powerful combination of symbolic AI reasoning with the flexibility and extensibility of the OpenManus agent framework.