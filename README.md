# 🤖 Rasa PDF Chatbot

A conversational chatbot built with Rasa that can answer questions about the content of a PDF. You ask it something, it looks through the PDF and responds with a relevant answer. It runs a Rasa NLU/dialogue model alongside a custom actions server, with a FastAPI layer sitting in front to handle incoming requests.

---

## 🧠 How It Works

When you send a message, the flow goes like this:

1. The FastAPI server (port 8000) receives the request and forwards it to the Rasa model.
2. Rasa classifies the intent using the **DIET classifier** trained on your data.
3. If the intent is `ask_pdf_content`, Rasa triggers the custom action `action_respond_pdf_content`.
4. The actions server reads through the PDF, finds the relevant content, and returns a response.
5. If Rasa can't confidently classify the intent (below 0.3 threshold), the fallback kicks in with a default message.

---

## 📁 Repo Structure

```
RasaChatbot/
├── actions/              # Custom action code (action_respond_pdf_content)
├── api/                  # FastAPI app (main.py) serving as the entry point
├── data/                 # Rasa training data (NLU examples, stories, rules)
├── models/               # Trained Rasa model files
├── config.yml            # NLU pipeline and policy configuration
├── domain.yml            # Intents, responses, and actions definition
├── credentials.yml       # Channel credentials
├── endpoints.yml         # Action server endpoint config
├── requirements.txt      # Python dependencies
├── start_all.sh          # Shell script to start both servers at once (Linux/Mac)
└── use_python310.bat     # Batch script for Python 3.10 setup on Windows
```

---

## ⚙️ Requirements

Rasa requires **Python 3.10** specifically. Using a different version will cause compatibility issues.

Install all dependencies:

```bash
pip install -r requirements.txt
```

Key dependencies: `rasa`, `fastapi`, `uvicorn`

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/radhika-khatri/RasaChatbot.git
cd RasaChatbot
```

### 2. Set up Python 3.10 (Windows)

If you're on Windows, run the batch script first to configure the right Python version:

```bat
use_python310.bat
```

### 3. Train the Rasa model

If a pre-trained model isn't already in the `models/` folder, train one:

```bash
rasa train
```

This will use the data in `data/`, the pipeline in `config.yml`, and the domain defined in `domain.yml`.

### 4. Start both servers

**On Linux or Mac**, use the provided shell script to start everything in one go:

```bash
bash start_all.sh
```

This starts the FastAPI server on port 8000 and the Rasa actions server on port 5055.

**On Windows**, open two separate terminals and run:

Terminal 1 (FastAPI):
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Terminal 2 (Rasa actions server):
```bash
rasa run actions --port 5055 --debug
```

---

## 🖥️ How to Use It

Once both servers are running, send a POST request to the FastAPI endpoint with your message:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What does the PDF say about X?"}'
```

Or connect it to a frontend that sends messages to `http://localhost:8000`.

The bot handles two intents:

- `ask_pdf_content`: asks a question about the PDF content. The custom action reads the PDF and returns a relevant answer.
- `goodbye`: ends the conversation gracefully.

If the bot doesn't understand your message, it responds with a fallback: "Sorry, I couldn't find an answer."

---

## ⚙️ NLU Pipeline

The model uses the following pipeline (defined in `config.yml`):

- `WhitespaceTokenizer` for tokenization
- `RegexFeaturizer` and `LexicalSyntacticFeaturizer` for feature extraction
- `CountVectorsFeaturizer` (word-level and character n-gram level)
- `DIETClassifier` trained for 100 epochs
- `FallbackClassifier` with a confidence threshold of 0.3
- `MemoizationPolicy` and `RulePolicy` for dialogue management

---

## ⚠️ Things to Keep in Mind

- Python 3.10 is required. Rasa does not support newer Python versions cleanly.
- Both the FastAPI server and the Rasa actions server must be running at the same time for the bot to work.
- The PDF file used for Q&A needs to be accessible to the actions server. Check the `actions/` folder to see how the path is configured.
- Retrain the model (`rasa train`) any time you update the training data in `data/`.

---

## 🛠️ Built With

- **Rasa** for NLU and dialogue management
- **FastAPI** as the API layer
- **Uvicorn** as the ASGI server
- **Python 3.10**

---

## 👤 Author

**Radhika Khatri**  
[GitHub Profile](https://github.com/radhika-khatri)
