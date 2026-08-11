# This route is responsible for using rag tool where user is going to upload the documents
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from database import create_or_update_conservation
from rag import add_document_to_vector_store

uploaddocumentroute = APIRouter()

@uploaddocumentroute.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    thread_id: str = Form(...)
    ):
    try:
        allowed_extensions = ['.pdf', '.txt', '.docx', '.md', '.py', '.csv']

        filename = file.filename or "uploaded_file"
        suffix = Path(filename).suffix.lower()

        if suffix not in allowed_extensions:
            return JSONResponse(
                {
                    "success": False,
                    "message": "Unsupported file format. Upload only .pdf, .txt, .docx', .md, .py, .csv files"
                },
                status_code=400
            )

        file_id = str(uuid.uuid4())
        safe_filename = filename.replace(" ","_")
        file_path = f"Uploads/{file_id}_{safe_filename}"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        create_or_update_conservation(first_message="Uploaded documents",thread_id=thread_id)

        result = add_document_to_vector_store(
            file_path=file_path,
            thread_id=thread_id
        )

        return JSONResponse({
            "success": True,
            "message": f"Uploaded {result['filename']} and created {result['chunks']} chunks."
        })

    except Exception as e:
        return JSONResponse(
            {
                "success": False,
                "message": str(e)
            },
            status_code=500
        )