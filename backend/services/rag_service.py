"""RAG Service - Retrieval-Augmented Generation.

This project originally used ChromaDB, but on some Windows setups the native
dependency (`chroma-hnswlib`) requires MSVC build tools.

To keep local setup simple and allow the API to start reliably, this service
implements a lightweight in-memory retrieval strategy that ranks knowledge base
items by keyword overlap.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
from typing import Any, Dict, List, Optional

from loguru import logger

from api.config import settings


_WORD_RE = re.compile(r"[a-z0-9]+", re.IGNORECASE)


def _tokenize(text: str) -> List[str]:
    tokens = _WORD_RE.findall(text.lower())
    return [t for t in tokens if len(t) >= 3]


def _keyword_similarity(query: str, document: str) -> float:
    q_tokens = set(_tokenize(query))
    d_tokens = set(_tokenize(document))
    if not q_tokens or not d_tokens:
        return 0.0
    overlap = len(q_tokens & d_tokens)
    # Dice coefficient-like score in [0, 1]
    return (2.0 * overlap) / (len(q_tokens) + len(d_tokens))


@dataclass
class _InMemoryDoc:
    id: str
    item: Dict[str, Any]
    searchable_text: str


class _InMemoryCollection:
    def __init__(self, docs: List[_InMemoryDoc]):
        self._docs = docs

    def count(self) -> int:
        return len(self._docs)


class RAGService:
    """Service for managing vector database and retrieval"""
    
    def __init__(self):
        self.client = None
        self.collection: Optional[_InMemoryCollection] = None
        # Kept for backward compatibility with tests and callers.
        # This in-memory implementation does not require a heavy embedding model.
        self.embedding_model = object()
        self.initialized = False
        self._docs: List[_InMemoryDoc] = []
    
    async def initialize(self):
        """Initialize the RAG service"""
        if self.initialized:
            return

        # Create persist directory if it doesn't exist (kept for compatibility)
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)

        await self._initialize_sample_data()
        self.collection = _InMemoryCollection(self._docs)
        self.initialized = True
        logger.info(f"RAG service initialized (in-memory) with {self.collection.count()} documents")
    
    async def _initialize_sample_data(self):
        """Initialize the database with sample IT support knowledge"""
        logger.info("Initializing sample IT support knowledge base...")
        
        sample_data = [
            {
                "id": "wifi_1",
                "problem": "Wi-Fi not connecting",
                "description": "Device cannot connect to Wi-Fi network, shows 'Cannot connect' error",
                "device_type": "laptop",
                "os": "windows",
                "category": "networking",
                "symptoms": ["no wifi", "cannot connect", "network error"],
                "causes": [
                    {"cause": "Wi-Fi adapter disabled", "likelihood": "high"},
                    {"cause": "Wrong password", "likelihood": "high"},
                    {"cause": "Router issues", "likelihood": "medium"},
                    {"cause": "Driver problems", "likelihood": "medium"}
                ],
                "solutions": [
                    {
                        "step": 1,
                        "action": "Check if Wi-Fi is enabled on your device",
                        "why": "Wi-Fi might be disabled via airplane mode or physical switch",
                        "risk_level": "safe"
                    },
                    {
                        "step": 2,
                        "action": "Restart your Wi-Fi router by unplugging it for 30 seconds",
                        "why": "Clears temporary glitches in the router",
                        "risk_level": "safe"
                    },
                    {
                        "step": 3,
                        "action": "Forget the network and reconnect with the correct password",
                        "why": "Removes corrupted network settings",
                        "risk_level": "safe"
                    }
                ]
            },
            {
                "id": "slow_pc_1",
                "problem": "Computer running very slow",
                "description": "Computer has become sluggish, applications take long to open, frequent freezing",
                "device_type": "desktop",
                "os": "windows",
                "category": "performance",
                "symptoms": ["slow", "freezing", "laggy", "unresponsive"],
                "causes": [
                    {"cause": "Too many startup programs", "likelihood": "high"},
                    {"cause": "Insufficient RAM", "likelihood": "high"},
                    {"cause": "Full hard drive", "likelihood": "medium"},
                    {"cause": "Malware infection", "likelihood": "medium"}
                ],
                "solutions": [
                    {
                        "step": 1,
                        "action": "Open Task Manager (Ctrl+Shift+Esc) and check CPU/Memory usage",
                        "why": "Identifies which programs are consuming resources",
                        "risk_level": "safe"
                    },
                    {
                        "step": 2,
                        "action": "Disable unnecessary startup programs via Task Manager > Startup tab",
                        "why": "Reduces programs running in background",
                        "risk_level": "safe"
                    },
                    {
                        "step": 3,
                        "action": "Free up disk space by removing temporary files using Disk Cleanup",
                        "why": "More free space improves system performance",
                        "risk_level": "safe"
                    }
                ]
            },
            {
                "id": "blue_screen_1",
                "problem": "Blue Screen of Death (BSOD)",
                "description": "Computer crashes with blue screen showing error codes",
                "device_type": "laptop",
                "os": "windows",
                "category": "system",
                "symptoms": ["blue screen", "crash", "BSOD", "restart"],
                "causes": [
                    {"cause": "Driver conflicts", "likelihood": "high"},
                    {"cause": "Hardware failure", "likelihood": "medium"},
                    {"cause": "Windows updates", "likelihood": "medium"},
                    {"cause": "Overheating", "likelihood": "low"}
                ],
                "solutions": [
                    {
                        "step": 1,
                        "action": "Note down the error code from the blue screen (e.g., DRIVER_IRQL_NOT_LESS_OR_EQUAL)",
                        "why": "Error codes help identify the specific problem",
                        "risk_level": "safe"
                    },
                    {
                        "step": 2,
                        "action": "Boot in Safe Mode by restarting and pressing F8",
                        "why": "Safe Mode loads only essential drivers, helping isolate the problem",
                        "risk_level": "safe"
                    },
                    {
                        "step": 3,
                        "action": "Update or rollback recently installed drivers",
                        "why": "Incompatible drivers are a common cause of BSODs",
                        "risk_level": "caution"
                    }
                ]
            },
            {
                "id": "printer_1",
                "problem": "Printer not printing",
                "description": "Printer is connected but documents are not printing, stuck in queue",
                "device_type": "printer",
                "os": "windows",
                "category": "peripherals",
                "symptoms": ["not printing", "print queue", "printer offline"],
                "causes": [
                    {"cause": "Printer offline", "likelihood": "high"},
                    {"cause": "Paper jam", "likelihood": "high"},
                    {"cause": "Low ink/toner", "likelihood": "medium"},
                    {"cause": "Driver issues", "likelihood": "medium"}
                ],
                "solutions": [
                    {
                        "step": 1,
                        "action": "Check if printer is showing as 'Online' in Devices and Printers",
                        "why": "Printer must be online to accept print jobs",
                        "risk_level": "safe"
                    },
                    {
                        "step": 2,
                        "action": "Clear the print queue by canceling all documents",
                        "why": "Stuck documents can block new print jobs",
                        "risk_level": "safe"
                    },
                    {
                        "step": 3,
                        "action": "Restart the printer and reconnect USB cable or Wi-Fi",
                        "why": "Resets the connection between computer and printer",
                        "risk_level": "safe"
                    }
                ]
            },
            {
                "id": "phone_battery_1",
                "problem": "Phone battery draining fast",
                "description": "Smartphone battery depletes quickly, doesn't last through the day",
                "device_type": "phone",
                "os": "android",
                "category": "mobile",
                "symptoms": ["battery drain", "short battery life", "quick discharge"],
                "causes": [
                    {"cause": "Background apps consuming power", "likelihood": "high"},
                    {"cause": "Screen brightness too high", "likelihood": "high"},
                    {"cause": "Old battery", "likelihood": "medium"},
                    {"cause": "Location services always on", "likelihood": "medium"}
                ],
                "solutions": [
                    {
                        "step": 1,
                        "action": "Check battery usage in Settings > Battery to identify power-hungry apps",
                        "why": "Shows which apps are consuming the most battery",
                        "risk_level": "safe"
                    },
                    {
                        "step": 2,
                        "action": "Reduce screen brightness and enable adaptive brightness",
                        "why": "Display is typically the biggest battery consumer",
                        "risk_level": "safe"
                    },
                    {
                        "step": 3,
                        "action": "Disable unnecessary background app refresh and location services",
                        "why": "Apps running in background drain battery even when not in use",
                        "risk_level": "safe"
                    }
                ]
            },
            {
                "id": "laptop_no_power_1",
                "problem": "Laptop won't turn on",
                "description": "Laptop shows no signs of power, no lights, completely unresponsive",
                "device_type": "laptop",
                "os": "windows",
                "category": "hardware",
                "symptoms": ["won't turn on", "no power", "black screen", "dead"],
                "causes": [
                    {"cause": "Dead battery", "likelihood": "high"},
                    {"cause": "Power adapter failure", "likelihood": "high"},
                    {"cause": "Loose connection", "likelihood": "medium"},
                    {"cause": "Hardware failure", "likelihood": "low"}
                ],
                "solutions": [
                    {
                        "step": 1,
                        "action": "Check if power adapter LED is lit and connections are secure",
                        "why": "Verifies power is reaching the laptop",
                        "risk_level": "safe"
                    },
                    {
                        "step": 2,
                        "action": "Remove battery (if removable) and hold power button for 30 seconds, then reconnect",
                        "why": "Performs a hard reset to clear residual power",
                        "risk_level": "safe"
                    },
                    {
                        "step": 3,
                        "action": "Try a different power outlet and adapter if available",
                        "why": "Rules out faulty outlet or adapter",
                        "risk_level": "safe"
                    }
                ]
            },
            {
                "id": "forgot_password_1",
                "problem": "Forgot Windows password",
                "description": "Cannot log into Windows account, forgot the password",
                "device_type": "desktop",
                "os": "windows",
                "category": "security",
                "symptoms": ["locked out", "forgot password", "cannot login"],
                "causes": [
                    {"cause": "Password forgotten or mistyped", "likelihood": "high"},
                    {"cause": "Caps Lock enabled", "likelihood": "medium"}
                ],
                "solutions": [
                    {
                        "step": 1,
                        "action": "Check if Caps Lock is on - password is case-sensitive",
                        "why": "Common mistake that prevents login",
                        "risk_level": "safe"
                    },
                    {
                        "step": 2,
                        "action": "Use 'I forgot my password' link on login screen for Microsoft accounts",
                        "why": "Microsoft provides password reset via email or phone",
                        "risk_level": "safe"
                    },
                    {
                        "step": 3,
                        "action": "For local accounts, use password reset disk if created previously",
                        "why": "Password reset disk can restore access to local accounts",
                        "risk_level": "safe"
                    }
                ]
            },
            {
                "id": "mac_spinning_wheel_1",
                "problem": "Mac showing spinning wheel frequently",
                "description": "MacBook displays the spinning wait cursor (beach ball) often, applications freeze",
                "device_type": "laptop",
                "os": "macos",
                "category": "performance",
                "symptoms": ["spinning wheel", "beach ball", "freezing", "slow"],
                "causes": [
                    {"cause": "Insufficient RAM", "likelihood": "high"},
                    {"cause": "Full startup disk", "likelihood": "high"},
                    {"cause": "Too many background processes", "likelihood": "medium"},
                    {"cause": "Disk errors", "likelihood": "low"}
                ],
                "solutions": [
                    {
                        "step": 1,
                        "action": "Open Activity Monitor to check CPU and memory usage",
                        "why": "Identifies resource-hungry applications",
                        "risk_level": "safe"
                    },
                    {
                        "step": 2,
                        "action": "Check available storage in About This Mac > Storage",
                        "why": "macOS needs at least 10-15% free space to function properly",
                        "risk_level": "safe"
                    },
                    {
                        "step": 3,
                        "action": "Quit unnecessary applications and close browser tabs",
                        "why": "Frees up RAM and CPU resources",
                        "risk_level": "safe"
                    }
                ]
            }
        ]
        
        self._docs = []
        for item in sample_data:
            search_text = f"{item.get('problem','')} {item.get('description','')} {' '.join(item.get('symptoms', []))}"
            self._docs.append(_InMemoryDoc(id=item["id"], item=item, searchable_text=search_text))

        logger.info(f"Added {len(self._docs)} sample documents to knowledge base")
    
    async def retrieve_solutions(
        self,
        query: str,
        top_k: int = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant solutions from the knowledge base
        
        Args:
            query: User's problem description
            top_k: Number of results to return
            filter_dict: Optional filters (device_type, os, category)
        
        Returns:
            List of relevant solution documents
        """
        if not self.initialized:
            await self.initialize()
        
        top_k = top_k or settings.rag_top_k
        
        scored: List[Dict[str, Any]] = []

        for doc in self._docs:
            item = doc.item

            if filter_dict:
                matches = True
                for key, expected in filter_dict.items():
                    if expected is None:
                        continue
                    if str(item.get(key, "")).lower() != str(expected).lower():
                        matches = False
                        break
                if not matches:
                    continue

            similarity = _keyword_similarity(query, doc.searchable_text)
            metadata = {
                "problem": item.get("problem", ""),
                "device_type": item.get("device_type", ""),
                "os": item.get("os", ""),
                "category": item.get("category", ""),
                "data": str(item),
            }
            scored.append(
                {
                    "id": doc.id,
                    "similarity": similarity,
                    "problem": item.get("problem", ""),
                    "category": item.get("category", ""),
                    "device_type": item.get("device_type", ""),
                    "os": item.get("os", ""),
                    "content": doc.searchable_text,
                    "metadata": metadata,
                }
            )

        scored.sort(key=lambda r: r.get("similarity", 0.0), reverse=True)

        # If the configured similarity threshold is too strict for keyword scoring,
        # still return best-effort results.
        filtered = [r for r in scored if r.get("similarity", 0.0) >= settings.rag_similarity_threshold]
        results = filtered if filtered else scored
        results = results[:top_k]

        logger.info(f"Retrieved {len(results)} solutions for query: {query[:50]}...")
        return results
    
    async def add_document(
        self,
        doc_id: str,
        content: str,
        metadata: Dict[str, Any]
    ):
        """Add a new document to the knowledge base"""
        if not self.initialized:
            await self.initialize()
        
        self._docs.append(_InMemoryDoc(id=doc_id, item={**metadata, "id": doc_id}, searchable_text=content))
        if self.collection is None:
            self.collection = _InMemoryCollection(self._docs)
        logger.info(f"Added document {doc_id} to knowledge base")
    
    async def close(self):
        """Cleanup resources"""
        self.initialized = False
        logger.info("RAG service closed")
