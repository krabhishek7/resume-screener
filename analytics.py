from typing import Dict, List, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime, timedelta

from app.db.mongodb import get_database
from app.models.resume_model import ResumeModel
from app.models.job_model import JobModel
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard_metrics(db = Depends(get_database)):
    """
    Get main dashboard metrics and KPIs
    """
    resume_model = ResumeModel(db)
    job_model = JobModel(db)
    analytics_service = AnalyticsService(db)
    
    # Get counts
    resume_count = await resume_model.count({})
    job_count = await job_model.count({})
    active_job_count = await job_model.count({"is_active": True})
    
    # Get recent activity
    recent_resumes = await resume_model.get_all(
        limit=5, 
        sort=[("created_at", -1)]
    )
    
    # Get skill distribution
    skill_distribution = await analytics_service.get_skill_distribution()
    
    # Get matching metrics 
    matching_metrics = await analytics_service.get_matching_metrics()
    
    return {
        "counts": {
            "resumes": resume_count,
            "jobs": job_count,
            "active_jobs": active_job_count,
        },
        "recent_activity": {
            "resumes": recent_resumes
        },
        "skill_distribution": skill_distribution,
        "matching_metrics": matching_metrics
    }


@router.get("/skills")
async def get_skill_analytics(
    time_period: str = Query("all", enum=["week", "month", "year", "all"]),
    db = Depends(get_database)
):
    """
    Get analytics about skills across resumes
    """
    analytics_service = AnalyticsService(db)
    
    # Define date filter based on time period
    date_filter = {}
    if time_period != "all":
        now = datetime.utcnow()
        if time_period == "week":
            date_filter = {"created_at": {"$gte": now - timedelta(days=7)}}
        elif time_period == "month":
            date_filter = {"created_at": {"$gte": now - timedelta(days=30)}}
        elif time_period == "year":
            date_filter = {"created_at": {"$gte": now - timedelta(days=365)}}
    
    skill_analytics = await analytics_service.get_skill_analytics(date_filter)
    
    return skill_analytics


@router.get("/jobs/{job_id}/candidates")
async def get_job_candidate_analytics(job_id: str, db = Depends(get_database)):
    """
    Get analytics about candidates for a specific job
    """
    job_model = JobModel(db)
    job = await job_model.get_by_id(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    analytics_service = AnalyticsService(db)
    candidate_analytics = await analytics_service.get_job_candidate_analytics(job_id)
    
    return candidate_analytics


@router.get("/candidates/distribution")
async def get_candidate_distribution(db = Depends(get_database)):
    """
    Get distribution of candidates by different dimensions
    """
    analytics_service = AnalyticsService(db)
    
    education_distribution = await analytics_service.get_education_distribution()
    experience_distribution = await analytics_service.get_experience_distribution()
    location_distribution = await analytics_service.get_location_distribution()
    
    return {
        "education": education_distribution,
        "experience": experience_distribution,
        "location": location_distribution
    } 