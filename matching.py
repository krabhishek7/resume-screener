from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.db.mongodb import get_database
from app.services.matching_engine import MatchingEngine
from app.models.job_model import JobModel
from app.models.resume_model import ResumeModel
from app.schemas.matching import MatchingResult, MatchingRequest

router = APIRouter()


@router.post("/match-job", response_model=List[MatchingResult])
async def match_job_with_resumes(
    matching_request: MatchingRequest,
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    limit: int = Query(10, ge=1, le=100),
    db = Depends(get_database)
):
    """
    Match a job with suitable resumes
    """
    job_model = JobModel(db)
    resume_model = ResumeModel(db)
    
    # Get job information
    job = await job_model.get_by_id(matching_request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Get resumes
    resumes = await resume_model.get_all(limit=1000)  # Get a larger set to filter
    
    # Initialize matching engine
    matching_engine = MatchingEngine()
    
    # Get matching results
    results = await matching_engine.match_job_with_resumes(
        job=job,
        resumes=resumes,
        min_score=min_score
    )
    
    # Sort by score (descending) and limit results
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:limit]
    
    return results


@router.post("/match-resume", response_model=List[MatchingResult])
async def match_resume_with_jobs(
    matching_request: MatchingRequest,
    min_score: float = Query(0.5, ge=0.0, le=1.0),
    limit: int = Query(10, ge=1, le=100),
    db = Depends(get_database)
):
    """
    Match a resume with suitable jobs
    """
    job_model = JobModel(db)
    resume_model = ResumeModel(db)
    
    # Get resume information
    resume = await resume_model.get_by_id(matching_request.resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Get active jobs
    jobs = await job_model.get_all(filters={"is_active": True})
    
    # Initialize matching engine
    matching_engine = MatchingEngine()
    
    # Get matching results
    results = await matching_engine.match_resume_with_jobs(
        resume=resume,
        jobs=jobs,
        min_score=min_score
    )
    
    # Sort by score (descending) and limit results
    results.sort(key=lambda x: x["score"], reverse=True)
    results = results[:limit]
    
    return results 