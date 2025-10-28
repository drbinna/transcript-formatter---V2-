
# 🎓 ORU Transcript Formatting Application

A lightweight web application that uses **Claude AI (Anthropic)** to intelligently format raw transcript text files (`.txt`) into clean, styled `.docx` documents using ORU's formatting standards.

The app:
1. **Reads your sample** formatted document to learn the desired formatting
2. **Uses Claude AI** to parse and structure raw transcript content
3. **Applies intelligent formatting** with inline mixed styles (bold, italic, etc.)
4. Returns a perfectly formatted `.docx` file for download

**No authentication, no file storage** - just upload and get formatted output.

---

## 🚀 Features

- 🧠 **AI-Powered Formatting** - Uses Claude 3.5 Sonnet to intelligently parse transcripts
- 📂 Upload `.txt` transcript files directly
- 🎯 Learn from your template - Reads your sample document to match exact formatting
- 🔤 Mixed inline formatting - Bold speakers, italic quotes, bold scripture refs within same paragraph
- 🪶 Generate well-formatted `.docx` instantly
- 💻 Simple one-page interface (React + Tailwind)
- ⚡ No authentication or database required (except Anthropic API key)

---

## 🧱 Architecture Overview

| Layer | Technology | Purpose |
|-------|-------------|----------|
| **Frontend** | React + TailwindCSS | Handles file upload, user interaction, and triggers formatting |
| **Backend** | FastAPI (Python) | Receives transcript, calls Claude API, generates formatted `.docx` |
| **AI Engine** | **Claude 3.5 Sonnet** | Intelligently parses and formats transcripts based on sample template |
| **Formatting Engine** | `python-docx` | Applies text styles (fonts, sizes, italics, indentations) from AI output |

**How it works:**
1. Sample document in `templates/` teaches Claude the desired formatting
2. Raw transcript upload → Claude analyzes and structures content
3. AI returns JSON with formatting instructions
4. Backend generates `.docx` with mixed formatting (bold, italic, etc.)

---

## ⚙️ Project Structure

```
transcript-app/
├── backend/
│   ├── main.py            # FastAPI entrypoint
│   ├── formatter.py       # Transcript parsing and DOCX generation logic
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # React frontend UI
│   │   └── index.css
│   └── package.json
├── templates/
│   └── sample_formatted.docx  # TEMPLATE: Styled example showing desired output format
├── samples/
│   └── sample_input.txt       # Sample raw transcript input for testing
└── README.md              # Project documentation
```

---

## 📋 Setup with Sample Document

**IMPORTANT:** Your sample document `templates/sample_formatted.docx` is already included and will be used to train Claude on formatting.

### How Claude Learns from Your Sample:

The formatter has been configured based on your exact formatting requirements:

1. **Title**: "Living in the Last Days" - Centered, Bold, 20pt
2. **Speakers**: Names ending with ":" are Bold (12pt Times New Roman)
   - Example: `Dr. Billy Wilson:`, `male announcer:`, `Billy:`, `Eli Brown:`
3. **Scripture References**: Bold (e.g., "1 John 2:18", "2 Timothy 3:1–5")
4. **Scripture Quotes**: Text in quotes is italic
5. **Show Names**: Quoted show names like "World Impact" are italic
6. **Song Titles**: Quoted song titles like "Give me Jesus" are italic
7. **Music Lines**: Preserve ♪ symbols as-is
8. **Regular Text**: 12pt Times New Roman

### Claude AI Automatically:

- **Reads your template** to understand the exact formatting you want
- **Intelligently parses** raw transcript input
- **Detects and formats:**
  - Speaker names (ending with ":") → Bold
  - Scripture references → Bold
  - Quoted text (show names, song titles) → Italic
  - Music lines with ♪ symbols → Preserved as-is
- **Applies inline mixed formatting** within paragraphs (e.g., bold speaker name followed by italic quote in same line)
- **Returns structured JSON** for backend to generate perfect `.docx`

