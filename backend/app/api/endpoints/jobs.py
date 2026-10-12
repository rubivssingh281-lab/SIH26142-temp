import random
import math
import datetime
import asyncio
import logging
from datetime import date
from typing import Optional
from fastapi import APIRouter, Request, UploadFile, File, Query, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from app.schemas import NewJobEstimate, JobStatus
from app.services.job_service import JobService
from app.services import data_service
from app.services.email_service import send_job_notification_email
from app.api.endpoints.notifications import add_in_app_notification
from app.repository.storage import StorageRepository, object_storage
from app.core.config import settings
from app.core.auth import current_principal
from app.core.errors import APIError
from app.core.dependencies import get_db
from app.db.models import Job

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/jobs/estimate", response_model=NewJobEstimate)
async def estimate(body: dict):
    area = float(body.get("area_km2", 12.64))
    minutes = max(20, round(area * 11))
    return {
        "area_km2": round(area, 2),
        "estimated_time": f"{minutes // 60}h {minutes % 60:02d}m",
        "estimated_storage_gb": round(area * 3.85, 1)
    }

@router.post("/jobs", status_code=201)
async def submit_job(request: Request, db: AsyncSession = Depends(get_db)):
    content_type = request.headers.get("content-type", "")

    # Branch 1: Multipart file upload (GeoTIFF)
    if "multipart/form-data" in content_type:
        form = await request.form()
        file = form.get("file")
        if not file or not isinstance(file, UploadFile):
            raise APIError(400, "missing_file", "File field required for multipart uploads")

        chunks = []
        total_bytes = 0
        while True:
            chunk = await file.read(min(1024 * 1024, settings.MAX_UPLOAD_BYTES + 1 - total_bytes))
            if not chunk:
                break
            chunks.append(chunk)
            total_bytes += len(chunk)
            if total_bytes > settings.MAX_UPLOAD_BYTES:
                raise APIError(413, "oversized", "Uploaded file exceeds the maximum allowed size")

        file_bytes = b"".join(chunks)
        try:
            job_id = await JobService.create_job(db, file.filename, file_bytes)
        except ValueError as e:
            if str(e) == "corrupt_file":
                raise APIError(400, "corrupt_file", "Uploaded file must be a valid GeoTIFF (.tif or .tiff)")
            if str(e) == "oversized":
                raise APIError(413, "oversized", "Uploaded file exceeds the configured upload or raster limits")
            if str(e) == "missing_bands":
                raise APIError(400, "missing_bands", "Uploaded raster contains too many bands")
            raise APIError(500, "internal_error", str(e))

        # Dispatch SMTP notification
        job_info = {
            "job_id": job_id,
            "project": "Custom GeoTIFF Upload",
            "resolution_gain": "4x (10m → 2.5m)",
            "model": "TerraSharp v2.1 (GAN)",
            "compute_node": "GPU-Node-01 (NVIDIA A100)",
        }
        try:
            asyncio.create_task(asyncio.to_thread(send_job_notification_email, settings.SMTP_FROM_EMAIL, job_info, "queued"))
        except Exception:
            logger.exception("smtp_notification_failed_for_uploaded_job")

        add_in_app_notification({
            "id": f"notif-{job_id}",
            "type": "info",
            "title": f"Job {job_id} Queued",
            "message": f"GeoTIFF {file.filename} accepted and queued for inference.",
            "time": "Just now",
            "read": False,
            "href": "/queue",
            "tag": "Processing",
        })

        return {"job_id": job_id, "status": "queued"}

    # Branch 2: JSON payload from Frontend wizard (NewJobPayload)
    try:
        body = await request.json()
    except Exception:
        body = {}
    project = body.get("project", "Ladakh Border Infrastructure")
    job_name = body.get("job_name", "SR_v2_job")
    model = body.get("model", "gan").upper()
    target_res = body.get("target_resolution_m", 2.5)
    source = body.get("satellite_source", "sentinel-2")
    bands = body.get("bands", ["RGB", "NIR"])

    stamp = datetime.datetime.now().strftime("%Y%m%d")
    rand = random.randint(1000, 8999)
    job_id = f"SR_v2_{stamp}_{rand}"

    now = datetime.datetime.now()
    now_str = now.strftime("%d %b %Y %I:%M %p")
    date_str = now.strftime("%d %b %Y")

    new_job = {
        "job_id": job_id,
        "project": project,
        "status": "processing",
        "date": date_str,
        "resolution_gain": f"4x (10m → {target_res}m)",
        "progress": 25,
        "compute_node": "GPU-Node-01",
        "gpu": "A100 40GB",
        "started": now_str,
        "eta": "~18 min",
        "lr_thumb": "ladakh-01",
        "sr_thumb": "ladakh-01",
        "tiles_processed": 240,
        "tiles_total": 1280,
        "throughput_mbps": 320,
        "stages": [
            {"name": "Pre-processing", "state": "completed", "detail": "Completed · Cloud masking passed"},
            {"name": "Model Inference", "state": "in_progress", "detail": f"In Progress ({model})", "progress": 25},
            {"name": "Post-processing", "state": "pending", "detail": "Pending"},
            {"name": "Validation", "state": "pending", "detail": "Pending"},
        ]
    }

    # Prepend to active queue so user sees their new job immediately in UI
    data_service.QUEUE_JOBS.insert(0, new_job)
    data_service.QUEUE_STATS["processing"] = data_service.QUEUE_STATS.get("processing", 0) + 1
    data_service.DASHBOARD["stats"]["total_jobs"] = data_service.DASHBOARD["stats"].get("total_jobs", 0) + 1

    # Update recent job preview on dashboard
    data_service.DASHBOARD["recent_job"] = {
        "job_id": job_id,
        "status": "processing",
        "area_km2": 12.6,
        "location": "34.2345° N, 77.5612° E",
        "acquisition_date": date_str,
        "model": f"TerraSharp v2.1 ({model})",
        "resolution_gain": f"4x (10m → {target_res}m)",
        "lr_image": "ladakh-urban",
        "sr_image": "ladakh-urban",
        "uncertainty_image": "ladakh-urban",
        "lr_resolution": "10 m / pixel",
        "sr_resolution": f"{target_res} m / pixel",
    }

    # Dispatch SMTP notification via background task
    try:
        asyncio.create_task(
            asyncio.to_thread(
                send_job_notification_email,
                settings.SMTP_FROM_EMAIL,
                new_job,
                "created"
            )
        )
    except Exception as exc:
        logger.warning(f"Could not dispatch SMTP job created notification: {exc}")

    # Add in-app notification
    add_in_app_notification({
        "id": f"notif-{job_id}",
        "type": "info",
        "title": f"Job {job_id} Scheduled",
        "message": f"Inference job created for {project} (Sensor: {source}, Target: {target_res}m).",
        "time": "Just now",
        "read": False,
        "href": f"/queue",
        "tag": "Inference",
    })

    return {
        "job_id": job_id,
        "status": "queued",
        "submitted": job_name,
    }

