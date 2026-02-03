import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse

from app.config import UPLOAD_DIR, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K, MAX_PAGES, MAX_FILE_SIZE_MB, SIMILARITY_THRESHOLD
from app.pdf_reader import load_pdf
from app.text_splitter import split_text
from app.faiss_db import create_or_update_faiss, load_faiss_index, search_faiss_with_score
from app.llm import get_llm_response
from app.formatter import format_text

app = FastAPI(title="PDF Chatbot")

os.makedirs(UPLOAD_DIR, exist_ok=True)

faiss_index = load_faiss_index()


@app.post("/upload-multiple")
async def upload_pdfs(files: list[UploadFile] = File()):
    global faiss_index
    total_chunks = 0

    MAX_FILE_SIZE_MB = 50
    MIN_PAGES = 1
    MAX_PAGEX = 500

    try:
        for file in files:
            if not file.filename.lower().endswith(".pdf"):
                continue

            content = await file.read()
            if len(content) > MAX_FILE_SIZE_MB * 1024 * 1024:
                return JSONResponse(
                    {"error": f"{file.filename} exceeds {MAX_FILE_SIZE_MB} MB limit."},
                    status_code=400
                )
            await file.seek(0) 

            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as f:
                f.write(await file.read())

        
            pages = load_pdf(file_path)
            if not pages:
                continue
            
            num_pages = len(pages)
            if num_pages < MIN_PAGES or num_pages > MAX_PAGES:
                return JSONResponse(
                    {
                        "error": f"{file.filename} has {num_pages} pages. "
                                 f"Allowed range: {MIN_PAGES}-{MAX_PAGES}."
                    },
                    status_code=400
                )

            full_text = "\n\n".join(
                [page["text"] for page in pages if page["text"].strip()]
            )

            if not full_text.strip():
                continue

            chunks = split_text(full_text, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            chunks_with_meta = [
                { 
                    "text": c,
                    "metadata": {
                        "source": file.filename,
                        "chunk_id": i
                    }
                }
                    for i, c in enumerate(chunks)
            ]
            
            faiss_index = create_or_update_faiss(chunks_with_meta, existing_index=faiss_index)
            total_chunks += len(chunks)

        if total_chunks == 0:
            return JSONResponse({"error": "No valid PDFs uploaded."}, status_code=400)

        return {"message":  "PDFs uploaded and indexed.", "total_chunks": total_chunks}

    except Exception as e:
        return JSONResponse({"error": f"Upload failed: {str(e)}"}, status_code=500)

@app.post("/ask")
async def ask_question(question: str = Form()):
    global faiss_index
    if not faiss_index:
        faiss_index = load_faiss_index()
    if not question.strip():
        return JSONResponse({"error": "Question cannot be empty."}, status_code=400)

    try:
        retrieved = search_faiss_with_score(faiss_index, question, TOP_K)
        contexts = [chunk for chunk, score, meta in retrieved if chunk.strip()]

        if len(contexts) == 0:
            return {"answer": "Sorry, the requested information is not available in the provided PDF.",
                    "used_pdf_context": False}

       
        context_text_from_faiss = "\n\n---\n\n".join(contexts)
        context_text = f"Question: {question}\n\nContext:\n{context_text_from_faiss}"

        
        raw_answer = get_llm_response(context_text)

        
        unwanted_phrases = ["(as described in the provided context)"]
        for phrase in unwanted_phrases:
            raw_answer = raw_answer.replace(phrase, "")

        answer = format_text(raw_answer.strip())

        if "sorry" in raw_answer.lower() or "not available" in raw_answer.lower():
            pdf_used = False
        else:
            pdf_used = True

        return {
            "answer": answer,
            "used_pdf_context": pdf_used
    }

    except Exception as e:
        return JSONResponse(
            {"error": f"Question processing failed: {str(e)}"}, 
            status_code=500
        )
























































































































































































































