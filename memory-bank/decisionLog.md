# Decision Log

This file records architectural and implementation decisions using a list format.
2025-05-01 11:10:55 - Initial creation.
2025-05-01 11:21:46 - Updated with implementation decisions.
2025-05-01 11:53:52 - Updated with custom MemoryGraph implementation decision.
2025-05-01 13:13:00 - Performed memory bank update to ensure project context consistency.
2025-05-01 13:45:10 - Updated with code reorganization decisions.

## Decision

* Use Python 3.12 for the virtual environment (updated from Python 3.11)
* Implement memory graph using LanceDB for vector storage
* Use OpenAI embeddings for semantic representation
* Configure parallel processing for document handling
* Implement custom MemoryGraph class instead of using a built-in solution
* Use a schema-based approach for memory nodes with dynamic linking
* Separate implementation from examples in code organization
* Create simplified test implementation for testing without external dependencies

## Rationale

* Python 3.12 offers the latest performance improvements and features
* Compatible with all required dependencies in requirements.txt
* Python 3.12.7 is available on the system
* Chosen based on user preference
* LanceDB provides efficient vector storage and retrieval capabilities
* OpenAI embeddings offer high-quality semantic representation
* Parallel processing improves performance for large document batches
* Agno framework doesn't natively support memory graphs
* Custom MemoryGraph implementation allows for tailored functionality
* LanceDB's flexible schema and vector search capabilities enable efficient dynamic linking
* Schema-based approach provides structure for memory nodes and relationships

## Implementation Details

* Virtual environment will be created in a .venv directory
* All dependencies will be installed from requirements.txt
* Implementation plan documented in venv_setup_plan.md
* Memory graph initialized with LanceDB backend and OpenAI embeddings
* Agent configuration includes memory integration and knowledge base
* Performance optimization includes parallel execution and HNSW indexing
* Custom MemoryGraph class implements:
  * Node creation and retrieval
  * Dynamic linking between semantically similar nodes
  * Graph traversal with depth control
  * Versioning for handling conflicting information
  * SQL-like querying capabilities
  * Compatibility with Agno agents
* Code organization follows separation of concerns:
  * main.py: Core MemoryGraph class implementation
  * example.py: Example usage with agent configuration
  * test_memory_graph.py: Testing with LanceDB integration
  * simple_test.py: Simplified testing with in-memory storage
* Simplified test implementation uses:
  * In-memory storage instead of LanceDB
  * Mock embeddings with deterministic generation
  * Same API interface as the main implementation