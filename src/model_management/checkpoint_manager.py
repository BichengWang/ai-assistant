import json
import os
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

class CheckpointManager:
    def __init__(self, data_dir: str = "data/checkpoints"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.metadata_file = os.path.join(data_dir, "checkpoints_metadata.json")
        self.models_dir = os.path.join(data_dir, "models")
        os.makedirs(self.models_dir, exist_ok=True)
    
    def save_checkpoint(self, model_name: str, version: str, model_path: str = None, 
                       model_data: bytes = None, metadata: Dict[str, Any] = None) -> str:
        checkpoint_id = f"{model_name}_{version}_{int(datetime.now().timestamp())}"
        checkpoint_dir = os.path.join(self.models_dir, checkpoint_id)
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        checkpoint_info = {
            "id": checkpoint_id,
            "model_name": model_name,
            "version": version,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "file_path": None,
            "file_hash": None,
            "file_size": None
        }
        
        # Save model file
        if model_path and os.path.exists(model_path):
            dest_path = os.path.join(checkpoint_dir, os.path.basename(model_path))
            shutil.copy2(model_path, dest_path)
            checkpoint_info["file_path"] = dest_path
            checkpoint_info["file_hash"] = self._calculate_file_hash(dest_path)
            checkpoint_info["file_size"] = os.path.getsize(dest_path)
        elif model_data:
            model_file = os.path.join(checkpoint_dir, f"{model_name}_v{version}.bin")
            with open(model_file, 'wb') as f:
                f.write(model_data)
            checkpoint_info["file_path"] = model_file
            checkpoint_info["file_hash"] = hashlib.md5(model_data).hexdigest()
            checkpoint_info["file_size"] = len(model_data)
        
        # Save checkpoint metadata
        metadata_path = os.path.join(checkpoint_dir, "checkpoint_info.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_info, f, ensure_ascii=False, indent=2)
        
        # Update global metadata
        self._update_global_metadata(checkpoint_id, checkpoint_info)
        
        return checkpoint_id
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        metadata = self._load_global_metadata()
        if checkpoint_id not in metadata:
            return None
        
        checkpoint_dir = os.path.join(self.models_dir, checkpoint_id)
        metadata_path = os.path.join(checkpoint_dir, "checkpoint_info.json")
        
        if not os.path.exists(metadata_path):
            return None
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            checkpoint_info = json.load(f)
        
        # Verify file integrity if file exists
        if checkpoint_info.get("file_path") and os.path.exists(checkpoint_info["file_path"]):
            current_hash = self._calculate_file_hash(checkpoint_info["file_path"])
            if current_hash != checkpoint_info.get("file_hash"):
                checkpoint_info["integrity_warning"] = "File hash mismatch - file may be corrupted"
        
        return checkpoint_info
    
    def list_checkpoints(self, model_name: str = None, sort_by: str = "created_at", 
                        limit: int = None) -> List[Dict[str, Any]]:
        metadata = self._load_global_metadata()
        checkpoints = list(metadata.values())
        
        # Filter by model name
        if model_name:
            checkpoints = [cp for cp in checkpoints if cp.get("model_name") == model_name]
        
        # Sort
        reverse = sort_by in ["created_at", "file_size"]
        checkpoints.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
        
        return checkpoints[:limit] if limit else checkpoints
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        checkpoint_dir = os.path.join(self.models_dir, checkpoint_id)
        if not os.path.exists(checkpoint_dir):
            return False
        
        # Remove directory and all contents
        shutil.rmtree(checkpoint_dir)
        
        # Update global metadata
        metadata = self._load_global_metadata()
        if checkpoint_id in metadata:
            del metadata[checkpoint_id]
            self._save_global_metadata(metadata)
        
        return True
    
    def compare_checkpoints(self, checkpoint_id1: str, checkpoint_id2: str) -> Dict[str, Any]:
        cp1 = self.load_checkpoint(checkpoint_id1)
        cp2 = self.load_checkpoint(checkpoint_id2)
        
        if not cp1 or not cp2:
            return {"error": "One or both checkpoints not found"}
        
        comparison = {
            "checkpoint_1": {
                "id": cp1["id"],
                "model_name": cp1["model_name"],
                "version": cp1["version"],
                "created_at": cp1["created_at"],
                "file_size": cp1.get("file_size")
            },
            "checkpoint_2": {
                "id": cp2["id"],
                "model_name": cp2["model_name"],
                "version": cp2["version"],
                "created_at": cp2["created_at"],
                "file_size": cp2.get("file_size")
            },
            "differences": {
                "model_name": cp1["model_name"] != cp2["model_name"],
                "version": cp1["version"] != cp2["version"],
                "file_size_diff": (cp1.get("file_size", 0) - cp2.get("file_size", 0)),
                "time_diff_hours": self._calculate_time_diff(cp1["created_at"], cp2["created_at"])
            }
        }
        
        return comparison
    
    def get_model_versions(self, model_name: str) -> List[Dict[str, Any]]:
        checkpoints = self.list_checkpoints(model_name=model_name, sort_by="created_at")
        versions = []
        
        for cp in checkpoints:
            versions.append({
                "checkpoint_id": cp["id"],
                "version": cp["version"],
                "created_at": cp["created_at"],
                "metadata": cp.get("metadata", {})
            })
        
        return versions
    
    def export_checkpoint(self, checkpoint_id: str, export_path: str) -> bool:
        checkpoint_info = self.load_checkpoint(checkpoint_id)
        if not checkpoint_info or not checkpoint_info.get("file_path"):
            return False
        
        source_file = checkpoint_info["file_path"]
        if not os.path.exists(source_file):
            return False
        
        try:
            shutil.copy2(source_file, export_path)
            
            # Also export metadata
            metadata_export = export_path.replace('.bin', '_metadata.json')
            with open(metadata_export, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_info, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception:
            return False
    
    def cleanup_old_checkpoints(self, model_name: str, keep_count: int = 5) -> List[str]:
        checkpoints = self.list_checkpoints(model_name=model_name, sort_by="created_at")
        
        if len(checkpoints) <= keep_count:
            return []
        
        to_delete = checkpoints[keep_count:]
        deleted_ids = []
        
        for cp in to_delete:
            if self.delete_checkpoint(cp["id"]):
                deleted_ids.append(cp["id"])
        
        return deleted_ids
    
    def get_statistics(self) -> Dict[str, Any]:
        metadata = self._load_global_metadata()
        
        total_checkpoints = len(metadata)
        model_counts = {}
        total_size = 0
        
        for cp in metadata.values():
            model_name = cp.get("model_name", "unknown")
            model_counts[model_name] = model_counts.get(model_name, 0) + 1
            total_size += cp.get("file_size", 0)
        
        return {
            "total_checkpoints": total_checkpoints,
            "models": model_counts,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    
    def _load_global_metadata(self) -> Dict[str, Any]:
        if not os.path.exists(self.metadata_file):
            return {}
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_global_metadata(self, metadata: Dict[str, Any]) -> None:
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _update_global_metadata(self, checkpoint_id: str, checkpoint_info: Dict[str, Any]) -> None:
        metadata = self._load_global_metadata()
        metadata[checkpoint_id] = {
            "id": checkpoint_info["id"],
            "model_name": checkpoint_info["model_name"],
            "version": checkpoint_info["version"],
            "created_at": checkpoint_info["created_at"],
            "file_size": checkpoint_info.get("file_size"),
            "file_hash": checkpoint_info.get("file_hash")
        }
        self._save_global_metadata(metadata)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _calculate_time_diff(self, time1: str, time2: str) -> float:
        dt1 = datetime.fromisoformat(time1.replace('Z', '+00:00'))
        dt2 = datetime.fromisoformat(time2.replace('Z', '+00:00'))
        diff = abs((dt1 - dt2).total_seconds())
        return round(diff / 3600, 2)  # Convert to hours