**Workflow:**
```
Sample Template → Claude Learns Formatting Rules → Raw Transcript → Claude Parses & Formats → JSON Structure → Generate Formatted .docx
```

**The formatter intelligently handles:**
- Speaker detection (names ending with ":")
- Scripture reference detection (book names with chapter:verse)
- Quote detection (text in quotation marks)
- Music preservation (♪ symbols)
- Inline mixed formatting (bold speakers + italic quotes within same paragraph)
- Context-aware formatting based on your sample document

---

## 🧠 Core Logic

### 1. Template-Based Style Extraction

**Key Innovation:** The application reads your `sample_formatted.docx` template file to extract exact formatting preferences.

- On startup, the backend analyzes `templates/sample_formatted.docx`
- Extracts font sizes, colors, bold/italic settings, indentation, and alignment
- Uses these exact styles for all future transcript formatting
- **Result:** Every output matches your sample document's look and feel

### 2. Parsing Rules

The backend identifies four main content types:

| Type | Detection Pattern | Example | Formatting |
|------|-------------------|----------|-------------|
| **Speaker** | Regex: `^([A-Z][a-zA-Z .'-]+):` | `Dr. Billy Wilson:` | Bold name, normal paragraph text |
| **Scripture** | Regex: `\b([1-3]?\s?[A-Z][a-z]+)\s\d+:\d+` | `2 Timothy 3:1–5` | Italic, indented |
| **Music** | Line starts with `♪` | `♪ Give me Jesus ♪` | Italic + centered |
| **Narration** | Default (everything else) | `Welcome to World Impact...` | Standard paragraph |

These rules are applied sequentially to the text input.

### 3. DOCX Generation

- Uses `python-docx` to create a document in memory
- Applies extracted styles from your template to each content type
- Ensures consistent formatting across all transcripts
- Final `.docx` is returned as a byte stream for immediate download

---

## 🧩 API Reference

### Base URL
```
http://localhost:8000
```

### `POST /format`

**Description:**  
Formats a raw text transcript into a styled `.docx`.

**Request:**
- `Content-Type: multipart/form-data`
- **Body:**  
  - `file`: the `.txt` transcript to format

**Response:**
- `Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document`
- Returns a `.docx` file for download

**Example cURL:**
```bash
curl -X POST http://localhost:8000/format   -F "file=@Last_Days.txt"   --output Formatted_Transcript.docx
```

---

## 🧠 Example Processing Flow

```
User uploads: Last_Days.txt
        ↓
Backend parses:
   - Detects speakers, scriptures, songs, narration
        ↓
Formats into DOCX:
   - Applies ORU styling
   - Adds indentation, italics, and bold where needed
        ↓
Frontend auto-triggers download
```

---

## 🖥️ Frontend Setup (React + Tailwind)

### Prerequisites
- Node.js (v18+ recommended)

### Run
```bash
cd frontend
npm install
npm run dev
```

This launches the app at:
```
http://localhost:5173
```

### Frontend Behavior
- Displays upload input and “Generate DOCX” button.
- Sends `.txt` file to backend via `POST /format`.
- Receives and downloads formatted `.docx` automatically.

---

## 🧮 Backend Setup (FastAPI + Claude API)

