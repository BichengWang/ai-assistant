import json
import os
from typing import List, Dict, Any
from datetime import datetime

class QAManager:
    def __init__(self, data_dir: str = "data/qa_pairs"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def add_qa_pair(self, question: str, answer: str, category: str = "general", metadata: Dict = None) -> str:
        qa_id = f"qa_{int(datetime.now().timestamp())}"
        qa_pair = {
            "id": qa_id,
            "question": question,
            "answer": answer,
            "category": category,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        filename = f"{qa_id}.json"
        filepath = os.path.join(self.data_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(qa_pair, f, ensure_ascii=False, indent=2)
        
        return qa_id
    
    def get_qa_pair(self, qa_id: str) -> Dict[str, Any]:
        filepath = os.path.join(self.data_dir, f"{qa_id}.json")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"QA pair {qa_id} not found")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_qa_pairs(self, category: str = None) -> List[Dict[str, Any]]:
        qa_pairs = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.data_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    qa_pair = json.load(f)
                    if category is None or qa_pair.get('category') == category:
                        qa_pairs.append(qa_pair)
        
        return sorted(qa_pairs, key=lambda x: x['created_at'], reverse=True)
    
    def update_qa_pair(self, qa_id: str, **updates) -> None:
        qa_pair = self.get_qa_pair(qa_id)
        qa_pair.update(updates)
        qa_pair['updated_at'] = datetime.now().isoformat()
        
        filepath = os.path.join(self.data_dir, f"{qa_id}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(qa_pair, f, ensure_ascii=False, indent=2)
    
    def delete_qa_pair(self, qa_id: str) -> None:
        filepath = os.path.join(self.data_dir, f"{qa_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
    
    def export_for_finetuning(self, output_file: str, format: str = "jsonl") -> None:
        qa_pairs = self.list_qa_pairs()
        
        if format == "jsonl":
            with open(output_file, 'w', encoding='utf-8') as f:
                for qa in qa_pairs:
                    training_example = {
                        "messages": [
                            {"role": "user", "content": qa["question"]},
                            {"role": "assistant", "content": qa["answer"]}
                        ]
                    }
                    f.write(json.dumps(training_example, ensure_ascii=False) + '\n')
        elif format == "csv":
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['question', 'answer', 'category'])
                for qa in qa_pairs:
                    writer.writerow([qa['question'], qa['answer'], qa['category']])