@router.post("/jobs/{job_id}/simulate-complete")
async def simulate_complete_job(job_id: str):
    job = next((j for j in data_service.QUEUE_JOBS if j["job_id"] == job_id), None)
    if not job:
        job = {
            "job_id": job_id,
            "project": "Ladakh Border Infrastructure",
            "status": "completed",
            "date": datetime.datetime.now().strftime("%d %b %Y"),
            "resolution_gain": "4x (10m → 2.5m)",
            "progress": 100,
            "compute_node": "GPU-Node-01",
            "gpu": "A100 40GB",
            "started": datetime.datetime.now().strftime("%d %b %Y %I:%M %p"),
            "eta": "Completed",
            "lr_thumb": "ladakh-01",
            "sr_thumb": "ladakh-01",
            "tiles_processed": 1280,
            "tiles_total": 1280,
            "throughput_mbps": 340,
            "stages": [
                {"name": "Pre-processing", "state": "completed", "detail": "Completed"},
                {"name": "Model Inference", "state": "completed", "detail": "Completed · PSNR: 34.58 dB"},
                {"name": "Post-processing", "state": "completed", "detail": "Completed"},
                {"name": "Validation", "state": "completed", "detail": "Completed · SSIM: 0.912"},
            ]
        }
        data_service.QUEUE_JOBS.insert(0, job)
    else:
        job["status"] = "completed"
        job["progress"] = 100
        job["eta"] = "Completed"
        if "stages" in job:
            for s in job["stages"]:
                s["state"] = "completed"

    data_service.QUEUE_STATS["completed_today"] = data_service.QUEUE_STATS.get("completed_today", 0) + 1
    data_service.QUEUE_STATS["processing"] = max(0, data_service.QUEUE_STATS.get("processing", 1) - 1)

    # Dispatch SMTP completion email
    try:
        await asyncio.to_thread(send_job_notification_email, settings.SMTP_FROM_EMAIL, job, "completed")
    except Exception as exc:
        logger.warning(f"Could not dispatch SMTP job completed notification: {exc}")

    add_in_app_notification({
        "id": f"notif-complete-{job_id}",
        "type": "success",
        "title": f"Job {job_id} Completed",
        "message": f"Super-resolution finished. Imagery and validation metrics available.",
        "time": "Just now",
        "read": False,
        "href": f"/comparison?job={job_id}",
        "tag": "Completed",
    })

    return {"status": "ok", "job": job}

