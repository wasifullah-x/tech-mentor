"""
Data Collection Script - Collect IT support knowledge from various sources
"""
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import json
import csv
from pathlib import Path
import time
from loguru import logger

# Configure logger
logger.add("logs/data_collection.log", rotation="10 MB")


class ITSupportDataCollector:
    """Collects IT support data from various sources"""
    
    def __init__(self, output_dir: str = "./data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = None
    
    async def initialize(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession(
            headers={"User-Agent": "IT-Support-Assistant/1.0"}
        )
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def collect_microsoft_support(self) -> List[Dict[str, Any]]:
        """
        Collect data from Microsoft support documentation
        Note: This is a template - actual implementation requires API access
        """
        logger.info("Collecting Microsoft support articles...")
        
        # Template data structure - in production, use Microsoft Graph API
        sample_articles = [
            {
                "source": "microsoft",
                "title": "Fix Wi-Fi connection issues in Windows",
                "url": "https://support.microsoft.com/windows/wifi-issues",
                "problem": "Wi-Fi not working",
                "os": "windows",
                "solutions": [
                    "Run the network troubleshooter",
                    "Restart your modem and router",
                    "Update network adapter driver"
                ]
            },
            {
                "source": "microsoft",
                "title": "Improve Windows 11 performance",
                "url": "https://support.microsoft.com/windows/performance",
                "problem": "Slow computer performance",
                "os": "windows",
                "solutions": [
                    "Disable startup programs",
                    "Run Disk Cleanup",
                    "Check for malware"
                ]
            }
        ]
        
        return sample_articles
    
    async def collect_apple_support(self) -> List[Dict[str, Any]]:
        """
        Collect data from Apple support documentation
        Note: This is a template - actual implementation requires API access
        """
        logger.info("Collecting Apple support articles...")
        
        sample_articles = [
            {
                "source": "apple",
                "title": "If your Mac runs slowly",
                "url": "https://support.apple.com/mac/performance",
                "problem": "Mac running slow",
                "os": "macos",
                "solutions": [
                    "Check Activity Monitor",
                    "Free up storage space",
                    "Update macOS"
                ]
            }
        ]
        
        return sample_articles
    
    def create_structured_dataset(self, raw_articles: List[Dict]) -> List[Dict[str, Any]]:
        """
        Convert raw articles into structured format for training/RAG
        """
        logger.info(f"Processing {len(raw_articles)} articles into structured format...")
        
        structured_data = []
        
        for article in raw_articles:
            structured_item = {
                "id": f"{article['source']}_{len(structured_data)}",
                "problem": article.get("problem", ""),
                "description": article.get("title", ""),
                "device_type": self._infer_device_type(article),
                "os": article.get("os", "unknown"),
                "category": self._infer_category(article.get("problem", "")),
                "symptoms": self._extract_symptoms(article.get("problem", "")),
                "causes": self._infer_causes(article.get("problem", "")),
                "solutions": self._structure_solutions(article.get("solutions", [])),
                "source_url": article.get("url", ""),
                "source": article.get("source", "")
            }
            
            structured_data.append(structured_item)
        
        return structured_data
    
    def _infer_device_type(self, article: Dict) -> str:
        """Infer device type from article content"""
        text = (article.get("problem", "") + " " + article.get("title", "")).lower()
        
        if any(word in text for word in ["laptop", "notebook"]):
            return "laptop"
        elif any(word in text for word in ["desktop", "pc"]):
            return "desktop"
        elif any(word in text for word in ["iphone", "android", "phone", "mobile"]):
            return "phone"
        elif any(word in text for word in ["ipad", "tablet"]):
            return "tablet"
        elif any(word in text for word in ["mac", "macbook"]):
            return "laptop"
        else:
            return "computer"
    
    def _infer_category(self, problem: str) -> str:
        """Infer problem category"""
        problem_lower = problem.lower()
        
        if any(word in problem_lower for word in ["wifi", "internet", "network"]):
            return "networking"
        elif any(word in problem_lower for word in ["slow", "freeze", "performance"]):
            return "performance"
        elif any(word in problem_lower for word in ["printer", "mouse", "keyboard"]):
            return "peripherals"
        elif any(word in problem_lower for word in ["crash", "error", "blue screen"]):
            return "system"
        elif any(word in problem_lower for word in ["battery", "power"]):
            return "hardware"
        else:
            return "general"
    
    def _extract_symptoms(self, problem: str) -> List[str]:
        """Extract symptoms/keywords from problem description"""
        problem_lower = problem.lower()
        symptoms = []
        
        # Common symptom patterns
        symptom_keywords = [
            "slow", "freeze", "crash", "error", "not working", "won't turn on",
            "blue screen", "black screen", "no power", "overheating", "loud noise",
            "not connecting", "no signal", "battery drain", "stuck"
        ]
        
        for keyword in symptom_keywords:
            if keyword in problem_lower:
                symptoms.append(keyword)
        
        return symptoms if symptoms else ["unknown issue"]
    
    def _infer_causes(self, problem: str) -> List[Dict[str, str]]:
        """Infer likely causes based on problem"""
        # Simplified cause inference - in production, use ML model
        return [
            {"cause": "Configuration issue", "likelihood": "medium"},
            {"cause": "Software conflict", "likelihood": "medium"}
        ]
    
    def _structure_solutions(self, solutions: List[str]) -> List[Dict[str, Any]]:
        """Structure solutions into step format"""
        structured = []
        
        for i, solution in enumerate(solutions, 1):
            structured.append({
                "step": i,
                "action": solution,
                "why": "Addresses common cause of this issue",
                "risk_level": "safe"
            })
        
        return structured
    
    def save_to_json(self, data: List[Dict], filename: str):
        """Save collected data to JSON file"""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(data)} items to {output_path}")
    
    def save_to_csv(self, data: List[Dict], filename: str):
        """Save collected data to CSV file"""
        if not data:
            logger.warning("No data to save")
            return
        
        output_path = self.output_dir / filename
        
        # Flatten nested structures for CSV
        flattened_data = []
        for item in data:
            flat_item = {
                "id": item.get("id"),
                "problem": item.get("problem"),
                "description": item.get("description"),
                "device_type": item.get("device_type"),
                "os": item.get("os"),
                "category": item.get("category"),
                "symptoms": ", ".join(item.get("symptoms", [])),
                "source": item.get("source"),
                "source_url": item.get("source_url")
            }
            flattened_data.append(flat_item)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if flattened_data:
                writer = csv.DictWriter(f, fieldnames=flattened_data[0].keys())
                writer.writeheader()
                writer.writerows(flattened_data)
        
        logger.info(f"Saved {len(flattened_data)} items to {output_path}")
    
    async def collect_all(self):
        """Collect data from all sources"""
        logger.info("Starting data collection process...")
        
        await self.initialize()
        
        try:
            # Collect from various sources
            microsoft_data = await self.collect_microsoft_support()
            apple_data = await self.collect_apple_support()
            
            # Combine all data
            all_raw_data = microsoft_data + apple_data
            
            # Structure the data
            structured_data = self.create_structured_dataset(all_raw_data)
            
            # Save results
            self.save_to_json(structured_data, "it_support_knowledge.json")
            self.save_to_csv(structured_data, "it_support_knowledge.csv")
            
            logger.info(f"Data collection complete! Total items: {len(structured_data)}")
            
            return structured_data
            
        finally:
            await self.close()


async def main():
    """Main entry point for data collection"""
    collector = ITSupportDataCollector()
    await collector.collect_all()


if __name__ == "__main__":
    logger.info("IT Support Data Collection Script")
    logger.info("=" * 50)
    
    asyncio.run(main())
