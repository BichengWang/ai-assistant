import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

class KnowledgeManager:
    def __init__(self, data_dir: str = "data/knowledge"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.index_file = os.path.join(data_dir, "index.json")
        self.documents_dir = os.path.join(data_dir, "documents")
        os.makedirs(self.documents_dir, exist_ok=True)
    
    def add_document(self, title: str, content: str, tags: List[str] = None, 
                    source: str = None, doc_type: str = "text") -> str:
        doc_id = hashlib.md5(f"{title}_{datetime.now().isoformat()}".encode()).hexdigest()
        
        document = {
            "id": doc_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "source": source,
            "type": doc_type,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": None
        }
        
        # Save document
        doc_path = os.path.join(self.documents_dir, f"{doc_id}.json")
        with open(doc_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        
        # Update index
        self._update_index(doc_id, document)
        
        return doc_id
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        doc_path = os.path.join(self.documents_dir, f"{doc_id}.json")
        if not os.path.exists(doc_path):
            return None
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            document = json.load(f)
        
        # Update access tracking
        document["access_count"] += 1
        document["last_accessed"] = datetime.now().isoformat()
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        
        return document
    
    def search_documents(self, query: str, tags: List[str] = None, 
                        doc_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        index = self._load_index()
        results = []
        
        query_lower = query.lower()
        
        for doc_id, doc_info in index.items():
            # Filter by type if specified
            if doc_type and doc_info.get("type") != doc_type:
                continue
            
            # Filter by tags if specified
            if tags and not any(tag in doc_info.get("tags", []) for tag in tags):
                continue
            
            # Search in title and content
            title_match = query_lower in doc_info.get("title", "").lower()
            content_match = query_lower in doc_info.get("content_preview", "").lower()
            
            if title_match or content_match:
                score = 0
                if title_match:
                    score += 2
                if content_match:
                    score += 1
                
                doc_info["relevance_score"] = score
                results.append(doc_info)
        
        # Sort by relevance and access count
        results.sort(key=lambda x: (x.get("relevance_score", 0), x.get("access_count", 0)), reverse=True)
        
        return results[:limit]
    
    def list_documents(self, tags: List[str] = None, doc_type: str = None, 
                      sort_by: str = "created_at", limit: int = None) -> List[Dict[str, Any]]:
        index = self._load_index()
        documents = list(index.values())
        
        # Filter by tags
        if tags:
            documents = [doc for doc in documents if any(tag in doc.get("tags", []) for tag in tags)]
        
        # Filter by type
        if doc_type:
            documents = [doc for doc in documents if doc.get("type") == doc_type]
        
        # Sort
        reverse = sort_by in ["created_at", "updated_at", "access_count"]
        documents.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
        
        return documents[:limit] if limit else documents
    
    def update_document(self, doc_id: str, **updates) -> bool:
        doc_path = os.path.join(self.documents_dir, f"{doc_id}.json")
        if not os.path.exists(doc_path):
            return False
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            document = json.load(f)
        
        document.update(updates)
        document["updated_at"] = datetime.now().isoformat()
        
        with open(doc_path, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
        
        # Update index
        self._update_index(doc_id, document)
        
        return True
    
    def delete_document(self, doc_id: str) -> bool:
        doc_path = os.path.join(self.documents_dir, f"{doc_id}.json")
        if not os.path.exists(doc_path):
            return False
        
        os.remove(doc_path)
        
        # Remove from index
        index = self._load_index()
        if doc_id in index:
            del index[doc_id]
            self._save_index(index)
        
        return True
    
    def get_tags(self) -> List[str]:
        index = self._load_index()
        all_tags = set()
        for doc_info in index.values():
            all_tags.update(doc_info.get("tags", []))
        return sorted(list(all_tags))
    
    def get_statistics(self) -> Dict[str, Any]:
        index = self._load_index()
        
        total_docs = len(index)
        types = {}
        tags = {}
        
        for doc_info in index.values():
            doc_type = doc_info.get("type", "unknown")
            types[doc_type] = types.get(doc_type, 0) + 1
            
            for tag in doc_info.get("tags", []):
                tags[tag] = tags.get(tag, 0) + 1
        
        return {
            "total_documents": total_docs,
            "document_types": types,
            "tag_usage": tags,
            "most_accessed": sorted(index.values(), key=lambda x: x.get("access_count", 0), reverse=True)[:5]
        }
    
    def _load_index(self) -> Dict[str, Any]:
        if not os.path.exists(self.index_file):
            return {}
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict[str, Any]) -> None:
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def _update_index(self, doc_id: str, document: Dict[str, Any]) -> None:
        index = self._load_index()
        
        # Create index entry with searchable preview
        content_preview = document.get("content", "")[:200] if document.get("content") else ""
        
        index[doc_id] = {
            "id": doc_id,
            "title": document.get("title"),
            "tags": document.get("tags", []),
            "type": document.get("type"),
            "source": document.get("source"),
            "created_at": document.get("created_at"),
            "updated_at": document.get("updated_at"),
            "access_count": document.get("access_count", 0),
            "content_preview": content_preview
        }
        
        self._save_index(index)