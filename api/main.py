# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from llm.langgraph_handler import analyze_image_with_langgraph

app = FastAPI()

# CORS設定はそのまま
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result_text = analyze_image_with_langgraph(image_bytes)
    return {"content": result_text}
