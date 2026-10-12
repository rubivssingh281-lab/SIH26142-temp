import copy
from fastapi import APIRouter
from app.schemas import SettingsResponse
from app.services import data_service

router = APIRouter()

_settings = copy.deepcopy(data_service.SETTINGS)

@router.get("/settings", response_model=SettingsResponse)
def get_settings():
    return _settings

@router.put("/settings", response_model=SettingsResponse)
async def put_settings(body: dict):
    # Update known and extended fields
    for k, v in body.items():
        _settings[k] = v
    return _settings
