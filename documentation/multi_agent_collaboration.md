# Multi-Agent Collaboration with Shared Memory

## Overview

Multi-agent collaboration is a powerful feature of the Agno framework that allows multiple specialized agents to share a common memory graph. This enables true collaborative intelligence where agents can build on each other's findings, update shared knowledge, and retrieve context-aware information.

## Key Concepts

### Shared Memory Architecture

The foundation of multi-agent collaboration is a shared `MemoryGraph` instance that serves as the central knowledge repository:

```python
# Initialize shared memory graph
memory_graph = MemoryGraph(
    vector_db=LanceDb(
        uri="shared-memory.db",
        table_name="knowledge_nodes",
        embedder=OpenAIEmbedder(id="text-embedding-3-small")
    ),
    llm=OpenAIChat(id="gpt-4o")
)
```

### Agent Memory Allocation

Each agent receives its own memory interface to the shared graph, allowing for agent-specific memory operations while maintaining the shared knowledge base:

```python
# Create agent-specific memory interfaces
research_agent_memory = memory_graph.create_agent_memory(
    user_memory=True,
    session_summary=True,
    agent_id="research_agent"
)

synthesis_agent_memory = memory_graph.create_agent_memory(
    user_memory=True,
    session_summary=True,
    agent_id="synthesis_agent"
)
```

## Implementation Patterns

### Specialized Agent Teams

Create teams of specialized agents that collaborate on complex tasks:

```python
# Research Agent - Discovers and extracts information
research_agent = Agent(
    name="Research Specialist",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGoTools()],
    knowledge=PDFUrlKnowledgeBase(
        urls=["https://arxiv.org/pdf/2502.12110.pdf"],
        vector_db=memory_graph.vector_db
    ),
    memory=memory_graph.create_agent_memory(
        user_memory=True,
        session_summary=True,
        agent_id="research_agent"
    ),
    instructions=[
        "Generate atomic notes for key concepts",
        "Auto-link new findings to existing knowledge"
    ]
)

# Synthesis Agent - Connects and integrates information
synthesis_agent = Agent(
    name="Knowledge Synthesizer",
    model=OpenAIChat(id="gpt-4o"),
    memory=memory_graph.create_agent_memory(
        user_memory=True,
        session_summary=True,
        agent_id="synthesis_agent"
    ),
    instructions=[
        "Identify patterns across research findings",
        "Create higher-order knowledge structures",
        "Resolve conflicts in knowledge representation"
    ]
)

# Reporting Agent - Communicates findings
reporting_agent = Agent(
    name="Information Reporter",
    model=OpenAIChat(id="gpt-4o"),
    memory=memory_graph.create_agent_memory(
        user_memory=True,
        session_summary=True,
        agent_id="reporting_agent"
    ),
    instructions=[
        "Summarize key findings from the memory graph",
        "Adapt explanations to user's context and questions",
        "Highlight confidence levels in reported information"
    ]
)
```

### Collaborative Workflows

Implement sequential or parallel workflows where agents build on each other's work:

```python
# Sequential workflow example
def collaborative_research(query, context=None):
    # Step 1: Research agent gathers information
    research_result = research_agent.run(
        f"Research information about: {query}",
        context=context
    )
    
    # Step 2: Synthesis agent integrates findings
    synthesis_result = synthesis_agent.run(
        f"Synthesize research findings about: {query}",
        context=context
    )
    
    # Step 3: Reporting agent creates final output
    final_report = reporting_agent.run(
        f"Create a comprehensive report about: {query}",
        context=context
    )
    
    return final_report

# Parallel workflow with executor
def parallel_collaborative_research(query, context=None):
    with ParallelExecutor(max_workers=3) as executor:
        # Submit research tasks to be executed in parallel
        research_future = executor.submit(
            research_agent.run,
            f"Research factual information about: {query}",
            context=context
        )
        
        analysis_future = executor.submit(
            research_agent.run,
            f"Research analytical perspectives on: {query}",
            context=context
        )
        
        # Wait for research to complete
        research_result = research_future.result()
        analysis_result = analysis_future.result()
        
        # Synthesize the findings
        synthesis_result = synthesis_agent.run(
            f"Synthesize research and analysis about: {query}",
            context=context
        )
        
        # Create final report
        final_report = reporting_agent.run(
            f"Create a comprehensive report about: {query}",
            context=context
        )
        
    return final_report
```

## Memory Synchronization

### Automatic Synchronization

The shared memory graph automatically synchronizes knowledge between agents:

```python
# Agent 1 adds knowledge
research_agent.run("Research quantum computing algorithms")

# Agent 2 can access this knowledge without explicit transfer
synthesis_agent.run("Synthesize information about quantum computing algorithms")
```

### Manual Memory Operations

Explicitly manage memory operations when needed:

