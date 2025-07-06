from fastapi import APIRouter, Request, File, UploadFile
from fastapi.responses import Response
from core.schema.api_response import ApiResponse
from src.app.controllers.storage_controller import list_file, list_chunk_private, upload_file_to_s3_ver2, list_chunk_public

router = APIRouter(tags=["file-split"])


@router.get('', response_model=ApiResponse)
async def get_list_file():
    results = await list_file()
    return {"data": results}


@router.get("/{id}", response_model=ApiResponse)
async def get_list_chunk_public(id: str):
    return await list_chunk_public(id)


@router.post('', response_model=ApiResponse)
async def upload(
    request: Request,
    file: UploadFile = File(...),
):
    message = await upload_file_to_s3_ver2(file)
    return {"message": message}


@router.get("/{id}/playlist")
async def get_list_chunk(id: str):
    result = await list_chunk_private(id=id)
    if result.get("status_code") == 200:
        return Response(content=result.get("data"), media_type="application/vnd.apple.mpegurl")
    return Response(status_code=result.get("status_code"), content=result.get("message"))
