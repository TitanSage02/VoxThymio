# VoxThymio 🤖🎤

> **Advanced voice and manual control system for Thymio robot**  
> Developed by **Espérance AYIWAHOUN** for **AI4Innov**

![VoxThymio](https://img.shields.io/badge/VoxThymio-v2.0-00d4aa?style=for-the-badge&logo=robot)
![AI4Innov](https://img.shields.io/badge/AI4Innov-Innovation-00d4aa?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-≥3.8-blue?style=for-the-badge&logo=python)
![Whisper](https://img.shields.io/badge/Speech--to--Text-Whisper-informational?style=for-the-badge)
![BERT](https://img.shields.io/badge/NLP-BERT-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**Intelligent Voice Control for Thymio Robot with AI**

VoxThymio is an advanced voice control system for Thymio robots that uses artificial intelligence to understand and execute natural language commands. The system dynamically learns new commands and offers an intuitive interface to control your Thymio robot by voice.

[🇫🇷 Version Française](./README.md)

## ✨ Key Features

- **🎤 Real-time Voice Recognition** - Multimodal support with Whisper and SpeechRecognition
- **🧠 Semantic Understanding** - Uses multilingual embeddings to understand command variations
- **📚 Dynamic Learning** - Automatically adds new commands based on semantic similarity
- **🔍 Vector Search** - ChromaDB database for efficient similar command retrieval
- **🤖 Native Thymio Control** - Direct robot communication via tdmclient
- **⚙️ Configurable Thresholds** - Fine-tuning of execution and learning thresholds

## 🏗️ Architecture

```
VoxThymio/
├── src/
│   ├── smart_voice_controller.py    # Main controller
│   ├── speech_recognizer.py         # Voice recognition module
│   ├── embedding_generator.py       # Semantic embeddings generation
│   ├── embedding_manager.py         # Vector database manager
│   ├── commands.json                # Base commands
│   └── controller/
│       └── thymio_controller.py     # Thymio interface
├── vector_db/                       # ChromaDB database
├── gui/                            # Graphical interface
├── requirements.txt                # Python dependencies
└── README.md                       # Documentation
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Thymio robot with compatible firmware
- Working microphone
- GPU recommended for better performance (optional)

### 1. Clone the repository
```bash
git clone https://github.com/TitanSage02/Vox-Thymio.git
cd VoxThymio
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Audio configuration (Windows)
```bash
# If pyaudio causes issues
pip install pipwin
pipwin install pyaudio
```

## 🎯 Usage

### Basic usage
```python
from src.smart_voice_controller import SmartVoiceController
from src.controller.thymio_controller import ThymioController
import asyncio

async def main():
    # Initialize Thymio connection
    thymio = ThymioController()
    await thymio.connect()
    
    # Create voice controller
    voice_controller = SmartVoiceController(thymio)
    
    # Process a text command
    result = await voice_controller.process_command("move forward")
    print(result)
    
    # Start voice recognition
    await voice_controller.voice_recognition()

asyncio.run(main())
```

### Available commands

#### Basic commands
- **Movement**: "move forward", "go back", "go straight"
- **Rotation**: "turn right", "turn left", "turn around"
- **Stop**: "stop", "halt", "brake"

#### Adding new commands
```python
# Add a custom command
voice_controller.add_new_command(
    command_id="dance",
    description="perform a dance",
    code="motor.left.target = 200\nmotor.right.target = -200\ncall prox.all"
)
```

## 🔧 Configuration

### Threshold adjustment
```python
# Modify similarity thresholds
voice_controller.update_thresholds(
    execution_threshold=0.6,  # Threshold for execution (0.0-1.0)
    learning_threshold=0.85   # Threshold for learning (0.0-1.0)
)
```

### Audio configuration
Modify parameters in `speech_recognizer.py`:
```python
# Voice recognition configuration
language = "en-US"          # Recognition language
model_size = "small"        # Whisper model size
energy_threshold = 300      # Audio detection threshold
```

## 📊 Technical Operation

### 1. Voice processing pipeline
1. **Audio Capture** → Microphone via PyAudio/SoundDevice
2. **Recognition** → Whisper or SpeechRecognition
3. **Normalization** → Text cleaning and preparation
4. **Embedding** → Generation via multilingual SentenceTransformer
5. **Search** → Cosine similarity in ChromaDB
6. **Execution** → Aseba code sent to Thymio

### 2. Models used
- **Voice Recognition**: OpenAI Whisper or Google Speech Recognition
- **Semantic Embeddings**: `paraphrase-multilingual-MiniLM-L12-v2`
- **Vector Database**: ChromaDB with cosine distance
- **Robot Communication**: Aseba Protocol via tdmclient

### 3. Learning system
- **Execution Threshold** (0.5): Recognized commands are executed
- **Learning Threshold** (0.85): New variants are automatically added
- **Conflict Detection**: Prevents duplicate similar commands

## 🧪 Testing and Debugging

### Run tests
```bash
# Test main controller
python src/smart_voice_controller.py

# Test voice recognition
python src/speech_recognizer.py

# Test Thymio communication
python src/controller/thymio_controller.py
```

### Performance diagnostics
```python
# Get system statistics
stats = voice_controller.get_system_stats()
print(f"Commands in database: {stats['database']['total_commands']}")
print(f"Embedding model: {stats['embedding_model']['model_name']}")
```

## 🛠️ Main Dependencies

| Package | Version | Usage |
|---------|---------|--------|
| `tdmclient` | ≥0.1.0 | Thymio communication |
| `SpeechRecognition` | ≥3.10.0 | Voice recognition fallback |
| `openai-whisper` | ≥20230314 | Main voice recognition |
| `transformers` | ≥4.0.0 | Embedding models |
| `sentence-transformers` | ≥2.2.0 | Semantic embeddings |
| `chromadb` | ≥0.4.0 | Vector database |
| `torch` | ≥1.10.0 | Embedding computations |
| `pyaudio` | ≥0.2.11 | Audio capture |

## 🐛 Troubleshooting

### Common issues

#### 1. Thymio connection error
```bash
❌ No Thymio robot detected
```
**Solution**: Check that the robot is powered on and connected via USB/Bluetooth.

#### 2. PyAudio error
```bash
❌ OSError: No Default Input Device Available
```
**Solution**: Check microphone permissions and install PyAudio correctly.

#### 3. Whisper model not found
```bash
❌ faster-whisper error: model not found
```
**Solution**: The model downloads automatically on first use. Check your internet connection.

#### 4. Inaccurate voice recognition
**Solutions**:
- Adjust `energy_threshold` in speech_recognizer.py
- Speak more clearly and close to the microphone
- Reduce ambient noise

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

### Code standards
- Follow PEP 8 for Python style
- Document new functions with docstrings
- Add tests for new functionality
- Use explicit variable names

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Espérance AYIWAHOUN** - *Main Development* - [GitHub](https://github.com/TitanSage02)
- **AI4Innov** - *Organization*

## 🙏 Acknowledgments

- [Mobsya](https://www.mobsya.org/) for the Thymio robot and development ecosystem
- [OpenAI](https://openai.com/) for the Whisper model
- [Sentence Transformers](https://www.sbert.net/) for multilingual embeddings
- [ChromaDB](https://www.trychroma.com/) for the vector database
- The open source community for the tools and libraries used

## 📈 Roadmap

- [ ] Complete graphical interface
- [ ] Gestural command support
- [ ] Multi-step complex command integration
- [ ] Support for multiple simultaneous robots
- [ ] REST API for remote control
- [ ] Contextual intention recognition
- [ ] Guided interactive learning mode

---

**VoxThymio** - Give your robot a voice! 🤖🗣️
