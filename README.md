# Private Assistant Chatbot

A comprehensive private assistant chatbot system with fine-tuning capabilities, personal profiling, knowledge management, and model checkpoint handling.

## Features

### 🤖 Core Components

1. **Fine-tune Q/A Pair Management** - Collect and manage training data for model fine-tuning
2. **Personal Profiling** - Track user preferences, interests, and interaction patterns
3. **Knowledge Base** - Store and search through personal knowledge documents
4. **Model Checkpoints** - Manage and version AI model checkpoints
5. **Material Assistant** - Integrated assistant that combines all components

### 💡 Key Capabilities

- **Interactive CLI Interface** - Easy-to-use command line interface
- **Conversation History** - Maintains context across interactions
- **Personalized Responses** - Adapts responses based on user profile
- **Knowledge Search** - Query your personal knowledge base
- **Training Data Export** - Export conversations for model fine-tuning
- **Profile Analytics** - Track interaction patterns and preferences

## Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd private-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the assistant:
```bash
python main.py
```

### Basic Usage

```bash
# Start interactive mode
python main.py

# Use with custom data directory
python main.py --data-dir /path/to/data

# Use with configuration file
python main.py --config config/custom.json
```

## Interactive Commands

- `help` - Show available commands
- `/profile` - View current profile
- `/profile create` - Create/update user profile
- `/knowledge add` - Add knowledge to database
- `/knowledge search <query>` - Search knowledge base
- `/export <filename>` - Export training data
- `/stats` - Show system statistics

## Project Structure

```
private-assistant/
├── src/
│   ├── finetune/           # Q&A pair management
│   ├── profiling/          # User profile tracking
│   ├── knowledge_base/     # Knowledge management
│   ├── model_management/   # Model checkpoint handling
│   └── material_assistant/ # Main assistant component
├── data/                   # Data storage
│   ├── qa_pairs/          # Training Q&A pairs
│   ├── profiles/          # User profiles
│   ├── knowledge/         # Knowledge documents
│   └── checkpoints/       # Model checkpoints
├── config/                # Configuration files
├── tests/                 # Test files
└── main.py               # Main application entry point
```

## API Usage

```python
from src.material_assistant import MaterialAssistant

# Initialize assistant
assistant = MaterialAssistant("data")

# Process queries
response = assistant.process_query("What is machine learning?")
print(response['content'])

# Add knowledge
doc_id = assistant.add_knowledge(
    "Machine Learning Basics",
    "Machine learning is a subset of AI...",
    tags=["AI", "ML", "education"]
)

# Update profile
assistant.update_profile(
    name="John Doe",
    interests=["AI", "Python", "Data Science"],
    communication_style="technical"
)
```

## Configuration

Create a custom configuration file:

```json
{
  "assistant": {
    "name": "My Assistant",
    "context_window": 10
  },
  "features": {
    "auto_learn": true,
    "profile_tracking": true
  }
}
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Format code
black src/

# Type checking
mypy src/
```

## License

MIT License - see LICENSE file for details.
