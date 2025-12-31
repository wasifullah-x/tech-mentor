"""
Data Preprocessing Script - Clean and prepare data for RAG system
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
import re
from loguru import logger

logger.add("logs/preprocessing.log", rotation="10 MB")


class DataPreprocessor:
    """Preprocesses IT support data for RAG ingestion"""
    
    def __init__(self, input_dir: str = "./data/raw", output_dir: str = "./data/processed"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def load_json(self, filename: str) -> List[Dict]:
        """Load data from JSON file"""
        file_path = self.input_dir / filename
        
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"Loaded {len(data)} items from {filename}")
        return data
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.,!?-]', '', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def deduplicate(self, data: List[Dict]) -> List[Dict]:
        """Remove duplicate entries"""
        seen_problems = set()
        unique_data = []
        
        for item in data:
            problem = item.get("problem", "").lower()
            
            # Create a fingerprint
            fingerprint = f"{problem}_{item.get('os', '')}_{item.get('device_type', '')}"
            
            if fingerprint not in seen_problems:
                seen_problems.add(fingerprint)
                unique_data.append(item)
            else:
                logger.debug(f"Duplicate found: {problem}")
        
        logger.info(f"Removed {len(data) - len(unique_data)} duplicates")
        return unique_data
    
    def validate_item(self, item: Dict) -> bool:
        """Validate that item has required fields"""
        required_fields = ["problem", "solutions"]
        
        for field in required_fields:
            if field not in item or not item[field]:
                logger.warning(f"Item missing required field: {field}")
                return False
        
        # Check solutions is not empty
        if isinstance(item["solutions"], list) and len(item["solutions"]) == 0:
            logger.warning("Item has empty solutions list")
            return False
        
        return True
    
    def enrich_data(self, item: Dict) -> Dict:
        """Enrich item with additional metadata"""
        # Add search tags
        if "search_tags" not in item:
            tags = set()
            
            # Add symptoms as tags
            if "symptoms" in item:
                tags.update(item["symptoms"])
            
            # Add OS and device type
            if "os" in item:
                tags.add(item["os"])
            if "device_type" in item:
                tags.add(item["device_type"])
            
            # Extract tags from problem description
            problem = item.get("problem", "").lower()
            common_tags = [
                "wifi", "internet", "slow", "freeze", "crash", "error",
                "battery", "power", "screen", "keyboard", "mouse", "printer"
            ]
            
            for tag in common_tags:
                if tag in problem:
                    tags.add(tag)
            
            item["search_tags"] = list(tags)
        
        # Add difficulty level
        if "difficulty" not in item:
            num_steps = len(item.get("solutions", []))
            if num_steps <= 2:
                item["difficulty"] = "easy"
            elif num_steps <= 4:
                item["difficulty"] = "medium"
            else:
                item["difficulty"] = "advanced"
        
        # Add estimated time
        if "estimated_time" not in item:
            num_steps = len(item.get("solutions", []))
            item["estimated_time"] = f"{num_steps * 2}-{num_steps * 5} minutes"
        
        return item
    
    def normalize_categories(self, data: List[Dict]) -> List[Dict]:
        """Normalize category names"""
        category_mapping = {
            "network": "networking",
            "internet": "networking",
            "wifi": "networking",
            "hardware": "hardware",
            "hw": "hardware",
            "software": "software",
            "sw": "software",
            "performance": "performance",
            "speed": "performance",
            "system": "system",
            "os": "system"
        }
        
        for item in data:
            category = item.get("category", "general").lower()
            item["category"] = category_mapping.get(category, category)
        
        return data
    
    def process_all(self, input_filename: str = "it_support_knowledge.json") -> List[Dict]:
        """Process all data through the pipeline"""
        logger.info("Starting data preprocessing...")
        
        # Load data
        data = self.load_json(input_filename)
        
        if not data:
            logger.error("No data loaded, cannot proceed")
            return []
        
        logger.info(f"Initial dataset size: {len(data)}")
        
        # Clean text fields
        for item in data:
            item["problem"] = self.clean_text(item.get("problem", ""))
            item["description"] = self.clean_text(item.get("description", ""))
        
        # Validate items
        data = [item for item in data if self.validate_item(item)]
        logger.info(f"After validation: {len(data)} items")
        
        # Deduplicate
        data = self.deduplicate(data)
        
        # Normalize categories
        data = self.normalize_categories(data)
        
        # Enrich with metadata
        data = [self.enrich_data(item) for item in data]
        
        # Save processed data
        output_path = self.output_dir / "processed_knowledge.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(data)} processed items to {output_path}")
        
        # Generate statistics
        self.generate_statistics(data)
        
        return data
    
    def generate_statistics(self, data: List[Dict]):
        """Generate and save statistics about the dataset"""
        stats = {
            "total_items": len(data),
            "categories": {},
            "device_types": {},
            "operating_systems": {},
            "difficulty_levels": {}
        }
        
        for item in data:
            # Count categories
            category = item.get("category", "unknown")
            stats["categories"][category] = stats["categories"].get(category, 0) + 1
            
            # Count device types
            device = item.get("device_type", "unknown")
            stats["device_types"][device] = stats["device_types"].get(device, 0) + 1
            
            # Count OS
            os = item.get("os", "unknown")
            stats["operating_systems"][os] = stats["operating_systems"].get(os, 0) + 1
            
            # Count difficulty
            difficulty = item.get("difficulty", "unknown")
            stats["difficulty_levels"][difficulty] = stats["difficulty_levels"].get(difficulty, 0) + 1
        
        # Save statistics
        stats_path = self.output_dir / "dataset_statistics.json"
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        
        logger.info("Dataset Statistics:")
        logger.info(f"  Total items: {stats['total_items']}")
        logger.info(f"  Categories: {stats['categories']}")
        logger.info(f"  Device types: {stats['device_types']}")
        logger.info(f"  Operating systems: {stats['operating_systems']}")
        logger.info(f"  Difficulty levels: {stats['difficulty_levels']}")


def main():
    """Main entry point"""
    preprocessor = DataPreprocessor()
    preprocessor.process_all()


if __name__ == "__main__":
    logger.info("IT Support Data Preprocessing Script")
    logger.info("=" * 50)
    
    main()
