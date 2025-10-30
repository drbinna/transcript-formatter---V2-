from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from formatter import format_transcript
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="ORU Transcript Formatter")

# Serialize formatting requests to reduce rate/egress spikes in hosted envs
format_semaphore = asyncio.Semaphore(1)

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
    
    # Format the transcript (serialized to avoid bursts)
    async with format_semaphore:
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

@app.get("/debug/template")
async def debug_template():
    """Debug endpoint to check template file location"""
    import os
    from formatter import get_template_path
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    
    info = {
        "current_dir": current_dir,
        "root_dir": root_dir,
        "working_dir": os.getcwd(),
        "file_loc": __file__,
        "templates_dir_exists": os.path.exists(os.path.join(root_dir, 'templates')),
    }
    
    # Try to get template path
    try:
        template_path = get_template_path()
        info["template_path"] = template_path
        info["template_exists"] = os.path.exists(template_path)
    except Exception as e:
        info["error"] = str(e)
    
    return info

# Mount static files at the end - this will serve index.html and all assets
static_dir = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(static_dir):
    # Mount the dist folder - html=True will serve index.html for /
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

