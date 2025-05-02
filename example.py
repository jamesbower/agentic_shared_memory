#!/usr/bin/env python3
"""
Example script demonstrating how to use the MemoryGraph with Agno agents.
This file shows practical usage patterns for the A-MEM system.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import the MemoryGraph class from main.py
from main import MemoryGraph

# Import Agno components
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.openai import OpenAIChat
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.lancedb import LanceDb
from agno.embedder.openai import OpenAIEmbedder

def print_separator(title):
    """Print a separator with a title for better readability."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def main():
    print_separator("A-MEM SYSTEM EXAMPLE")
    
    # Step 1: Initialize the Memory Graph
    print("Initializing memory graph...")
    memory_graph = MemoryGraph(
        vector_db=LanceDb(
            uri="data/example-mem.db",
            table_name="example_knowledge_nodes",
            embedder=OpenAIEmbedder(id="text-embedding-3-small")
        ),
        llm=OpenAIChat(id="gpt-4o")
    )
    print("Memory graph initialized successfully")
    
    # Step 2: Configure an Agent with the Memory Graph
    print_separator("AGENT CONFIGURATION")
    print("Configuring research agent...")
    
    research_agent = Agent(
        name="Research Specialist",
        model=OpenAIChat(id="gpt-4o"),
        tools=[DuckDuckGoTools()],
        knowledge=PDFKnowledgeBase(
            path="./Graph-SIEM.pdf",  # Using the arXiv paper
            vector_db=memory_graph.vector_db
        ),
        memory=memory_graph.create_agent_memory(
            user_memory=True,
            session_summary=True
        ),
        instructions=[
            "Generate atomic notes for key concepts",
            "Auto-link new findings to existing knowledge",
            "Update related nodes during memory storage"
        ]
    )
    print("Research agent configured successfully")
    
    # Step 3: Process Knowledge (Optional)
    print_separator("KNOWLEDGE PROCESSING")
    print("Do you want to process the PDF knowledge? (y/n)")
    choice = input().lower()
    
    if choice == 'y':
        print("Processing PDF knowledge...")
        research_agent.knowledge.load()
        print("Knowledge processing completed")
    else:
        print("Skipping knowledge processing")
    
    # Step 4: Run Queries with the Agent
    print_separator("AGENT QUERIES")
    print("Running query: 'How is predictive analysis used in this case?'")
    
    response = research_agent.run(
        "Explain how A-MEM handles conflicting information",
        context={
            "memory_strategy": "versioned_updates",
            "confidence_threshold": 0.85
        }
    )
    
    print("\nAgent Response:")
    print(response)
    
    # Step 5: Process Document Chunks in Parallel
    print_separator("PARALLEL DOCUMENT PROCESSING")
    print("Processing document chunks in parallel...")
    
    document_chunks = [
        "A-MEM uses versioned nodes to handle conflicting information",
        "Knowledge nodes can be updated with new information while preserving history",
        "Confidence scores determine when to update existing information"
    ]
    
    print(f"Processing {len(document_chunks)} document chunks...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(research_agent.run, chunk) for chunk in document_chunks]
        for i, future in enumerate(futures):
            # Extract the content from RunResponse object
            result = future.result()
            result_text = result.content if hasattr(result, 'content') else str(result)
            # Print the first 50 characters
            print(f"Result for chunk {i+1}: {result_text[:50]}...")
    
    # Step 6: Inspect Memory Evolution
    print_separator("MEMORY INSPECTION")
    print("Inspecting recently updated nodes...")
    
    updated_nodes = memory_graph.query(
        "SELECT * FROM example_knowledge_nodes WHERE last_updated > NOW() - INTERVAL '1 hour'"
    )
    
    print(f"Found {len(updated_nodes)} recently updated nodes")
    if len(updated_nodes) > 0:
        print("\nSample node content:")
        for i, (_, row) in enumerate(updated_nodes.iterrows()):
            if i >= 3:  # Limit to 3 samples
                break
            print(f"Node {i+1}: {row.get('content', '')[:100]}...")
    
    # Step 7: Create Index for Efficient Search
    print_separator("MEMORY INDEXING")
    print("Creating vector index for efficient search...")
    
    # Check if we have enough data for IVF_PQ index (requires at least 256 rows)
    row_count = len(memory_graph.query("SELECT COUNT(*) FROM example_knowledge_nodes").iloc[0, 0])
    
    if row_count >= 256:
        try:
            memory_graph.create_index(
                index_type="IVF_PQ",  # Using ANN indices for LanceDB
                metric="cosine"
            )
            print("Vector index created successfully")
        except Exception as e:
            print(f"Error creating index: {e}")
            print("Continuing without index creation")
    else:
        print(f"Not enough data to create IVF_PQ index (requires 256 rows, but only {row_count} available)")
        print("Skipping index creation - this is normal for small datasets")
    
    print_separator("EXAMPLE COMPLETED")
    print("The A-MEM system example has been completed successfully.")
    print(f"Memory graph data is stored in: data/example-mem.db")

if __name__ == "__main__":
    main()