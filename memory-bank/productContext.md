# Product Context

This file provides a high-level overview of the project and the expected product that will be created. Initially it is based upon projectBrief.md (if provided) and all other available project-related information in the working directory. This file is intended to be updated as the project evolves, and should be used to inform all other modes of the project's goals and context.
2025-05-01 11:10:00 - Initial creation based on project files.

## Project Goal

* The Agno Shared Memory project aims to implement an associative memory (A-MEM) system using the Agno framework, enabling agents to create, link, and retrieve knowledge dynamically.

## Key Features

* **Atomic Note Creation**: Generate discrete knowledge units from various sources
* **Dynamic Linking**: Automatically connect related information
* **Continuous Evolution**: Update and refine knowledge over time
* **Context-Aware Retrieval**: Retrieve information based on contextual relevance
* **Multi-Agent Collaboration**: Enable multiple agents to share and build upon knowledge
* **Performance Optimization**: Scale to handle large knowledge bases efficiently

## Overall Architecture

* The system uses a memory graph structure implemented with LanceDB as the vector database
* OpenAI embeddings are used for semantic representation of knowledge
* The framework supports multiple specialized agents that can share and build upon the same memory graph
* The system includes components for document processing, knowledge extraction, and memory optimization