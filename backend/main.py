from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
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

@app.get("/api")
async def api_info():
    return {"message": "ORU Transcript Formatting API", "version": "1.0"}

# Mount static files at the end - this will serve index.html and all assets
static_dir = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(static_dir):
    # Mount the dist folder - html=True will serve index.html for /
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

