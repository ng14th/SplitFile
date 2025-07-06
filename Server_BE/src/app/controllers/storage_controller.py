import subprocess
from src.app.schemas import *
from src.app.models import Storage, ChunkStorage
from core.minio_manage import MinIOClient, get_minio_client

from fastapi import UploadFile
from tempfile import TemporaryDirectory
from uuid import uuid4
import os
import ffmpeg

minio_client = get_minio_client()


async def get_duration(file_path: str) -> float:
    try:
        probe = ffmpeg.probe(file_path)
        return float(probe["format"]["duration"])
    except Exception as e:
        return 0.0  # fallback nếu lỗi


async def upload_file_to_s3(file: UploadFile):

    name_generated = str(uuid4())

    # Tạo thư mục tạm
    with TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, f"{name_generated}.mp4")
        output_pattern = os.path.join(temp_dir, "chunk_%03d.mp4")

        # Ghi file tạm
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # FFmpeg command để chia video
        command = [
            "ffmpeg",
            "-i", input_path,
            "-c", "copy",
            "-map", "0",
            "-f", "segment",
            "-segment_time", "10",
            "-reset_timestamps", "1",
            "-movflags", "+frag_keyframe+empty_moov",  # ✅ thêm flag này
            output_pattern
        ]

        subprocess.run(command, check=True)

        # Lấy danh sách file đã chia nhỏ
        chunk_files = sorted(
            f for f in os.listdir(temp_dir) if f.startswith("chunk_") and f.endswith(".mp4")
        )

        uploaded_files = []

        # Đảm bảo bucket tồn tại

        # Upload từng file chunk
        for chunk_file in chunk_files:
            file_path = os.path.join(temp_dir, chunk_file)
            object_name = f"{name_generated}/{chunk_file}"
            await minio_client.fput_object(object_name, file_path)
            uploaded_files.append(chunk_file)

    new_file = await Storage.create(
        name=file.filename,
        location_path=name_generated
    )

    await ChunkStorage.bulk_create(
        [
            ChunkStorage(
                name=chunk_file,
                storage=new_file
            )
            for chunk_file in uploaded_files
        ]
    )

    return "File uploaded successfully"


async def upload_file_to_s3_ver2(file: UploadFile):
    name_generated = str(uuid4())
    name_file_m3u8 = f"{name_generated}_index.m3u8"

    with TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, f"{name_generated}.mp4")
        segment_pattern = os.path.join(
            temp_dir,
            f"{name_generated}_chunk_%03d.ts"
        )
        m3u8_path = os.path.join(temp_dir, name_file_m3u8)

        # Ghi file đầu vào
        with open(input_path, "wb") as f:
            f.write(await file.read())

        # FFmpeg command để split thành .ts + generate m3u8
        command = [
            "ffmpeg",
            "-i", input_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-f", "hls",
            "-hls_time", "10",
            "-hls_segment_filename", segment_pattern,
            "-hls_playlist_type", "vod",
            "-hls_flags", "independent_segments",
            m3u8_path
        ]

        subprocess.run(command, check=True)

        # Upload các chunk ts
        uploaded_chunks = []
        for f_name in sorted(os.listdir(temp_dir)):
            if f_name.endswith(".ts"):
                full_path = os.path.join(temp_dir, f_name)
                object_name = f"{name_generated}/{f_name}"
                await minio_client.fput_object(object_name, full_path)
                duration = await get_duration(full_path)
                uploaded_chunks.append({
                    "name": f_name,
                    "duration": duration
                })

        # Upload m3u8
        await minio_client.fput_object(
            f"{name_generated}/{name_file_m3u8}", m3u8_path
        )
        uploaded_chunks.append({
            "name": name_file_m3u8,
            "duration": 0
        })

    # Lưu vào DB
    new_file = await Storage.create(
        name=file.filename,
        location_path=name_generated
    )

    await ChunkStorage.bulk_create([
        ChunkStorage(
            name=chunk["name"],
            storage=new_file,
            duration=chunk["duration"]
        ) for chunk in uploaded_chunks
    ])

    return "HLS chunks uploaded successfully"


async def list_file():
    results = []
    list_file = await Storage.all()
    for file in list_file:
        results.append({
            "id": file.id,
            "name": file.name,
            "location_path": file.location_path
        })
    return results


async def list_chunk_public(id: str):
    # FE will got 403 when call this, if want public bucket run mc command in minio "mc anonymous set download local/spliter"
    results = []
    file = await Storage.filter(id=id).first()
    if not file:
        return {
            "status_code": 404,
            "message": "File not found",
            "data": []
        }

    file_index = await ChunkStorage.filter(storage=file, name="index.m3u8").first()
    chunk_url = await minio_client.presign_get_url(f'{file.location_path}/{file_index.name}')

    results.append({
        "id": file_index.id,
        "name": file_index.name,
        "url": chunk_url
    })

    return {
        "message": "Success",
        "data": results
    }


async def list_chunk_private(id: str):
    file = await Storage.filter(id=id).first()
    if not file:
        return {
            "status_code": 404,
            "message": "File not found",
            "data": ""
        }
    chunks = await ChunkStorage.filter(storage=file, duration__gt=0).order_by("id")
    chunk_smallest = await ChunkStorage.filter(storage=file).order_by("duration").first()

    if not chunks:
        return {
            "status_code": 200,
            "message": "No chunks found",
            "data": ""
        }

    lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3",
        "#EXT-X-PLAYLIST-TYPE:VOD",
        f"#EXT-X-TARGETDURATION:{chunk_smallest.duration:.3f}",
    ]
    for chunk in chunks:
        presigned_url = await minio_client.presign_get_url(f"{file.location_path}/{chunk.name}")
        lines.append(f"#EXTINF:{chunk.duration:.3f},")
        lines.append(presigned_url)

    lines.append("#EXT-X-ENDLIST")

    return {
        "status_code": 200,
        "message": "Success",
        "data": "\n".join(lines)
    }
