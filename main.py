#!/usr/bin/env python3
"""
Private Assistant Chatbot
Main application entry point
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

from src.material_assistant import MaterialAssistant

class PrivateAssistantCLI:
    def __init__(self, data_dir: str = "data"):
        self.assistant = MaterialAssistant(data_dir)
        self.running = True
    
    def run_interactive(self):
        print("=== Private Assistant Chatbot ===")
        print("Type 'help' for commands, 'quit' to exit")
        print()
        
        while self.running:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    self.running = False
                    print("Goodbye!")
                    continue
                
                if user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                if user_input.startswith('/'):
                    self.handle_command(user_input[1:])
                    continue
                
                # Process normal query
                response = self.assistant.process_query(user_input)
                print(f"Assistant: {response['content']}")
                print()
                
            except KeyboardInterrupt:
                self.running = False
                print("\nGoodbye!")
            except Exception as e:
                print(f"Error: {e}")
    
    def handle_command(self, command: str):
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == 'profile':
            if len(parts) > 1 and parts[1] == 'create':
                self.create_profile()
            else:
                self.show_profile()
        
        elif cmd == 'knowledge':
            if len(parts) > 1:
                if parts[1] == 'add':
                    self.add_knowledge()
                elif parts[1] == 'search':
                    query = ' '.join(parts[2:]) if len(parts) > 2 else input("Search query: ")
                    self.search_knowledge(query)
                elif parts[1] == 'list':
                    self.list_knowledge()
            else:
                print("Usage: /knowledge [add|search|list]")
        
        elif cmd == 'export':
            if len(parts) > 1:
                self.export_training_data(parts[1])
            else:
                print("Usage: /export <filename>")
        
        elif cmd == 'stats':
            self.show_stats()
        
        else:
            print(f"Unknown command: {cmd}")
    
    def show_help(self):
        help_text = """
Available commands:
- help                    : Show this help message
- quit/exit/bye          : Exit the application
- /profile               : Show current profile
- /profile create        : Create/update profile
- /knowledge add         : Add knowledge to database
- /knowledge search <query> : Search knowledge base
- /knowledge list        : List all knowledge entries
- /export <filename>     : Export training data
- /stats                 : Show assistant statistics

You can also just type naturally to chat with the assistant.
        """
        print(help_text)
    
    def create_profile(self):
        print("=== Profile Setup ===")
        name = input("Name: ")
        interests = input("Interests (comma-separated): ").split(',')
        interests = [i.strip() for i in interests if i.strip()]
        
        comm_style = input("Communication style (formal/casual/technical): ").lower()
        if comm_style not in ['formal', 'casual', 'technical']:
            comm_style = 'neutral'
        
        profile = self.assistant.update_profile(
            name=name,
            interests=[{"name": interest, "weight": 1.0} for interest in interests],
            communication_style=comm_style
        )
        
        print("Profile created successfully!")
    
    def show_profile(self):
        profile = self.assistant.profile_manager.get_profile()
        if not profile:
            print("No profile found. Use '/profile create' to create one.")
            return
        
        print("=== Current Profile ===")
        print(f"Name: {profile.get('name', 'Not set')}")
        print(f"Communication Style: {profile.get('communication_style', 'neutral')}")
        
        interests = profile.get('interests', [])
        if interests:
            print("Interests:")
            for interest in interests:
                if isinstance(interest, dict):
                    print(f"  - {interest.get('name', interest)}")
                else:
                    print(f"  - {interest}")
        
        skills = profile.get('skills', [])
        if skills:
            print("Skills:")
            for skill in skills:
                if isinstance(skill, dict):
                    print(f"  - {skill.get('name', skill)} ({skill.get('level', 'unknown')})")
                else:
                    print(f"  - {skill}")
        print()
    
    def add_knowledge(self):
        print("=== Add Knowledge ===")
        title = input("Title: ")
        print("Content (enter empty line to finish):")
        content_lines = []
        while True:
            line = input()
            if not line:
                break
            content_lines.append(line)
        content = '\n'.join(content_lines)
        
        tags = input("Tags (comma-separated): ").split(',')
        tags = [t.strip() for t in tags if t.strip()]
        
        source = input("Source (optional): ").strip() or None
        
        doc_id = self.assistant.add_knowledge(title, content, tags, source)
        print(f"Knowledge added with ID: {doc_id}")
    
    def search_knowledge(self, query: str):
        results = self.assistant.knowledge_manager.search_documents(query, limit=5)
        
        if not results:
            print("No matching knowledge found.")
            return
        
        print(f"=== Search Results for '{query}' ===")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('title', 'Untitled')}")
            print(f"   Tags: {', '.join(result.get('tags', []))}")
            preview = result.get('content_preview', '')
            if len(preview) > 100:
                preview = preview[:100] + "..."
            print(f"   Preview: {preview}")
            print()
    
    def list_knowledge(self):
        docs = self.assistant.knowledge_manager.list_documents(limit=10)
        
        if not docs:
            print("No knowledge entries found.")
            return
        
        print("=== Knowledge Base ===")
        for doc in docs:
            print(f"- {doc.get('title', 'Untitled')} ({len(doc.get('tags', []))} tags)")
    
    def export_training_data(self, filename: str):
        try:
            self.assistant.export_training_data(filename)
            print(f"Training data exported to: {filename}")
        except Exception as e:
            print(f"Export failed: {e}")
    
    def show_stats(self):
        stats = self.assistant.get_assistant_stats()
        
        print("=== Assistant Statistics ===")
        print(f"Total interactions: {stats['profile_analysis'].get('total_interactions', 0)}")
        print(f"Knowledge base: {stats['knowledge_base'].get('total_documents', 0)} documents")
        print(f"Model checkpoints: {stats['model_checkpoints'].get('total_checkpoints', 0)}")
        print(f"Conversation history: {stats.get('conversation_history_length', 0)} exchanges")
        
        if stats.get('last_interaction'):
            print(f"Last interaction: {stats['last_interaction']}")
        print()

def main():
    parser = argparse.ArgumentParser(description='Private Assistant Chatbot')
    parser.add_argument('--data-dir', default='data', help='Data directory path')
    parser.add_argument('--config', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Ensure data directory exists
    os.makedirs(args.data_dir, exist_ok=True)
    
    # Load configuration if provided
    config = {}
    if args.config and os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    try:
        cli = PrivateAssistantCLI(args.data_dir)
        cli.run_interactive()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()