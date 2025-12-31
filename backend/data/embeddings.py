"""
Embeddings Generation Script - Create vector embeddings for RAG
"""
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:  # pragma: no cover
    chromadb = None
    Settings = None
from loguru import logger
from tqdm import tqdm

logger.add("logs/embeddings.log", rotation="10 MB")


class EmbeddingsGenerator:
    """Generates embeddings and populates vector database"""
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        chroma_path: str = "./data/chroma_db",
        collection_name: str = "it_support_kb"
    ):
        self.model_name = model_name
        self.chroma_path = Path(chroma_path)
        self.collection_name = collection_name
        self.model = None
        self.client = None
        self.collection = None
    
    def initialize(self):
        """Initialize embedding model and vector database"""
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)

        if chromadb is None or Settings is None:
            raise RuntimeError(
                "ChromaDB is not installed. This script is optional and not required to run the API. "
                "If you want to generate embeddings into ChromaDB, install the missing dependency set."
            )
        
        # Create ChromaDB client
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initializing ChromaDB at: {self.chroma_path}")
        
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collection
        try:
            # Try to delete existing collection for fresh start
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted existing collection: {self.collection_name}")
        except:
            pass
        
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        logger.info(f"Created collection: {self.collection_name}")
    
    def load_processed_data(self, data_path: str = "./data/processed/processed_knowledge.json") -> List[Dict]:
        """Load processed knowledge data"""
        data_file = Path(data_path)
        
        if not data_file.exists():
            logger.error(f"Data file not found: {data_path}")
            return []
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data)} items from {data_path}")
        return data
    
    def create_searchable_text(self, item: Dict) -> str:
        """Create comprehensive searchable text from item"""
        components = []
        
        # Add problem and description
        if item.get("problem"):
            components.append(item["problem"])
        if item.get("description"):
            components.append(item["description"])
        
        # Add symptoms
        if item.get("symptoms"):
            symptoms_text = " ".join(item["symptoms"])
            components.append(f"Symptoms: {symptoms_text}")
        
        # Add search tags
        if item.get("search_tags"):
            tags_text = " ".join(item["search_tags"])
            components.append(f"Related: {tags_text}")
        
        # Add causes
        if item.get("causes"):
            causes_text = " ".join([c["cause"] for c in item["causes"]])
            components.append(f"Causes: {causes_text}")
        
        # Add solution summaries
        if item.get("solutions"):
            solutions_text = " ".join([s.get("action", "") for s in item["solutions"]])
            components.append(f"Solutions: {solutions_text}")
        
        return " ".join(components)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def add_to_vector_db(self, items: List[Dict], batch_size: int = 100):
        """Add items to vector database in batches"""
        logger.info(f"Adding {len(items)} items to vector database...")
        
        total_batches = (len(items) + batch_size - 1) // batch_size
        
        for batch_idx in tqdm(range(0, len(items), batch_size), desc="Processing batches"):
            batch = items[batch_idx:batch_idx + batch_size]
            
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for item in batch:
                # Create searchable text
                searchable_text = self.create_searchable_text(item)
                
                # Generate embedding
                embedding = self.generate_embedding(searchable_text)
                
                # Prepare metadata (flatten for ChromaDB)
                metadata = {
                    "problem": item.get("problem", ""),
                    "category": item.get("category", "general"),
                    "device_type": item.get("device_type", "unknown"),
                    "os": item.get("os", "unknown"),
                    "difficulty": item.get("difficulty", "medium"),
                    "estimated_time": item.get("estimated_time", "unknown"),
                    "data": str(item)  # Store full item as string for retrieval
                }
                
                ids.append(item.get("id", f"item_{batch_idx}_{len(ids)}"))
                embeddings.append(embedding)
                documents.append(searchable_text)
                metadatas.append(metadata)
            
            # Add batch to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
        
        total_count = self.collection.count()
        logger.info(f"Successfully added items. Total in database: {total_count}")
    
    def test_retrieval(self, test_queries: List[str]):
        """Test retrieval with sample queries"""
        logger.info("\nTesting retrieval with sample queries...")
        
        for query in test_queries:
            logger.info(f"\nQuery: {query}")
            
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=3
            )
            
            # Display results
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for i, doc_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    problem = results['metadatas'][0][i].get('problem', 'Unknown')
                    
                    logger.info(f"  {i+1}. {problem} (similarity: {similarity:.3f})")
            else:
                logger.info("  No results found")
    
    def generate_statistics(self):
        """Generate statistics about the vector database"""
        total_count = self.collection.count()
        
        # Sample some items to analyze
        sample_results = self.collection.get(
            limit=min(100, total_count)
        )
        
        stats = {
            "total_documents": total_count,
            "embedding_dimension": len(sample_results['embeddings'][0]) if sample_results['embeddings'] else 0,
            "categories": {},
            "device_types": {},
            "operating_systems": {}
        }
        
        # Analyze metadata
        for metadata in sample_results['metadatas']:
            category = metadata.get('category', 'unknown')
            device = metadata.get('device_type', 'unknown')
            os = metadata.get('os', 'unknown')
            
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            stats["device_types"][device] = stats["device_types"].get(device, 0) + 1
            stats["operating_systems"][os] = stats["operating_systems"].get(os, 0) + 1
        
        logger.info("\nVector Database Statistics:")
        logger.info(f"  Total documents: {stats['total_documents']}")
        logger.info(f"  Embedding dimension: {stats['embedding_dimension']}")
        logger.info(f"  Sample categories: {stats['categories']}")
        logger.info(f"  Sample device types: {stats['device_types']}")
        logger.info(f"  Sample OS: {stats['operating_systems']}")
        
        return stats
    
    def process_all(self, data_path: str = "./data/processed/processed_knowledge.json"):
        """Complete pipeline: load, embed, and store"""
        self.initialize()
        
        # Load data
        data = self.load_processed_data(data_path)
        
        if not data:
            logger.error("No data to process")
            return
        
        # Generate embeddings and store
        self.add_to_vector_db(data)
        
        # Generate statistics
        self.generate_statistics()
        
        # Test retrieval
        test_queries = [
            "My Wi-Fi won't connect",
            "Computer is very slow",
            "Laptop won't turn on",
            "Printer not printing",
            "Phone battery dying fast"
        ]
        
        self.test_retrieval(test_queries)
        
        logger.info("\nEmbeddings generation complete!")


def main():
    """Main entry point"""
    generator = EmbeddingsGenerator()
    generator.process_all()


if __name__ == "__main__":
    logger.info("IT Support Embeddings Generation Script")
    logger.info("=" * 50)
    
    main()
