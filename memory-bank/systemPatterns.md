# System Patterns

This file documents recurring patterns and standards used in the project.
It is optional, but recommended to be updated as the project evolves.
2025-05-01 11:11:25 - Initial creation.
2025-05-01 11:22:02 - Updated with implementation patterns.
2025-05-01 11:54:22 - Updated with custom MemoryGraph patterns.

## Coding Patterns

* Virtual environment setup follows standard Python venv practices
* Dependencies are managed through requirements.txt
* Agent configuration follows a consistent pattern with model, tools, knowledge, and memory components
* Memory graph operations use a fluent API style
* Custom class implementation with comprehensive docstrings
* Method chaining for database operations
* Consistent error handling and validation

## Architectural Patterns

* Custom MemoryGraph implementation using LanceDB for vector storage
* Schema-based approach for memory nodes with dynamic linking
* Bidirectional linking between semantically similar nodes
* Graph traversal using breadth-first search
* OpenAI embeddings for semantic representation
* Agent-based design with specialized roles
* Shared memory graph for multi-agent collaboration
* Parallel execution for performance optimization
* HNSW indexing for efficient vector search

## Memory Graph Patterns

* Atomic note storage with metadata
* Dynamic linking between semantically similar nodes
* Link representation using embedded arrays in metadata
* Hybrid search combining vector similarity with SQL filters
* Version control for non-destructive updates
* Bidirectional links for comprehensive traversal
* Depth-limited graph traversal for performance
* Threshold-based link creation for relevance control

## Testing Patterns

* Not yet defined

## Performance Optimization Patterns

* Parallel document processing using ParallelExecutor
* HNSW indexing for efficient similarity search
* Configurable confidence thresholds for memory retrieval
* Versioned updates for handling conflicting information
* Batch processing for document chunks
* Efficient graph traversal with depth limits
* Link caching for frequently accessed connections