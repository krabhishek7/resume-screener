from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from app.db.mongodb import get_database
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.models.job_model import JobModel

router = APIRouter()


@router.post("/", response_model=JobResponse)
async def create_job(job: JobCreate, db = Depends(get_database)):
    """
    Create a new job posting
    """
    job_model = JobModel(db)
    job_id = await job_model.create(job.dict())
    
    return await job_model.get_by_id(job_id)


@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    title: Optional[str] = None,
    department: Optional[str] = None,
    active: Optional[bool] = None,
    db = Depends(get_database)
):
    """
    Get a list of job postings with optional filtering
    """
    job_model = JobModel(db)
    
    # Build filter dictionary based on query parameters
    filters = {}
    if title:
        filters["title"] = {"$regex": title, "$options": "i"}
    if department:
        filters["department"] = department
    if active is not None:
        filters["is_active"] = active
    
    jobs = await job_model.get_all(filters=filters, skip=skip, limit=limit)
    return jobs


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, db = Depends(get_database)):
    """
    Get a specific job posting by ID
    """
    job_model = JobModel(db)
    job = await job_model.get_by_id(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job


@router.put("/{job_id}", response_model=JobResponse)
async def update_job(job_id: str, job_update: JobUpdate, db = Depends(get_database)):
    """
    Update a job posting
    """
    job_model = JobModel(db)
    job = await job_model.get_by_id(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Update job
    updated_job = await job_model.update(job_id, job_update.dict(exclude_unset=True))
    
    return updated_job


@router.delete("/{job_id}")
async def delete_job(job_id: str, db = Depends(get_database)):
    """
    Delete a job posting
    """
    job_model = JobModel(db)
    job = await job_model.get_by_id(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    await job_model.delete(job_id)
    
    return JSONResponse(content={"message": "Job deleted successfully"}) 