import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..profiling import ProfileManager
from ..knowledge_base import KnowledgeManager
from ..finetune import QAManager
from ..model_management import CheckpointManager

class MaterialAssistant:
    def __init__(self, data_dir: str = "data"):
        self.profile_manager = ProfileManager(f"{data_dir}/profiles")
        self.knowledge_manager = KnowledgeManager(f"{data_dir}/knowledge")
        self.qa_manager = QAManager(f"{data_dir}/qa_pairs")
        self.checkpoint_manager = CheckpointManager(f"{data_dir}/checkpoints")
        
        self.conversation_history = []
        self.context_window = 10  # Number of recent interactions to consider
    
    def process_query(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        # Log the interaction
        self.profile_manager.log_interaction("query", user_input, metadata=context)
        
        # Get user profile for personalization
        profile = self.profile_manager.get_profile()
        preferences = self.profile_manager.get_preferences()
        
        # Search relevant knowledge
        knowledge_results = self.knowledge_manager.search_documents(user_input, limit=5)
        
        # Build response context
        response_context = {
            "user_profile": profile,
            "preferences": preferences,
            "relevant_knowledge": knowledge_results,
            "conversation_history": self.conversation_history[-self.context_window:],
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate response (placeholder for actual AI model integration)
        response = self._generate_response(user_input, response_context)
        
        # Log the response
        self.profile_manager.log_interaction("response", response["content"], 
                                           response=user_input, metadata=response_context)
        
        # Update conversation history
        self.conversation_history.append({
            "user_input": user_input,
            "assistant_response": response["content"],
            "timestamp": datetime.now().isoformat(),
            "context": context
        })
        
        # Learn from interaction
        self._learn_from_interaction(user_input, response, context)
        
        return response
    
    def add_knowledge(self, title: str, content: str, tags: List[str] = None, 
                     source: str = None) -> str:
        return self.knowledge_manager.add_document(title, content, tags, source)
    
    def update_profile(self, **updates) -> Dict[str, Any]:
        return self.profile_manager.update_profile(**updates)
    
    def set_preferences(self, preferences: Dict[str, Any]) -> None:
        self.profile_manager.set_preferences(preferences)
    
    def train_from_interaction(self, question: str, answer: str, category: str = "conversation") -> str:
        return self.qa_manager.add_qa_pair(question, answer, category)
    
    def export_training_data(self, output_file: str, format: str = "jsonl") -> None:
        self.qa_manager.export_for_finetuning(output_file, format)
    
    def save_model_checkpoint(self, model_name: str, version: str, model_path: str = None, 
                             metadata: Dict[str, Any] = None) -> str:
        return self.checkpoint_manager.save_checkpoint(model_name, version, model_path, metadata=metadata)
    
    def get_assistant_stats(self) -> Dict[str, Any]:
        profile_analysis = self.profile_manager.analyze_patterns()
        knowledge_stats = self.knowledge_manager.get_statistics()
        checkpoint_stats = self.checkpoint_manager.get_statistics()
        
        return {
            "profile_analysis": profile_analysis,
            "knowledge_base": knowledge_stats,
            "model_checkpoints": checkpoint_stats,
            "conversation_history_length": len(self.conversation_history),
            "last_interaction": self.conversation_history[-1]["timestamp"] if self.conversation_history else None
        }
    
    def personalize_response(self, base_response: str, user_profile: Dict[str, Any], 
                           preferences: Dict[str, Any]) -> str:
        # Adjust response based on user preferences
        communication_style = user_profile.get("communication_style", "neutral")
        
        if communication_style == "formal":
            # Make response more formal
            pass
        elif communication_style == "casual":
            # Make response more casual
            pass
        elif communication_style == "technical":
            # Add more technical details
            pass
        
        # Adjust based on learning preferences
        learning_style = preferences.get("learning_style", "balanced")
        if learning_style == "detailed":
            # Provide more detailed explanations
            pass
        elif learning_style == "concise":
            # Keep responses brief
            pass
        
        return base_response
    
    def get_relevant_context(self, query: str) -> Dict[str, Any]:
        # Get relevant knowledge
        knowledge = self.knowledge_manager.search_documents(query, limit=3)
        
        # Get recent relevant conversations
        relevant_history = []
        query_lower = query.lower()
        
        for conv in reversed(self.conversation_history):
            if query_lower in conv["user_input"].lower() or query_lower in conv["assistant_response"].lower():
                relevant_history.append(conv)
                if len(relevant_history) >= 3:
                    break
        
        return {
            "relevant_knowledge": knowledge,
            "relevant_conversations": relevant_history,
            "user_interests": self.profile_manager.get_profile().get("interests", []),
            "recent_topics": self._extract_recent_topics()
        }
    
    def _generate_response(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Placeholder for actual AI model integration
        # In a real implementation, this would use a language model
        
        base_response = f"I understand you're asking about: {user_input}"
        
        # Add relevant knowledge if found
        if context["relevant_knowledge"]:
            base_response += f"\n\nBased on my knowledge base, here's what I found relevant: {context['relevant_knowledge'][0].get('title', 'Information')}"
        
        # Personalize response
        personalized_response = self.personalize_response(
            base_response, 
            context["user_profile"], 
            context["preferences"]
        )
        
        return {
            "content": personalized_response,
            "confidence": 0.8,
            "sources": [doc["id"] for doc in context["relevant_knowledge"]],
            "context_used": len(context["relevant_knowledge"]) > 0
        }
    
    def _learn_from_interaction(self, user_input: str, response: Dict[str, Any], context: Dict[str, Any]) -> None:
        # Extract potential interests/topics from user input
        words = user_input.lower().split()
        important_words = [word for word in words if len(word) > 4]  # Simple heuristic
        
        for word in important_words[:3]:  # Limit to top 3
            self.profile_manager.add_interest(word, weight=0.1)
        
        # Update conversation patterns
        if context and context.get("topic"):
            self.profile_manager.add_interest(context["topic"], weight=0.5)
    
    def _extract_recent_topics(self) -> List[str]:
        topics = []
        for conv in self.conversation_history[-5:]:  # Last 5 conversations
            if conv.get("context", {}).get("topic"):
                topics.append(conv["context"]["topic"])
        return list(set(topics))