@router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    global data_service
    data_service.QUEUE_JOBS = [j for j in data_service.QUEUE_JOBS if j["job_id"] != job_id]
    return {"status": "ok", "message": f"Job {job_id} cancelled"}

@router.get("/jobs")
async def list_jobs(page: int = 1, limit: int = 10, status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    db_jobs = []
    try:
        query = select(Job).order_by(Job.created_at.desc())
        count_query = select(func.count(Job.id))

        if settings.AUTH_ENABLED:
            org_id = current_principal().org_id
            query = query.where(Job.org_id == org_id)
            count_query = count_query.where(Job.org_id == org_id)

        if status:
            query = query.where(Job.status == status)
            count_query = count_query.where(Job.status == status)

        query = query.limit(limit).offset((page - 1) * limit)
        result = await asyncio.wait_for(db.execute(query), timeout=1.5)
        db_jobs = result.scalars().all()
    except Exception:
        db_jobs = []

    if not db_jobs:
        # Graceful fallback to data_service jobs
        jobs_list = [
            {
                "id": j["job_id"],
                "status": j["status"],
                "stage": "inference" if j["status"] == "processing" else "done",
                "progress": j.get("progress", 0),
                "model": j.get("resolution_gain", "4x"),
                "error_code": None,
                "error_message": None,
            }
            for j in data_service.QUEUE_JOBS
        ]
        return {
            "jobs": jobs_list,
            "page": page,
            "total": len(jobs_list),
            "rows_per_page": limit,
        }

    jobs_list = []
    for job in db_jobs:
        jobs_list.append({
            "id": job.id,
            "status": job.status,
            "stage": job.stage,
            "progress": job.progress,
            "model": job.model,
            "error_code": job.error_code,
            "error_message": job.error_message,
        })

    return {
        "jobs": jobs_list,
        "page": page,
        "total": len(jobs_list),
        "rows_per_page": limit,
    }

@router.get("/jobs/{job_id}")
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    job = None
    try:
        job = await asyncio.wait_for(StorageRepository.get_job(db, job_id), timeout=1.5)
    except Exception:
        job = None

    if not job:
        # Check data_service
        mock_job = next((j for j in data_service.QUEUE_JOBS if j["job_id"] == job_id), None)
        if mock_job:
            return {
                "id": mock_job["job_id"],
                "status": mock_job["status"],
                "stage": "inference",
                "progress": mock_job.get("progress", 0),
                "model": "TerraSharp v2.1",
                "error_code": None,
                "error_message": None,
                "lr_image_url": None,
            }
        raise APIError(404, "not_found", "Job not found")

    lr_url = object_storage.get_presigned_url(job_id, job.lr_image_key) if job.lr_image_key else None

    return {
        "id": job.id,
        "status": job.status,
        "stage": job.stage,
        "progress": job.progress,
        "model": job.model,
        "error_code": job.error_code,
        "error_message": job.error_message,
        "lr_image_url": lr_url
    }

class ConfigPayload(BaseModel):
    model: str
    target_resolution_m: float
    bands: list[str]
    aoi_coordinates: list[list[float]]

@router.patch("/jobs/{job_id}/config")
async def patch_config(job_id: str, config: ConfigPayload, db: AsyncSession = Depends(get_db)):
    success, reason = await JobService.patch_config(db, job_id, config.dict())
    if not success:
        if reason == "not_found":
            raise APIError(404, "not_found", "Job not found")
        elif reason == "not_ready":
            raise APIError(409, "not_ready", "Job is not in 'created' state")
    return {"status": "ok"}

@router.post("/jobs/{job_id}/run", status_code=202)
async def run_job(job_id: str, db: AsyncSession = Depends(get_db)):
    success, reason = await JobService.enqueue_job(db, job_id)
    if not success:
        if reason == "not_found":
            raise APIError(404, "not_found", "Job not found")
        elif reason == "not_ready":
            raise APIError(409, "not_ready", "Job is not in 'created' state")
    return {"status": "queued"}
