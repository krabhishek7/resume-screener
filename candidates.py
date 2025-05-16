from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from app.db.mongodb import get_database
from app.schemas.candidate import CandidateCreate, CandidateResponse, CandidateUpdate
from app.models.candidate_model import CandidateModel
from app.models.resume_model import ResumeModel

router = APIRouter()


@router.post("/", response_model=CandidateResponse)
async def create_candidate(candidate: CandidateCreate, db = Depends(get_database)):
    """
    Create a new candidate
    """
    # Verify resume exists if resume_id is provided
    if candidate.resume_id:
        resume_model = ResumeModel(db)
        resume = await resume_model.get_by_id(candidate.resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
    
    candidate_model = CandidateModel(db)
    candidate_id = await candidate_model.create(candidate.dict())
    
    return await candidate_model.get_by_id(candidate_id)


@router.get("/", response_model=List[CandidateResponse])
async def get_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    email: Optional[str] = None,
    skill: Optional[str] = None,
    db = Depends(get_database)
):
    """
    Get a list of candidates with optional filtering
    """
    candidate_model = CandidateModel(db)
    
    # Build filter dictionary based on query parameters
    filters = {}
    if name:
        filters["name"] = {"$regex": name, "$options": "i"}
    if email:
        filters["email"] = {"$regex": email, "$options": "i"}
    if skill:
        filters["skills"] = {"$in": [skill]}
    
    candidates = await candidate_model.get_all(filters=filters, skip=skip, limit=limit)
    return candidates


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: str, db = Depends(get_database)):
    """
    Get a specific candidate by ID
    """
    candidate_model = CandidateModel(db)
    candidate = await candidate_model.get_by_id(candidate_id)
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
async def update_candidate(candidate_id: str, candidate_update: CandidateUpdate, db = Depends(get_database)):
    """
    Update a candidate
    """
    candidate_model = CandidateModel(db)
    candidate = await candidate_model.get_by_id(candidate_id)
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    # Verify resume exists if resume_id is updated
    if candidate_update.resume_id:
        resume_model = ResumeModel(db)
        resume = await resume_model.get_by_id(candidate_update.resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
    
    # Update candidate
    updated_candidate = await candidate_model.update(
        candidate_id, 
        candidate_update.dict(exclude_unset=True)
    )
    
    return updated_candidate


@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: str, db = Depends(get_database)):
    """
    Delete a candidate
    """
    candidate_model = CandidateModel(db)
    candidate = await candidate_model.get_by_id(candidate_id)
    
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    await candidate_model.delete(candidate_id)
    
    return JSONResponse(content={"message": "Candidate deleted successfully"}) 