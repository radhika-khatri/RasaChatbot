from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import os
import json
from .model_utils import html_to_structured_json_by_blocks, generate_response_from_structured_json

app = FastAPI()
TEMP_OUTPUT_PATH = "data/temp/structured_output.json"

@app.post("/upload/")
async def upload_html_file(file: UploadFile = File(...)):
    html_content = await file.read()
    sections = html_to_structured_json_by_blocks(html_content)
    os.makedirs(os.path.dirname(TEMP_OUTPUT_PATH), exist_ok=True)
    with open(TEMP_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(sections, f, indent=2, ensure_ascii=False)
    return {"message": "✅ HTML processed and structured JSON saved.", "sections": len(sections)}

@app.post("/query/")
async def ask_question(query: str = Form(...)):
    if not os.path.exists(TEMP_OUTPUT_PATH):
        return JSONResponse(status_code=400, content={"error": "No structured data found. Please upload HTML first."})
    with open(TEMP_OUTPUT_PATH, "r", encoding="utf-8") as f:
        structured_data = json.load(f)
    response_text, image_urls = generate_response_from_structured_json(query, structured_data)
    if not response_text:
        return {"response": "I couldn’t find anything relevant.", "images": []}
    return {"response": response_text, "images": image_urls}