```python
# Force memory synchronization
memory_graph.sync()

# Update specific nodes
memory_graph.update_node(
    node_id="concept:quantum_computing",
    content="Updated definition of quantum computing",
    metadata={
        "confidence": 0.95,
        "last_updated": datetime.now(),
        "source": "research_agent"
    }
)

# Create relationships between nodes
memory_graph.create_relationship(
    source_id="concept:quantum_computing",
    target_id="concept:quantum_algorithms",
    relationship_type="CONTAINS",
    metadata={
        "confidence": 0.9,
        "created_by": "synthesis_agent"
    }
)
```

## Conflict Resolution

### Version Control

Implement version control for knowledge nodes to track changes and resolve conflicts:

```python
# Enable versioning for the memory graph
memory_graph.enable_versioning(
    version_table="versioned_nodes",
    conflict_resolution="latest_confidence"
)

# Retrieve version history for a node
versions = memory_graph.get_node_versions("concept:quantum_computing")

# Restore previous version if needed
memory_graph.restore_node_version(
    node_id="concept:quantum_computing",
    version_id="v2"
)
```

### Conflict Resolution Strategies

Configure how conflicts between agents are resolved:

```python
# Configure conflict resolution strategy
memory_graph.set_conflict_resolution(
    strategy="confidence_weighted",
    confidence_threshold=0.8,
    recency_weight=0.7
)
```

Available strategies:
- `latest_update`: Use the most recent update
- `highest_confidence`: Use the update with highest confidence score
- `confidence_weighted`: Weighted combination based on confidence
- `agent_priority`: Prioritize updates from specific agents
- `consensus`: Require multiple agents to agree on changes

## Best Practices

1. **Agent Specialization**: Design agents with clear, specialized roles to maximize collaborative efficiency.

2. **Memory Partitioning**: Use agent_id and namespace parameters to partition the memory graph when appropriate:
   ```python
   agent_memory = memory_graph.create_agent_memory(
       agent_id="research_agent",
       namespace="project_alpha"
   )
   ```

3. **Confidence Scoring**: Implement consistent confidence scoring across agents:
   ```python
   memory_graph.store(
       content="Quantum computers use qubits instead of classical bits",
       metadata={
           "confidence": calculate_confidence(source, recency, verification),
           "source": "research_paper_analysis"
       }
   )
   ```

4. **Regular Synchronization**: Schedule periodic synchronization for long-running multi-agent systems:
   ```python
   # Set up automatic synchronization
   memory_graph.schedule_sync(interval_seconds=300)
   ```

5. **Monitoring**: Implement monitoring to track agent contributions and memory evolution:
   ```python
   # Enable monitoring
   memory_graph.enable_monitoring(
       metrics=["node_updates", "agent_contributions", "conflict_rate"],
       log_file="memory_collaboration.log"
   )
   
   # Generate collaboration report
   report = memory_graph.generate_collaboration_report(
       start_time=datetime(2025, 4, 1),
       end_time=datetime(2025, 4, 29)
   )
   ```

## Advanced Techniques

### Cross-Agent Learning

Enable agents to learn from each other's interactions:

```python
# Configure cross-agent learning
memory_graph.enable_cross_agent_learning(
    source_agents=["research_agent", "synthesis_agent"],
    target_agents=["reporting_agent"],
    learning_rate=0.3
)
```

### Dynamic Team Formation

Implement dynamic team formation based on task requirements:

```python
def form_agent_team(task_description):
    # Analyze task requirements
    task_analysis = meta_agent.run(f"Analyze requirements for: {task_description}")
    
    # Determine required agent specializations
    required_specializations = extract_specializations(task_analysis)
    
    # Create team with appropriate agents
    team = AgentTeam()
    for specialization in required_specializations:
        agent = create_specialized_agent(
            specialization=specialization,
            memory_graph=memory_graph
        )
        team.add_agent(agent)
    
    return team
```

## Troubleshooting

### Common Issues and Solutions

1. **Memory Contention**
   - Issue: Multiple agents attempting to update the same nodes simultaneously
   - Solution: Implement locking mechanisms or use the versioning system

2. **Knowledge Fragmentation**
   - Issue: Related information stored in disconnected nodes
   - Solution: Schedule periodic consolidation tasks with the synthesis agent

3. **Conflicting Information**
   - Issue: Agents storing contradictory information
   - Solution: Use confidence scoring and implement consensus mechanisms

4. **Memory Graph Overload**
   - Issue: Too many nodes affecting retrieval performance
   - Solution: Implement pruning strategies and node expiration policies

## Case Studies

### Research Team Simulation

A simulated research team consisting of:
- Literature Review Agent
- Experiment Design Agent
- Data Analysis Agent
- Paper Writing Agent

All agents share the same memory graph, allowing seamless collaboration where the Paper Writing Agent can access experimental results and literature context without explicit knowledge transfer.

### Customer Support System

A multi-agent customer support system with:
- Query Classification Agent
- Knowledge Retrieval Agent
- Response Generation Agent
- Feedback Processing Agent

The shared memory allows the system to learn from customer interactions and continuously improve response quality across all agents.