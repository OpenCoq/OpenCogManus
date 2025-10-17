"""
Configuration examples for OpenCog Cognitive Agent.

This file demonstrates various configuration options and setups for the
OpenCog-powered Cognitive Agent in different use cases.
"""

from typing import Dict, Any


def get_basic_config() -> Dict[str, Any]:
    """Basic configuration for general use."""
    return {
        "enable_auto_reasoning": True,
        "max_reasoning_iterations": 5,
        "knowledge_persistence": True
    }


def get_research_config() -> Dict[str, Any]:
    """Configuration optimized for research and analysis."""
    return {
        "enable_auto_reasoning": True,
        "max_reasoning_iterations": 10,
        "knowledge_persistence": True,
        # Additional tools for research
        "enable_pattern_analysis": True,
        "enable_knowledge_validation": True
    }


def get_educational_config() -> Dict[str, Any]:
    """Configuration for educational demonstrations."""
    return {
        "enable_auto_reasoning": True,
        "max_reasoning_iterations": 3,
        "knowledge_persistence": False,  # Fresh start each time
        "verbose_explanations": True
    }


def get_production_config() -> Dict[str, Any]:
    """Configuration for production environments."""
    return {
        "enable_auto_reasoning": True,
        "max_reasoning_iterations": 8,
        "knowledge_persistence": True,
        "performance_monitoring": True,
        "error_recovery": True
    }


# Example knowledge domains for initialization
SAMPLE_KNOWLEDGE_DOMAINS = {
    "artificial_intelligence": {
        "concepts": [
            "Artificial Intelligence",
            "Machine Learning", 
            "Deep Learning",
            "Neural Networks",
            "Natural Language Processing",
            "Computer Vision",
            "Robotics"
        ],
        "relationships": [
            ("Machine Learning", "Artificial Intelligence"),
            ("Deep Learning", "Machine Learning"),
            ("Neural Networks", "Deep Learning"),
            ("Natural Language Processing", "Artificial Intelligence"),
            ("Computer Vision", "Artificial Intelligence"),
            ("Robotics", "Artificial Intelligence")
        ],
        "facts": [
            ("Machine Learning", "learns_from", "data"),
            ("Neural Networks", "inspired_by", "biological_neurons"),
            ("Deep Learning", "uses", "multiple_layers"),
            ("Natural Language Processing", "processes", "human_language"),
            ("Computer Vision", "analyzes", "visual_data")
        ]
    },
    
    "science": {
        "concepts": [
            "Physics",
            "Chemistry", 
            "Biology",
            "Mathematics",
            "Quantum Mechanics",
            "Molecular Biology",
            "Genetics"
        ],
        "relationships": [
            ("Quantum Mechanics", "Physics"),
            ("Molecular Biology", "Biology"),
            ("Genetics", "Biology"),
            ("Mathematics", "Science")
        ],
        "facts": [
            ("Physics", "studies", "matter_and_energy"),
            ("Chemistry", "studies", "atoms_and_molecules"), 
            ("Biology", "studies", "living_organisms"),
            ("Mathematics", "provides", "logical_framework")
        ]
    }
}


def initialize_knowledge_domain(agent, domain_name: str):
    """
    Initialize agent with knowledge from a specific domain.
    
    Args:
        agent: CognitiveAgent instance
        domain_name: Name of domain from SAMPLE_KNOWLEDGE_DOMAINS
    """
    if domain_name not in SAMPLE_KNOWLEDGE_DOMAINS:
        raise ValueError(f"Unknown domain: {domain_name}")
    
    domain = SAMPLE_KNOWLEDGE_DOMAINS[domain_name]
    
    # Add concepts
    for concept in domain["concepts"]:
        agent.add_knowledge("concept", concept)
    
    # Add relationships  
    for child, parent in domain["relationships"]:
        agent.add_knowledge("relation", child, object_=parent)
    
    # Add facts
    for subject, predicate, object_ in domain["facts"]:
        agent.add_knowledge("fact", subject, predicate, object_)
    
    print(f"Initialized {domain_name} knowledge domain with:")
    print(f"  - {len(domain['concepts'])} concepts")
    print(f"  - {len(domain['relationships'])} relationships")
    print(f"  - {len(domain['facts'])} facts")


# Example usage patterns
USAGE_EXAMPLES = {
    "basic_qa": """
# Basic question answering setup
agent = CognitiveAgent(**get_basic_config())
initialize_knowledge_domain(agent, "artificial_intelligence")

# Ask questions about the domain
response = await agent.run("What is the relationship between Deep Learning and AI?")
""",

    "research_analysis": """
# Research analysis setup
agent = CognitiveAgent(**get_research_config())
initialize_knowledge_domain(agent, "science")

# Perform deep analysis
response = await agent.run("Analyze the interconnections between different science fields and suggest research opportunities")
""",

    "educational_demo": """
# Educational demonstration
agent = CognitiveAgent(**get_educational_config())
initialize_knowledge_domain(agent, "artificial_intelligence")

# Step-by-step learning
response = await agent.run("Teach me about AI by building up from basic concepts")
"""
}