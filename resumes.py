import os
import uuid
import shutil
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.resume_parser import ResumeParser
from app.db.mongodb import get_database
from app.schemas.resume import ResumeResponse, ResumeCreate
from app.models.resume_model import ResumeModel

router = APIRouter()


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    candidate_name: str = Form(None),
    candidate_email: str = Form(None),
    test_upload: bool = Form(False),
    db = Depends(get_database)
):
    """
    Upload and parse a resume file (PDF or DOC/DOCX)
    """
    try:
        # Print debug information
        print(f"Received file upload: {file.filename}, size: {file.size if hasattr(file, 'size') else 'unknown'}")
        print(f"Form data: name={candidate_name}, email={candidate_email}, test={test_upload}")
        
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file provided or filename is empty"
            )
        
        # For test uploads, we'll allow txt files
        allowed_extensions = settings.ALLOWED_EXTENSIONS.copy()
        if test_upload:
            allowed_extensions.append("txt")
            print(f"Test upload detected - allowing extensions: {allowed_extensions}")
        
        # Validate file extension
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file format. Allowed formats: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            )
        
        # If this is just a test upload, return early with simplified response
        if test_upload and file_ext == "txt":
            print("Processing test upload - returning test response")
            return {
                "id": "test-id-123",
                "filename": file.filename,
                "parsed_data": {
                    "name": candidate_name or "Test User",
                    "email": candidate_email or "test@example.com",
                    "test": True
                },
                "message": "Test upload successful"
            }
            
        # Continue with regular upload processing
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save the file
        print(f"Saving file to: {file_path}")
        try:
            # Method 1: Using .read() and write
            contents = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(contents)
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            # Method 2: Using shutil as fallback
            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
            except Exception as e2:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to save uploaded file: {str(e2)}"
                )
        
        # Parse the resume in the background to avoid timeout
        parser = ResumeParser(file_path)
        
        # Parse immediately if small file, otherwise do in background
        if os.path.getsize(file_path) < 1024 * 1024:  # 1MB
            parsed_data = await parser.parse()
        else:
            # For larger files, use a placeholder and update later
            parsed_data = {
                "name": candidate_name or "Processing...",
                "email": candidate_email or "Processing...",
                "processing": True
            }
            # Add background task for processing
            background_tasks.add_task(
                process_resume_background, file_path, db, unique_filename
            )
        
        # Override parsed data with form data if provided
        if candidate_name:
            parsed_data["name"] = candidate_name
        if candidate_email:
            parsed_data["email"] = candidate_email
        
        # Create resume object
        resume_data = ResumeCreate(
            file_path=file_path,
            original_filename=file.filename,
            parsed_data=parsed_data
        )
        
        # Save resume to database
        resume_model = ResumeModel(db)
        resume_id = await resume_model.create(resume_data.dict())
        
        return {
            "id": resume_id,
            "filename": file.filename,
            "parsed_data": parsed_data,
            "message": "Resume uploaded and parsed successfully"
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        print(f"Unexpected error during file upload: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


async def process_resume_background(file_path: str, db, resume_id: str):
    """Process resume in background to prevent timeout"""
    try:
        # Parse the resume
        parser = ResumeParser(file_path)
        parsed_data = await parser.parse()
        
        # Update the database with parsed data
        resume_model = ResumeModel(db)
        await resume_model.update(
            resume_id,
            {"parsed_data": parsed_data, "processing_complete": True}
        )
    except Exception as e:
        print(f"Background processing error for {resume_id}: {str(e)}")


# Allow preflight requests for the upload endpoint
@router.options("/upload")
async def upload_resume_options():
    return {}


@router.get("/", response_model=List[ResumeResponse])
async def get_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db = Depends(get_database)
):
    """
    Get a list of uploaded resumes
    """
    resume_model = ResumeModel(db)
    resumes = await resume_model.get_all(skip=skip, limit=limit)
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str, db = Depends(get_database)):
    """
    Get a specific resume by ID
    """
    resume_model = ResumeModel(db)
    resume = await resume_model.get_by_id(resume_id)
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return resume


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, db = Depends(get_database)):
    """
    Delete a resume from the system
    """
    resume_model = ResumeModel(db)
    resume = await resume_model.get_by_id(resume_id)
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file from filesystem
    if os.path.exists(resume["file_path"]):
        os.remove(resume["file_path"])
    
    # Delete from database
    await resume_model.delete(resume_id)
    
    return JSONResponse(content={"message": "Resume deleted successfully"}) 