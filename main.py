# Core Implementation Components
import os
import uuid
import pyarrow as pa
import numpy as np
from collections import deque
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.openai import OpenAIChat
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.vectordb.lancedb import LanceDb
from agno.embedder.openai import OpenAIEmbedder

# Custom MemoryGraph implementation using LanceDB
class MemoryGraph:
    def __init__(self, vector_db, llm):
        """
        Initialize a memory graph using LanceDB for vector storage and linking.
        
        Args:
            vector_db: LanceDB vector database instance
            llm: Language model for semantic analysis and link generation
        """
        self.vector_db = vector_db
        self.llm = llm
        self.table_name = vector_db.table_name
        self.uri = vector_db.uri
        
        # Define schema for memory nodes with dynamic linking
        self.schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("content", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), 1536)),
            pa.field("links", pa.list_(pa.string())),  # Array of linked node IDs
            pa.field("link_scores", pa.list_(pa.float32())),  # Similarity scores
            pa.field("tags", pa.list_(pa.string())),  # Tags for categorization
            pa.field("created_at", pa.timestamp('ms')),
            pa.field("last_updated", pa.timestamp('ms')),
            pa.field("version", pa.int32())  # For versioning
        ])
        
        # Initialize the table if it doesn't exist
        self._initialize_table()
    
    def _initialize_table(self):
        """Initialize the LanceDB table with the proper schema if it doesn't exist."""
        import lancedb
        db = lancedb.connect(self.uri)
        
        if self.table_name not in db.table_names():
            print(f"Creating new table with schema: {self.schema}")
            db.create_table(self.table_name, schema=self.schema)
            print(f"Created new memory graph table: {self.table_name}")
        else:
            # Check if the existing table has the expected schema
            table = db.open_table(self.table_name)
            print(f"Existing table schema: {table.schema}")
            print(f"Expected schema: {self.schema}")
            print("Note: Schema differences may cause issues. Consider using a new database.")
            
            # Check if we need to adapt to the existing schema
            if "vector" in str(table.schema) and "embedding" not in str(table.schema):
                print("Detected LanceDB default schema. Adapting to use 'vector' instead of 'embedding'.")
                # Update our schema field names to match LanceDB defaults
                self.schema = pa.schema([
                    pa.field("id", pa.string()),
                    pa.field("payload", pa.string()),  # Use payload instead of content
                    pa.field("vector", pa.list_(pa.float32(), 1536)),  # Use vector instead of embedding
                    # Other fields will be stored in the payload as JSON
                ])
    
    def add_node(self, content, tags=None, embedding=None):
        """
        Add a new node to the memory graph.
        
        Args:
            content: Text content of the node
            tags: List of tags for categorization
            embedding: Pre-computed embedding (if None, will be generated)
            
        Returns:
            node_id: ID of the created node
        """
        node_id = str(uuid.uuid4())
        
        # Generate embedding if not provided
        if embedding is None:
            # Use the correct method name for OpenAIEmbedder
            embedding = self.vector_db.embedder.get_embedding(content)
        
        # Ensure embedding is the right size
        if len(embedding) != 1536:
            print(f"Warning: Embedding size {len(embedding)} doesn't match schema (1536)")
            # Pad or truncate to match schema
            if len(embedding) < 1536:
                embedding = embedding + [0.0] * (1536 - len(embedding))
            else:
                embedding = embedding[:1536]
        
        # Ensure tags is a list
        if tags is None:
            tags = []
        elif not isinstance(tags, list):
            tags = [str(tags)]
        
        # Check if we're using the default LanceDB schema or our custom schema
        using_default_schema = "vector" in str(self.schema) and "embedding" not in str(self.schema)
        
        # Prepare node data based on schema
        if using_default_schema:
            # For default LanceDB schema (id, payload, vector)
            import json
            # Store all other fields as JSON in payload
            payload_data = {
                "content": content,
                "links": [],
                "link_scores": [],
                "tags": tags,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "version": 1
            }
            
            node_data = {
                "id": node_id,
                "payload": json.dumps(payload_data),
                "vector": embedding
            }
        else:
            # For our custom schema
            node_data = {
                "id": node_id,
                "content": content,
                "embedding": embedding,
                "links": [],
                "link_scores": [],
                "tags": tags,
                "created_at": datetime.now(),
                "last_updated": datetime.now(),
                "version": 1
            }
        
        # Add to LanceDB
        try:
            import lancedb
            db = lancedb.connect(self.uri)
            table = db.open_table(self.table_name)
            
            # Print schema for debugging
            print(f"Table schema before adding: {table.schema}")
            print(f"Adding node with keys: {list(node_data.keys())}")
            
            table.add([node_data])
            print(f"Successfully added node with ID: {node_id}")
        except Exception as e:
            print(f"Error adding node: {e}")
            print(f"Node data: {node_data}")
            raise
        
        # Find and create links to similar nodes
        self._update_links(node_id, content, embedding)
        
        return node_id
    
    def _update_links(self, node_id, content, embedding, max_links=5, threshold=0.7):
        """
        Update links for a node based on semantic similarity.
        
        Args:
            node_id: ID of the node to update links for
            content: Text content of the node
            embedding: Vector embedding of the node
            max_links: Maximum number of links to create
            threshold: Minimum similarity score threshold
        """
        import lancedb
        db = lancedb.connect(self.uri)
        table = db.open_table(self.table_name)
        
        # Check if we're using the default LanceDB schema
        using_default_schema = "vector" in str(self.schema) and "embedding" not in str(self.schema)
        
        # Find similar nodes - adapt search field based on schema
        if using_default_schema:
            # For older versions of LanceDB that don't support the column parameter
            # We need to use the vector field directly
            results = (
                table.search(embedding)  # Default search uses the first vector column
                .where(f"id != '{node_id}'")  # Exclude self
                .limit(max_links)
                .to_pandas()
            )
        else:
            results = (
                table.search(embedding)  # Default uses embedding column
                .where(f"id != '{node_id}'")  # Exclude self
                .limit(max_links)
                .to_pandas()
            )
        
        if len(results) == 0:
            return
        
        # Extract links and scores
        links = results['id'].tolist()
        scores = results['_distance'].tolist()  # LanceDB returns distances
        
        # Convert distances to similarity scores (assuming cosine distance)
        similarity_scores = [1 - score for score in scores]
        
        # Filter by threshold
        filtered_links = []
        filtered_scores = []
        for link, score in zip(links, similarity_scores):
            if score >= threshold:
                filtered_links.append(link)
                filtered_scores.append(score)
        
        # Update the node with new links - handle different schemas
        if using_default_schema:
            # For default schema, we need to update the JSON payload
            import json
            node_result = table.query().where(f"id = '{node_id}'").to_pandas()
            if len(node_result) == 0:
                return
                
            # Get current payload
            try:
                payload = json.loads(node_result['payload'].iloc[0])
                # Update links in payload
                payload['links'] = filtered_links
                payload['link_scores'] = filtered_scores
                payload['last_updated'] = datetime.now().isoformat()
                
                # Update the node with new payload
                table.update().where(f"id = '{node_id}'").set(
                    payload=json.dumps(payload)
                ).execute()
                print(f"Updated links for node {node_id} in payload")
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error updating links in payload: {e}")
                return
        else:
            # For custom schema, update fields directly
            table.update().where(f"id = '{node_id}'").set(
                links=filtered_links,
                link_scores=filtered_scores,
                last_updated=datetime.now()
            ).execute()
        
        # Also update the linked nodes to point back (bidirectional links)
        for linked_id in filtered_links:
            # Get the linked node
            linked_node_result = table.query().where(f"id = '{linked_id}'").to_pandas()
            if len(linked_node_result) == 0:
                continue
            
            if using_default_schema:
                # Handle payload for default schema
                try:
                    linked_payload = json.loads(linked_node_result['payload'].iloc[0])
                    existing_links = linked_payload.get('links', [])
                    existing_scores = linked_payload.get('link_scores', [])
                    
                    # Add the new link if it doesn't exist
                    if node_id not in existing_links:
                        existing_links.append(node_id)
                        # Find the score for this link
                        idx = filtered_links.index(linked_id)
                        existing_scores.append(filtered_scores[idx])
                        
                        # Update payload
                        linked_payload['links'] = existing_links
                        linked_payload['link_scores'] = existing_scores
                        linked_payload['last_updated'] = datetime.now().isoformat()
                        
                        # Update the node
                        table.update().where(f"id = '{linked_id}'").set(
                            payload=json.dumps(linked_payload)
                        ).execute()
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error updating bidirectional links in payload: {e}")
                    continue
            else:
                # Handle direct fields for custom schema
                existing_links = linked_node_result['links'].iloc[0] or []
                existing_scores = linked_node_result['link_scores'].iloc[0] or []
                
                # Add the new link if it doesn't exist
                if node_id not in existing_links:
                    existing_links.append(node_id)
                    # Find the score for this link
                    idx = filtered_links.index(linked_id)
                    existing_scores.append(filtered_scores[idx])
                    
                    table.update().where(f"id = '{linked_id}'").set(
                        links=existing_links,
                        link_scores=existing_scores,
                        last_updated=datetime.now()
                    ).execute()
    
    def get_node(self, node_id):
        """Get a node by ID."""
        import lancedb
        db = lancedb.connect(self.uri)
        table = db.open_table(self.table_name)
        
        result = table.query().where(f"id = '{node_id}'").to_pandas()
        if len(result) == 0:
            return None
            
        # Check if we're using the default LanceDB schema
        using_default_schema = "vector" in result.columns and "embedding" not in result.columns
        
        if using_default_schema:
            # Extract data from payload JSON
            import json
            row_dict = result.iloc[0].to_dict()
            
            try:
                payload_data = json.loads(row_dict.get('payload', '{}'))
                # Combine payload data with row data
                node_data = {
                    "id": row_dict.get('id'),
                    "embedding": row_dict.get('vector'),  # Map vector to embedding
                    **payload_data  # Unpack all payload fields
                }
                return node_data
            except json.JSONDecodeError:
                print(f"Warning: Could not parse payload JSON for node {node_id}")
                return row_dict
        else:
            # Using our custom schema
            return result.iloc[0].to_dict()
    
    def query(self, query_string):
        """Execute a SQL-like query on the memory graph."""
        import lancedb
        db = lancedb.connect(self.uri)
        table = db.open_table(self.table_name)
        
        # Check if we're using the default LanceDB schema
        using_default_schema = "vector" in str(self.schema) and "embedding" not in str(self.schema)
        
        # Parse the query to handle special functions
        if "NOW()" in query_string:
            now = datetime.now()
            query_string = query_string.replace("NOW()", f"'{now.isoformat()}'")
        
        # Get all nodes
        result = table.to_pandas()
        
        # Process results based on schema
        if using_default_schema and len(result) > 0 and 'payload' in result.columns:
            # For default schema, extract data from payload
            import json
            processed_results = []
            
            for _, row in result.iterrows():
                try:
                    # Extract payload data
                    payload = json.loads(row.get('payload', '{}'))
                    # Create a new row with combined data
                    combined_row = {
                        'id': row.get('id'),
                        'vector': row.get('vector'),
                        **payload  # Unpack payload fields
                    }
                    processed_results.append(combined_row)
                except json.JSONDecodeError:
                    # If payload can't be parsed, use original row
                    processed_results.append(row.to_dict())
            
            import pandas as pd
            result = pd.DataFrame(processed_results)
        
        # Execute the query - using filter instead of sql which may not be available in this version
        if "WHERE" in query_string:
            # Extract the condition after WHERE
            condition = query_string.split("WHERE")[1].strip()
            # Simple parsing for demonstration purposes
            if "last_updated" in condition and "NOW()" in condition:
                # Filter based on timestamp (simplified)
                # For a real implementation, we would need to parse the condition and apply it
                # Here we're just returning all recent nodes
                return result
        
        # Default: return all nodes
        return result
    
    def search(self, query_text, limit=5):
        """Search for nodes semantically similar to the query text."""
        # Generate embedding for the query
        embedding = self.vector_db.embedder.get_embedding(query_text)
        
        # Search in LanceDB
        import lancedb
        db = lancedb.connect(self.uri)
        table = db.open_table(self.table_name)
        
        # Check if we're using the default LanceDB schema
        using_default_schema = "vector" in str(self.schema) and "embedding" not in str(self.schema)
        
        # Search using the default vector column
        results = table.search(embedding).limit(limit).to_pandas()
        
        # Process results for default schema to include payload data
        if using_default_schema and len(results) > 0 and 'payload' in results.columns:
            import json
            processed_results = []
            
            for _, row in results.iterrows():
                try:
                    # Extract payload data
                    payload = json.loads(row.get('payload', '{}'))
                    # Create a new row with combined data
                    combined_row = {
                        'id': row.get('id'),
                        '_distance': row.get('_distance'),
                        **payload  # Unpack payload fields
                    }
                    processed_results.append(combined_row)
                except json.JSONDecodeError:
                    # If payload can't be parsed, use original row
                    processed_results.append(row.to_dict())
            
            import pandas as pd
            return pd.DataFrame(processed_results)
        
        return results
    
    def get_connected_nodes(self, start_id, depth=2):
        """
        Get nodes connected to the starting node up to a certain depth.
        Implements a breadth-first search traversal.
        
        Args:
            start_id: ID of the starting node
            depth: Maximum traversal depth
            
        Returns:
            List of connected node IDs
        """
        import lancedb
        db = lancedb.connect(self.uri)
        table = db.open_table(self.table_name)
        
        # Check if we're using the default LanceDB schema
        using_default_schema = "vector" in str(self.schema) and "embedding" not in str(self.schema)
        
        visited = set()
        queue = deque([(start_id, 0)])
        
        while queue:
            node_id, current_depth = queue.popleft()
            
            if current_depth > depth:
                break
                
            if node_id in visited:
                continue
                
            visited.add(node_id)
            
            # Get the node's links
            node = table.query().where(f"id = '{node_id}'").to_pandas()
            if len(node) == 0:
                continue
            
            # Extract links based on schema
            if using_default_schema:
                # For default schema, extract links from payload
                import json
                try:
                    payload = json.loads(node['payload'].iloc[0])
                    links = payload.get('links', [])
                except (json.JSONDecodeError, KeyError):
                    print(f"Warning: Could not extract links from payload for node {node_id}")
                    links = []
            else:
                # For custom schema, get links directly
                links = node['links'].iloc[0] or []
            
            # Add linked nodes to the queue
            for link_id in links:
                if link_id not in visited:
                    queue.append((link_id, current_depth + 1))
        
        return list(visited)
    
    def create_index(self, index_type="IVF_PQ", metric="cosine"):
        """Create an index for efficient vector search."""
        import lancedb
        db = lancedb.connect(self.uri)
        table = db.open_table(self.table_name)
        
        # Check if we're using the default LanceDB schema
        using_default_schema = "vector" in str(self.schema) and "embedding" not in str(self.schema)
        
        # Determine the vector column name based on schema
        vector_column = "vector" if using_default_schema else "embedding"
        
        try:
            table.create_index(
                vector_column_name=vector_column,  # Use the appropriate column name
                index_type=index_type,
                metric=metric
            )
            print(f"Created {index_type} index with {metric} metric on column {vector_column}")
        except Exception as e:
            print(f"Error creating index: {e}")
            print("Continuing without index creation")
    
    def create_agent_memory(self, user_memory=True, session_summary=True):
        """
        Create an agent memory configuration.
        This is a compatibility method to work with Agno agents.
        
        Returns:
            A dictionary with memory configuration
        """
        return {
            "user_memory": user_memory,
            "session_summary": session_summary,
            "memory_graph": self
        }

# If this file is run directly, show a simple usage example
if __name__ == "__main__":
    print("MemoryGraph class implementation")
    print("For usage examples, see example.py")
