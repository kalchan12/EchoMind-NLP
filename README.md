### EchoMind‑NLP

Simple, fast-to-build Python voice and text assistant with a clean UI. It supports text chat, speech-to-text (STT), and text-to-speech (TTS). Designed for quick iteration and easy deployment to Hugging Face Spaces or Streamlit Community Cloud.

---

### Features

- **Text Chat**: Natural language conversation with context awareness
- **Voice Input/Output**: Speech-to-text (Faster-Whisper) and text-to-speech (pyttsx3)
- **Conversation Memory**: Maintains conversation history for better responses
- **Command System**: Built-in commands like `/help`, `/clear`, `/status`, `/time`
- **Export/Import**: Save and load conversation history
- **Clean UI**: Modern Gradio interface with voice controls
- **Local-first**: Runs on CPU with lightweight models; can optionally use cloud APIs
- **Configurable**: Customize model size, language, and UI theme

---

### Quickstart

1) Clone and enter the project directory

```bash
git clone https://github.com/your-user/EchoMind-NLP.git
cd EchoMind-NLP
```

2) Create a virtual environment and install dependencies

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

3) (Optional) Set environment variables

```bash
cp .env.example .env
# edit .env if using cloud APIs like ElevenLabs or OpenAI
```

4) Run the app (Gradio)

```bash
python app.py
```

Then open the URL printed in your terminal (typically http://127.0.0.1:7860).

---

### Requirements

- Python 3.10+
- ffmpeg installed on your system (for audio I/O)

Ubuntu/Debian:

```bash
sudo apt update && sudo apt install -y ffmpeg
```

---

### Configuration

Environment variables (optional, for cloud services and tuning):

```env
# .env
# LLM (optional; otherwise use local Transformers pipeline)
OPENAI_API_KEY=""

# TTS (optional; otherwise use local Coqui TTS or pyttsx3)
ELEVENLABS_API_KEY=""

# STT language hint (e.g., en, es). Leave blank for auto.
STT_LANGUAGE="en"

# Model sizes (keep small for CPU): tiny/base/small/medium/large-v2
WHISPER_MODEL_SIZE="small"
```

Keep it simple: local STT/TTS defaults are enabled if API keys are not provided.

---

### Project Structure

```text
app.py                 # Gradio entry (Streamlit optional)
echomind/
  __init__.py
  config.py            # Pydantic settings wrapper
  core/
    orchestrator.py    # Glue: text in → response; hooks for voice
    nlp.py             # NLPProcessor (spaCy + Transformers or API)
    memory.py          # Simple in-memory conversation history
  speech/
    stt_base.py        # Interface for STT
    stt_fasterwhisper.py
    tts_base.py        # Interface for TTS
    tts_coqui.py
  ui/
    gradio_app.py      # Gradio components/fn bindings
    streamlit_app.py   # Optional Streamlit app
tests/
  test_nlp.py
  test_orchestrator.py
.env.example
requirements.txt
```

This is intentionally minimal. Interfaces are simple so you can swap implementations without touching the UI.

---

### Usage

**Text Chat:**
- Type your message in the text box and press Enter
- Use commands like `/help`, `/clear`, `/status`, `/time`
- Export conversations using the Export button

**Voice Features:**
- **Voice Input**: Click the microphone button, speak, and release to transcribe
- **Voice Output**: Click "🔊 Speak Response" to hear the assistant's response
- **Voice Settings**: Configure model size, language, and voice preferences

**Conversation Management:**
- View conversation history in the chat area
- Clear conversation history with the Clear button
- Export conversations to JSON files

**Tips for Performance:**
- Use `WHISPER_MODEL_SIZE=tiny` or `base` for faster processing on modest hardware
- Local `pyttsx3` TTS works offline and is lightweight
- Voice features require microphone access in your browser

---

### Development

Install optional dev tools:

```bash
pip install -r requirements-dev.txt  # if provided
```

Run tests:

```bash
pytest -q
```

Code style:
- `ruff` for linting, `black` for formatting (optional but recommended)
- Keep functions small and readable; avoid deep nesting

---

### Deployment

Hugging Face Spaces (Gradio):
- Push `app.py`, `requirements.txt`, and the `echomind/` package to a new Space
- Set secrets in the Space if using APIs (e.g., `OPENAI_API_KEY`)
- For faster cold starts, keep models small and load lazily


---



### FAQ

- **Do I need a GPU?** No. CPU works with small models; GPU helps but is optional.
- **Are API keys required?** No. Local defaults are used if keys are missing.
- **Which UI should I use?** Gradio is simplest. Streamlit is available if you prefer.

---



