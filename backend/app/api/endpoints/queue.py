import asyncio
import logging
from fastapi import APIRouter, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.schemas import QueueResponse
from app.services import data_service
from app.core.dependencies import get_db
from app.db.models import Job
from app.core.auth import current_principal
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

PROCESSING_STATUSES = {"processing", "preprocessing", "inference", "postprocessing", "validation"}
COMPLETED_STATUSES = {"completed", "done"}

@router.get("/queue", response_model=QueueResponse)
async def queue(
    page: int = 1,
    status: str | None = None,
    project: str | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    db_jobs = None
    try:
        # Fetch real jobs from DB with short timeout so requests never hang if Postgres is offline
        query = select(Job).order_by(Job.created_at.desc())
        if settings.AUTH_ENABLED:
            query = query.where(Job.org_id == current_principal().org_id)
        if status and status != "all":
            if status == "completed":
                query = query.where(Job.status.in_(["completed", "done"]))
            elif status == "processing":
                query = query.where(Job.status.in_(list(PROCESSING_STATUSES)))
            else:
                query = query.where(Job.status == status)
            
        result = await asyncio.wait_for(db.execute(query), timeout=1.5)
        db_jobs = result.scalars().all()
    except Exception as exc:
        logger.warning(f"Database connection unavailable in /queue, falling back to mock jobs: {exc}")
        db_jobs = None

    # If DB is unavailable or has no jobs, fallback gracefully to data_service mock data
    if not db_jobs:
        jobs = list(data_service.QUEUE_JOBS)
        if status and status != "all":
            if status == "completed":
                jobs = [j for j in jobs if j.get("status") in COMPLETED_STATUSES]
            elif status == "processing":
                jobs = [j for j in jobs if j.get("status") in PROCESSING_STATUSES]
            else:
                jobs = [j for j in jobs if j.get("status") == status]
        if project and project != "all":
            jobs = [j for j in jobs if j.get("project") == project]
        if q:
            ql = q.lower()
            jobs = [
                j for j in jobs
                if ql in str(j.get("job_id", "")).lower() or ql in str(j.get("project", "")).lower()
            ]

        stats = data_service.QUEUE_STATS.copy()
        stats["queued"] = len([j for j in jobs if j.get("status") == "queued"])
        stats["processing"] = len([j for j in jobs if j.get("status") in PROCESSING_STATUSES])
        stats["completed_today"] = len([j for j in jobs if j.get("status") in COMPLETED_STATUSES])
        stats["failed"] = len([j for j in jobs if j.get("status") == "failed"])

        return {
            "stats": stats,
            "jobs": jobs,
            "cluster": data_service.CLUSTER,
            "total": len(jobs),
            "page": page,
            "rows_per_page": 10
        }

    # Map real jobs to the contract
    jobs = []
    for j in db_jobs:
        if q and q.lower() not in j.id.lower() and (not j.name or q.lower() not in j.name.lower()):
            continue
        if project and project != "all" and (j.project_id or "Unknown Project") != project:
            continue
            
        job_status = j.status
        if job_status == "done":
            job_status = "completed"

        jobs.append({
            "job_id": j.id,
            "project": j.project_id or "Unknown Project",
            "status": job_status,
            "date": j.created_at.strftime("%d %b %Y") if j.created_at else "",
            "resolution_gain": f"{j.target_resolution_m}m" if j.target_resolution_m else "4x",
            "progress": j.progress,
            "compute_node": "GPU-Worker-1",
            "gpu": "A100 40GB",
            "started": j.started_at.strftime("%d %b %Y %H:%M") if j.started_at else "—",
            "eta": "—",
            "lr_thumb": j.lr_image_key or "default",
            "sr_thumb": j.sr_image_key or "default",
            "tiles_processed": 0,
            "tiles_total": 0,
            "throughput_mbps": 0,
            "stages": []
        })

    # Stats
    stats = data_service.QUEUE_STATS.copy()
    stats["queued"] = len([j for j in jobs if j["status"] == "queued"])
    stats["processing"] = len([j for j in jobs if j["status"] in PROCESSING_STATUSES])
    stats["completed_today"] = len([j for j in jobs if j["status"] in COMPLETED_STATUSES])
    stats["failed"] = len([j for j in jobs if j["status"] == "failed"])

    return {
        "stats": stats,
        "jobs": jobs,
        "cluster": data_service.CLUSTER,
        "total": len(jobs),
        "page": page,
        "rows_per_page": 10
    }
