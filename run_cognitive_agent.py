"""
Run script for OpenCog Cognitive Agent.

This script demonstrates how to run the OpenCog-powered Cognitive Agent
with symbolic reasoning capabilities.
"""

import argparse
import asyncio
from app.opencog.cognitive_agent import CognitiveAgent
from app.logger import logger


async def main():
    """Main function to run the Cognitive Agent."""
    parser = argparse.ArgumentParser(description="Run OpenCog Cognitive Agent")
    parser.add_argument(
        "--prompt", 
        type=str, 
        required=False, 
        help="Input prompt for the agent"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demonstration of OpenCog capabilities"
    )
    parser.add_argument(
        "--persist-knowledge",
        action="store_true",
        help="Persist knowledge between sessions"
    )
    parser.add_argument(
        "--load-knowledge",
        type=str,
        help="Load knowledge from file"
    )
    parser.add_argument(
        "--save-knowledge",
        type=str,
        help="Save knowledge to file"
    )
    
    args = parser.parse_args()
    
    # Create Cognitive Agent
    agent_config = {
        "knowledge_persistence": args.persist_knowledge,
        "enable_auto_reasoning": True,
        "max_reasoning_iterations": 5
    }
    
    agent = CognitiveAgent(**agent_config)
    
    try:
        # Load knowledge if specified
        if args.load_knowledge:
            success = agent.load_knowledge(args.load_knowledge)
            if success:
                logger.info(f"Loaded knowledge from {args.load_knowledge}")
            else:
                logger.warning(f"Failed to load knowledge from {args.load_knowledge}")
        
        # Run demonstration if requested
        if args.demo:
            await run_demonstration(agent)
            return
        
        # Handle prompt input
        if args.prompt:
            prompt = args.prompt
        else:
            prompt = input("Enter your prompt for the Cognitive Agent: ")
        
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return
        
        # Add some initial context about OpenCog capabilities
        context_prompt = f"""
        I am a Cognitive Agent with OpenCog symbolic AI capabilities including:
        - Knowledge representation using AtomSpace
        - Symbolic reasoning with forward/backward chaining
        - Advanced pattern matching and similarity detection
        - Truth value-based uncertain reasoning
        
        User request: {prompt}
        """
        
        logger.info("Processing request with symbolic AI capabilities...")
        await agent.run(context_prompt)
        
        # Save knowledge if specified
        if args.save_knowledge:
            success = agent.save_knowledge(args.save_knowledge)
            if success:
                logger.info(f"Saved knowledge to {args.save_knowledge}")
            else:
                logger.warning(f"Failed to save knowledge to {args.save_knowledge}")
        
        logger.info("Request processing completed.")
        
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    except Exception as e:
        logger.error(f"Error running Cognitive Agent: {e}")
    finally:
        await agent.cleanup()


async def run_demonstration(agent):
    """Run a demonstration of OpenCog capabilities."""
    print("OpenCog Cognitive Agent Demonstration")
    print("=" * 40)
    
    # Build knowledge base
    print("\n1. Building Knowledge Base...")
    agent.add_knowledge("concept", "Artificial Intelligence")
    agent.add_knowledge("concept", "Machine Learning") 
    agent.add_knowledge("concept", "Neural Networks")
    agent.add_knowledge("concept", "Deep Learning")
    
    agent.add_knowledge("relation", "Machine Learning", object_="Artificial Intelligence")
    agent.add_knowledge("relation", "Deep Learning", object_="Machine Learning")
    agent.add_knowledge("relation", "Neural Networks", object_="Deep Learning")
    
    agent.add_knowledge("fact", "Neural Networks", "inspired_by", "biological_neurons")
    agent.add_knowledge("fact", "Deep Learning", "uses", "multiple_layers")
    agent.add_knowledge("fact", "Machine Learning", "learns_from", "data")
    
    # Query knowledge
    print("\n2. Querying Knowledge...")
    results = agent.query_knowledge("Artificial Intelligence")
    print(f"Found {len(results)} items related to 'Artificial Intelligence'")
    for i, result in enumerate(results[:3], 1):
        print(f"  {i}. {result.get('type', 'Unknown')}('{result.get('name', '')}')")
    
    # Show reasoning
    print("\n3. Symbolic Reasoning...")
    await agent._perform_cognitive_reasoning()
    
    # Get insights
    print("\n4. Knowledge Analysis...")
    status = agent.get_cognitive_status()
    print(f"Knowledge Base contains:")
    print(f"  - {status['concept_nodes']} concepts")
    print(f"  - {status['inheritance_links']} inheritance relationships")
    print(f"  - {status['evaluation_links']} facts")
    print(f"  - {status['reasoning_rules']} reasoning rules")
    
    # Demonstrate tool usage
    print("\n5. Using Cognitive Tools...")
    
    demo_prompt = """
    Using my OpenCog capabilities, let me analyze the knowledge about AI:
    
    First, let me query the AtomSpace for AI-related concepts:
    """
    
    await agent.run(demo_prompt)
    
    print("\n=== Demonstration Complete ===")
    print("Successfully demonstrated OpenCog symbolic AI capabilities!")


if __name__ == "__main__":
    asyncio.run(main())