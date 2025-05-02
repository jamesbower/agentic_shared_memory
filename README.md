# Agentic Shared Memory Documentation

Welcome to the Agentic Shared Memory documentation. This repository contains comprehensive documentation for implementing and optimizing the A-MEM (Associative Memory) system utilizing both vector and graph memory for dynamic memory organization.

## Memory Graph Architecture

The A-MEM system implements a memory graph architecture with the following components:

### Core Components

- **Memory Nodes**: Atomic units of knowledge with content, embeddings, and metadata
- **Dynamic Links**: Bidirectional connections between semantically related nodes
- **Vector Database**: LanceDB for efficient vector storage and similarity search
- **Embedding Generation**: OpenAI embeddings for semantic representation
- **Graph Traversal**: Methods for exploring connected knowledge nodes
- **Versioning**: Support for handling conflicting information and knowledge evolution

## Key Implementation Features

The A-MEM system is built on several key implementation features that enable its functionality:

| A-MEM Requirement | Implementation |
|-------------------|---------------|
| **Atomic Note Creation** | Text chunking + metadata extraction |
| **Dynamic Linking** | Hybrid search (vector + semantic analysis) |
| **Continuous Evolution** | memory_graph.update_node() API |
| **Context-Aware Retrieval** | memory_graph.retrieve(context=...) |

### Key Advantages

- **Zettelkasten-Scale Performance**: Handles 10k+ notes with <100ms query latency
- **Dynamic Context Handling**: Automatically injects relevant memories into prompts
- **Multi-Agent Sync**: Shared memory graph enables team collaboration
- **Continuous Learning**: Daily automatic node reindexing

### Implementation Considerations

- Use Agno's monitoring=True flag to track memory graph metrics
- Implement conflict resolution with versioned_nodes table
- Schedule periodic memory_graph.optimize() calls for large datasets
- For multi-agent collaboration, instantiate multiple agents all referencing the same memory_graph

This implementation demonstrates how Agno's modular architecture and performance characteristics make it ideal for building A-MEM systems that require dynamic knowledge organization and efficient retrieval.

## Getting Started

To get started with Agno Shared Memory:

1. Clone this repository and set up your environment:
   ```bash
   # Create a Python 3.12 virtual environment
   python3.12 -m venv .venv
   
   # Activate the virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. Examine the [Memory Workflow](./documentation/memory_workflow.md) to understand how information flows through the system

3. Run the example script to see the memory graph in action:
   ```bash
   python3 example.py
   ```

4. Explore the implementation in main.py to understand how the MemoryGraph class works

5. For advanced use cases, refer to the specialized documentation:
   - [Multi-Agent Collaboration](./documentation/multi_agent_collaboration.md) for building collaborative agent systems
   - [Memory Graph Optimization](./documentation/memory_graph_optimization.md) for scaling and performance tuning
   - [LanceDB Implementation](./documentation/lancedb_implementation.md) for implementing memory graphs with LanceDB

## Implementation Examples

The project is organized into several key files:

- **main.py**: Core implementation of the MemoryGraph class
- **example.py**: Example code demonstrating how to use the MemoryGraph with Agno agents
- **test_memory_graph.py**: Test script for the MemoryGraph implementation with LanceDB
- **simple_test.py**: Simplified test implementation using in-memory storage

### Running the Examples

To run the example code:

```bash
python3 example.py
```

This will demonstrate:
- Initializing a memory graph with LanceDB
- Configuring an agent with shared memory
- Processing documents and storing knowledge
- Querying with memory integration
- Performance optimization techniques

### Implementation Details

- **Node Schema**:
  - Content: The actual knowledge or information
  - Embedding: Vector representation for semantic similarity
  - Links: Connections to related nodes
  - Link Scores: Similarity scores for each connection
  - Tags: Categorical metadata for organization
  - Version: For tracking updates and changes
  - Timestamps: Creation and update times

- **Key Operations**:
  - Node Creation: Adding new knowledge to the graph
  - Dynamic Linking: Automatically connecting related information
  - Semantic Search: Finding relevant information based on meaning
  - Graph Traversal: Exploring connected knowledge
  - Knowledge Updates: Evolving information over time

## Key Features

- **Atomic Note Creation**: Generate discrete knowledge units from various sources
- **Dynamic Linking**: Automatically connect related information
- **Continuous Evolution**: Update and refine knowledge over time
- **Context-Aware Retrieval**: Retrieve information based on contextual relevance
- **Multi-Agent Collaboration**: Enable multiple agents to share and build upon knowledge
- **Performance Optimization**: Scale to handle large knowledge bases efficiently

## Best Practices

For detailed best practices, refer to the specialized documentation files:

- [Multi-Agent Collaboration](./documentation/multi_agent_collaboration.md#best-practices) includes best practices for agent specialization, memory partitioning, and collaboration workflows
- [Memory Graph Optimization](./documentation/memory_graph_optimization.md#best-practices) includes best practices for performance tuning, maintenance, and scaling strategies
- [LanceDB Implementation](./documentation/lancedb_implementation.md#best-practices-for-lancedb-memory-graphs) includes best practices for implementing memory graphs with LanceDB

## Advanced Use Cases

- **Research Knowledge Management**: Organize and synthesize information from research papers
- **Customer Support Systems**: Build collaborative agent teams for customer interactions
- **Content Creation**: Develop systems that can collaboratively generate and refine content
- **Decision Support**: Create memory-augmented systems for complex decision-making
- **Knowledge Evolution**: Track how information changes and evolves over time
- **Multi-Agent Memory**: Enable multiple specialized agents to share and build upon knowledge
- **Semantic Knowledge Graphs**: Build rich knowledge representations with dynamic relationships
- **Continuous Learning Systems**: Develop systems that learn and improve over time

## Resources
[A-MEM: Agentic Memory for LLM Agents](https://arxiv.org/abs/2502.12110)
[Agentic Memory(A-MEM): Long-Term Knowledge Management for LLM Agents](https://levelup.gitconnected.com/agentic-memory-a-mem-long-term-knowledge-management-for-llm-agents-af06b5df48dc)

## Contributing

To contribute to this documentation:

1. Fork the repository
2. Make your changes
3. Submit a pull request with a clear description of your improvements