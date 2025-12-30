"""
CLI interface for the Neo4j LangChain application.
Enhanced version of the original demo.py.
"""

import sys
from typing import Optional

from src.services.neo4j_service import neo4j_service
from src.services.qa_service import QAService, SAMPLE_QUESTIONS
from src.core.config import settings
from src.core.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def print_banner() -> None:
    """Print welcome banner."""
    print("\n" + "="*70)
    print(f"  🤖 {settings.app_name} v{settings.app_version} - CLI")
    print("="*70)
    print("\nAsk questions about projects, people, and technologies!")
    print("Commands: 'help' | 'info' | 'debug' | 'quit'\n")


def print_help() -> None:
    """Print sample questions."""
    print("\n📝 Sample Questions:\n")
    for i, question in enumerate(SAMPLE_QUESTIONS, 1):
        print(f"  {i}. {question}")
    print()


def run_interactive(show_cypher: bool = False) -> None:
    """Run interactive CLI mode."""
    try:
        # Connect to Neo4j
        print("\n🔌 Connecting to Neo4j...")
        graph = neo4j_service.connect()
        
        # Create QA service
        print(f"🧠 Initializing {settings.llm_provider.upper()} LLM...")
        qa_service = QAService(graph)
        
        print_banner()
        
        # Interactive loop
        while True:
            try:
                user_input = input("❓ Your question: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!\n")
                    break
                
                elif user_input.lower() == 'help':
                    print_help()
                    continue
                
                elif user_input.lower() == 'info':
                    schema = neo4j_service.verify_schema()
                    print("\n📊 Database Schema:")
                    print(f"  Nodes: {schema['total_nodes']}")
                    for label, count in schema['nodes'].items():
                        print(f"    - {label}: {count}")
                    print(f"  Relationships: {schema['total_relationships']}")
                    for rel_type, count in schema['relationships'].items():
                        print(f"    - {rel_type}: {count}")
                    print()
                    continue
                
                elif user_input.lower() == 'debug':
                    show_cypher = not show_cypher
                    status = "enabled" if show_cypher else "disabled"
                    print(f"\n🔧 Debug mode {status}\n")
                    continue
                
                # Process question
                print("\n⏳ Thinking...")
                result = qa_service.query(user_input, include_cypher=show_cypher)
                
                if show_cypher and result.get('cypher_query'):
                    print(f"\n🔍 Cypher Query:")
                    print(f"   {result['cypher_query']}")
                
                print(f"\n💡 Answer:\n{result['answer']}\n")
                print("-" * 70 + "\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!\n")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                print(f"\n❌ Error: {e}\n")
                continue
                
    except Exception as e:
        logger.error(f"Startup error: {e}")
        print(f"\n❌ Startup Error: {e}")
        print("\nMake sure:")
        print("  1. Docker is running (docker-compose up -d)")
        print("  2. .env file is configured")
        print("  3. Neo4j has data loaded\n")
        sys.exit(1)


def main() -> None:
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Test mode
        try:
            graph = neo4j_service.connect()
            schema = neo4j_service.verify_schema()
            print(f"✅ Connected! {schema['total_nodes']} nodes, {schema['total_relationships']} relationships")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            sys.exit(1)
    else:
        # Interactive mode
        run_interactive()


if __name__ == "__main__":
    main()