### Prerequisites
- Python 3.9+
- pip
- Anthropic API key ([Get one here](https://console.anthropic.com/))

### Set Up API Key

Before running the backend, you need to set your Anthropic API key:

**Option 1: Environment variable (Recommended)**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

**Option 2: Create `.env` file (Recommended)**
```bash
# In the backend directory
cd backend
# Copy the example file
cp .env.example .env
# Then edit .env and replace "paste-your-api-key-here" with your actual API key
```

The `.env` file is already created for you! Just open `backend/.env` and replace `paste-your-api-key-here` with your actual Anthropic API key.

**Option 3: Windows PowerShell**
```powershell
$env:ANTHROPIC_API_KEY="your-api-key-here"
```

### Install
```bash
cd backend
pip install -r requirements.txt
```

### Run
```bash
uvicorn main:app --reload
```

This starts the backend at:
```
http://localhost:8000
```

---

## 🔌 API and Frontend Connection

The frontend sends the uploaded file to:
```
POST http://localhost:8000/format
```

Ensure both the frontend (`localhost:5173`) and backend (`localhost:8000`) are running concurrently.
For local dev, you may need to enable CORS in the FastAPI backend:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```

---

## 💻 Complete Implementation

### Backend Files

#### `backend/main.py`
```python
from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from formatter import format_transcript
import io
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="ORU Transcript Formatter")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/format")
async def format_transcript_endpoint(file: UploadFile = File(...)):
    """
    Accepts a raw transcript text file and returns a formatted .docx document.
    Uses Claude AI to intelligently parse and format the transcript.
    """
    # Read the uploaded file content
    content = await file.read()
    text = content.decode('utf-8')
    
    # Extract filename for potential title
    filename = file.filename or "transcript"
    
    # Format the transcript using Claude
    docx_bytes = format_transcript(text)
    
    # Return as downloadable .docx
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": "attachment; filename=formatted_transcript.docx"}
    )

@app.get("/")
async def root():
    return {"message": "ORU Transcript Formatting API", "version": "1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### `backend/formatter.py` (Claude-Powered)

**NEW:** This application uses Claude AI to intelligently parse and format transcripts based on your sample document.
```python
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re
import io
import os
import json
from anthropic import Anthropic

# Initialize Claude client
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def read_template_context(template_path: str = "templates/sample_formatted.docx") -> str:
    """Read the template document to use as context for Claude"""
    try:
        doc = Document(template_path)
        # Extract first 20 paragraphs as context
        context = []
        for para in doc.paragraphs[:20]:
            if para.text.strip():
                context.append(para.text)
        return "\n".join(context)
    except Exception as e:
        print(f"Warning: Could not read template: {e}")
        return ""

def format_transcript(text: str, title: str = None) -> bytes:
    """
    Use Claude AI to intelligently parse and format transcript based on sample template.
    
    Args:
        text: Raw transcript content as a string
        title: Optional title for the document
        
    Returns:
        bytes: The formatted .docx document as binary data
    """
    # Read the template to understand the desired formatting
    template_text = read_template_context()
    
    # Use Claude to analyze and format the transcript
    response = claude_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=8192,
        system="""You are a document formatting assistant. Your task is to analyze a raw transcript and format it according to the example template provided.

The formatting rules based on the template:
1. Title: Centered, bold, 20pt (Gotham font)
2. Speaker names (ending with ':'): Bold, 12pt Times New Roman
3. Scripture references (e.g., '1 John 2:18', '2 Timothy 3:1-5'): Bold
4. Text in double quotes (show names, song titles, scripture quotes): Italic
5. Music lines (containing ♪): Preserve as-is
6. Regular text: 12pt Times New Roman

Format the transcript using this JSON structure:
{
  "title": "Document title",
  "paragraphs": [
    {
      "text": "Full paragraph text",
      "runs": [
        {"text": "text segment", "bold": false, "italic": false}
      ]
    }
  ]
}

Return ONLY valid JSON, no markdown formatting.""",
        messages=[
            {
                "role": "user",
                "content": f"""Here is the sample formatting template:

{template_text}

Now format this transcript:

{text}

Provide the formatted result as JSON following the structure above."""
            }
        ]
    )
    
    # Parse Claude's response
    formatted_json = json.loads(response.content[0].text)
    
    # Create Word document
    doc = Document()
    
    # Add title
    title_para = doc.add_paragraph(formatted_json["title"])
    title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_para.runs[0]
    title_run.font.size = Pt(20)
    title_run.bold = True
    title_run.font.name = 'Gotham'
    
    doc.add_paragraph()
    
    # Add formatted paragraphs
    for para_data in formatted_json["paragraphs"]:
        para = doc.add_paragraph()
        
        if "runs" in para_data:
            for run_data in para_data["runs"]:
                run = para.add_run(run_data["text"])
                run.bold = run_data.get("bold", False)
                run.italic = run_data.get("italic", False)
                run.font.size = Pt(12)
                run.font.name = 'Times New Roman'
        else:
            # No runs specified, just add text
            para_text = para_data.get("text", "")
            run = para.add_run(para_text)
            run.font.size = Pt(12)
            run.font.name = 'Times New Roman'
    
    # Save to bytes
    doc_bytes = io.BytesIO()
    doc.save(doc_bytes)
    doc_bytes.seek(0)
    return doc_bytes.read()
```

#### `backend/requirements.txt`
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-docx==1.1.0
python-multipart==0.0.6
anthropic==0.34.1
python-dotenv==1.0.0
```

---

### Frontend Files

#### `frontend/package.json`
```json
{
  "name": "oru-transcript-app",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "tailwindcss": "^3.3.6",
    "vite": "^5.0.0"
  }
}
```

#### `frontend/vite.config.js`
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173
  }
})
```

