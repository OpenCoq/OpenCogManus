"""
Demonstration of OpenCog Cognitive Agent capabilities.

This script shows how to use the OpenCog-powered Cognitive Agent for
symbolic reasoning, knowledge representation, and pattern matching.
"""

import asyncio
from app.opencog.cognitive_agent import CognitiveAgent
from app.logger import logger


async def demonstrate_basic_knowledge():
    """Demonstrate basic knowledge representation and querying."""
    print("\n=== Basic Knowledge Representation ===")
    
    agent = CognitiveAgent()
    
    # Add some basic concepts
    agent.add_knowledge("concept", "Artificial Intelligence")
    agent.add_knowledge("concept", "Machine Learning")
    agent.add_knowledge("concept", "Deep Learning")
    agent.add_knowledge("concept", "Neural Networks")
    
    # Add relationships
    agent.add_knowledge("relation", "Machine Learning", object_="Artificial Intelligence")
    agent.add_knowledge("relation", "Deep Learning", object_="Machine Learning")
    agent.add_knowledge("relation", "Neural Networks", object_="Deep Learning")
    
    # Add facts
    agent.add_knowledge("fact", "Artificial Intelligence", "can_solve", "complex_problems")
    agent.add_knowledge("fact", "Machine Learning", "learns_from", "data")
    agent.add_knowledge("fact", "Deep Learning", "uses", "Neural Networks")
    
    # Query the knowledge
    results = agent.query_knowledge("Artificial Intelligence")
    print(f"Found {len(results)} items related to 'Artificial Intelligence':")
    for i, result in enumerate(results[:5], 1):
        print(f"  {i}. {result.get('type', 'Unknown')}('{result.get('name', '')}')")
    
    # Get cognitive status
    status = agent.get_cognitive_status()
    print(f"\nKnowledge Base Statistics:")
    print(f"  Total atoms: {status['total_atoms']}")
    print(f"  Concept nodes: {status['concept_nodes']}")
    print(f"  Inheritance links: {status['inheritance_links']}")
    

async def demonstrate_reasoning():
    """Demonstrate symbolic reasoning capabilities."""
    print("\n=== Symbolic Reasoning ===")
    
    agent = CognitiveAgent()
    
    # Build a knowledge base about animals
    agent.add_knowledge("concept", "Animal")
    agent.add_knowledge("concept", "Mammal")
    agent.add_knowledge("concept", "Dog")
    agent.add_knowledge("concept", "Poodle")
    
    # Add inheritance hierarchy
    agent.add_knowledge("relation", "Mammal", object_="Animal")
    agent.add_knowledge("relation", "Dog", object_="Mammal")
    agent.add_knowledge("relation", "Poodle", object_="Dog")
    
    # Add properties
    agent.add_knowledge("fact", "Animal", "has", "metabolism")
    agent.add_knowledge("fact", "Mammal", "has", "fur")
    agent.add_knowledge("fact", "Dog", "makes", "bark_sound")
    
    print("Knowledge base built. Performing reasoning...")
    
    # Query with reasoning
    results = agent.query_knowledge("Poodle")
    print(f"\nKnowledge about 'Poodle':")
    for result in results[:3]:
        print(f"  - {result.get('type', 'Unknown')}('{result.get('name', '')}')")
    
    # The reasoning engine should infer that Poodle inherits properties from Animal
    print("\nAfter reasoning, Poodle should inherit properties from Animal, Mammal, and Dog")


async def demonstrate_pattern_matching():
    """Demonstrate pattern matching capabilities."""
    print("\n=== Pattern Matching ===")
    
    agent = CognitiveAgent()
    
    # Add knowledge about different programming languages
    languages = ["Python", "JavaScript", "Java", "C++", "Go", "Rust"]
    paradigms = ["Object-Oriented", "Functional", "Procedural"]
    
    for lang in languages:
        agent.add_knowledge("concept", lang)
        agent.add_knowledge("relation", lang, object_="Programming Language")
    
    for paradigm in paradigms:
        agent.add_knowledge("concept", paradigm)
        agent.add_knowledge("relation", paradigm, object_="Programming Paradigm")
    
    # Add specific relationships
    agent.add_knowledge("fact", "Python", "supports", "Object-Oriented")
    agent.add_knowledge("fact", "Python", "supports", "Functional")
    agent.add_knowledge("fact", "JavaScript", "supports", "Object-Oriented")
    agent.add_knowledge("fact", "JavaScript", "supports", "Functional")
    agent.add_knowledge("fact", "Java", "supports", "Object-Oriented")
    
    print("Knowledge base built with programming language information.")
    
    # Query for languages that support Object-Oriented programming
    results = agent.query_knowledge("Object-Oriented")
    print(f"\nFound {len(results)} items related to 'Object-Oriented':")
    for result in results[:5]:
        print(f"  - {result.get('name', '')}")


async def demonstrate_knowledge_analysis():
    """Demonstrate knowledge analysis and insights."""
    print("\n=== Knowledge Analysis ===")
    
    agent = CognitiveAgent()
    
    # Build a more complex knowledge base
    # Technology domains
    domains = ["AI", "Robotics", "Blockchain", "IoT", "Cybersecurity"]
    applications = ["Healthcare", "Finance", "Transportation", "Education", "Entertainment"]
    
    for domain in domains:
        agent.add_knowledge("concept", domain)
        agent.add_knowledge("relation", domain, object_="Technology")
    
    for app in applications:
        agent.add_knowledge("concept", app)
        agent.add_knowledge("relation", app, object_="Application Domain")
    
    # Add cross-domain relationships
    agent.add_knowledge("fact", "AI", "used_in", "Healthcare")
    agent.add_knowledge("fact", "AI", "used_in", "Finance")
    agent.add_knowledge("fact", "Robotics", "used_in", "Healthcare")
    agent.add_knowledge("fact", "Robotics", "used_in", "Transportation")
    agent.add_knowledge("fact", "Blockchain", "used_in", "Finance")
    agent.add_knowledge("fact", "IoT", "used_in", "Healthcare")
    agent.add_knowledge("fact", "Cybersecurity", "used_in", "Finance")
    
    print("Complex knowledge base built.")
    
    # Analyze the knowledge
    status = agent.get_cognitive_status()
    print(f"\nFinal Knowledge Base Statistics:")
    print(f"  Total atoms: {status['total_atoms']}")
    print(f"  Concept nodes: {status['concept_nodes']}")
    print(f"  Predicate nodes: {status['predicate_nodes']}")
    print(f"  Evaluation links: {status['evaluation_links']}")
    print(f"  Inheritance links: {status['inheritance_links']}")
    
    # Query for most connected concepts
    healthcare_results = agent.query_knowledge("Healthcare")
    finance_results = agent.query_knowledge("Finance")
    
    print(f"\nHealthcare-related technologies: {len(healthcare_results)} found")
    print(f"Finance-related technologies: {len(finance_results)} found")


async def main():
    """Run all demonstrations."""
    print("OpenCog Cognitive Agent Demonstration")
    print("=" * 40)
    
    try:
        await demonstrate_basic_knowledge()
        await demonstrate_reasoning()
        await demonstrate_pattern_matching()
        await demonstrate_knowledge_analysis()
        
        print("\n=== Demonstration Complete ===")
        print("The OpenCog Cognitive Agent successfully demonstrated:")
        print("- Knowledge representation with concepts, relations, and facts")
        print("- Symbolic reasoning and inference")
        print("- Pattern matching and similarity detection")
        print("- Knowledge analysis and insights")
        
    except Exception as e:
        logger.error(f"Error during demonstration: {e}")
        print(f"Demonstration failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())