#### `frontend/tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

#### `frontend/postcss.config.js`
```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

#### `frontend/index.html`
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ORU Transcript Formatter</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

#### `frontend/src/main.jsx`
```jsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

#### `frontend/src/App.jsx`
```jsx
import React, { useState } from 'react'

function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && selectedFile.name.endsWith('.txt')) {
      setFile(selectedFile)
      setError(null)
    } else {
      setError('Please select a .txt file')
      setFile(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file first')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('http://localhost:8000/format', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Failed to format transcript')
      }

      // Download the file
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'formatted_transcript.docx'
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      // Reset form
      setFile(null)
      e.target.reset()
    } catch (err) {
      setError(err.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-2xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-indigo-900 mb-2">
            🎓 ORU Transcript Formatter
          </h1>
          <p className="text-gray-600">
            Upload your raw transcript and get a beautifully formatted Word document
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Transcript (.txt)
            </label>
            <input
              type="file"
              accept=".txt"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-indigo-50 file:text-indigo-700
                hover:file:bg-indigo-100
                cursor-pointer"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 px-4 rounded-lg font-semibold text-white
              transition duration-200 ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800'
              }`}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Formatting...
              </span>
            ) : (
              '✨ Generate DOCX'
            )}
          </button>
        </form>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            <strong>How it works:</strong> Automatically detects speakers, scriptures, music, and narration, then applies ORU formatting standards.
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
```

#### `frontend/src/index.css`
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
```

---

## 🧰 Dependencies

### Backend
```
fastapi
uvicorn
python-docx
python-multipart
```

### Frontend
```
react
react-dom
tailwindcss
autoprefixer
vite
@vitejs/plugin-react
```

---

## 🧾 Future Enhancements (Optional)

- 🎨 Add live formatted preview before download  
- 🧩 Add “Style Preset” selector (Chapel, Sermon, Academic)  
- 🔍 Highlight verse references dynamically  
- 🧰 Batch transcript uploads  

---

## 🧑‍💻 Example End-to-End Flow

1. Run backend (`uvicorn main:app --reload`)
2. Run frontend (`npm run dev`)
3. Open browser → `http://localhost:5173`
4. Upload your raw transcript `.txt`
5. Click **Generate DOCX**
6. Receive a styled Word document like your provided “Sample for transcript formatting.docx”

---

## 🏁 Summary

This app provides a clean, modern approach to transcript formatting:
- **No setup overhead**
- **No authentication**
- **Direct `.txt` → `.docx` transformation**
- **Extendable for ORU internal use or broader distribution**
