# 🎬 HLS Streaming Demo

This project demonstrates a simple implementation of **HTTP Live Streaming (HLS)** using:
- **Frontend**: HTML + JavaScript + [HLS.js](https://github.com/video-dev/hls.js)
- **Backend**: FastAPI + MinIO + FFmpeg + PostgreSQL

---

## 📌 Features

- Upload a video file and split it into `.ts` chunks and a `.m3u8` playlist using FFmpeg
- Serve `.m3u8` playlists and streamable `.ts` segments dynamically via API
- Built-in Swagger UI for testing and documentation

---

## 🔗 API Endpoints

| Method | Endpoint                       | Description                              |
|--------|--------------------------------|------------------------------------------|
| POST   | `/api/storage`                 | Upload a video file                      |
| GET    | `/api/storage`                 | Get list of uploaded files               |
| GET    | `/api/storage/{id}/playlist`  | Return `.m3u8` playlist for streaming    |

📘 View detailed documentation at:  
**http://localhost:4000/docs**

---

## ⚙️ Step-by-Step Setup

### ✅ Step 1: Install Requirements

#### 1.1 Install [`uv`](https://github.com/astral-sh/uv) (fastest Python package manager)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 1.2 Docker Compose Setup (MinIO + PostgreSQL)
Create a file named docker-compose.yml with the following content:

```bash
services:
  postgres:
    image: postgres:15
    container_name: hls_postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: hls_demo
      POSTGRES_USER: hls_user
      POSTGRES_PASSWORD: hls_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  minio:
    image: minio/minio
    container_name: hls_minio
    restart: unless-stopped
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  minio_data:
```
Then run : 
```
docker-compose up -d
```

### 🧪 Step 2: Initialize Source
#### 1.1  Frontend (Client)
 - Open the file index_private.html in your browser
 - It uses HLS.js to stream from the backend API
### 1.2 Backend (FastAPI Server)
```bash
# Install all dependencies
uv sync && uv lock

# Activate virtual environment
source .venv/bin/activate

# Initialize database and apply migrations
make init_db

# Start server at http://localhost:4000
make run-server
```
## 💡 Usage Guide
- Go to http://localhost:4000/docs
- Use POST /api/storage to upload a video file
- Use GET /api/storage to list uploaded files
- Use GET /api/storage/{id}/playlist to retrieve the .m3u8 playlist
- Open the index_private.html file and update the file ID to start streaming

## 📌 Notes
- FFmpeg must be installed on the host machine to split the videos
- Ensure the MinIO bucket exists before uploading (can automate with Python/CLI)
- Avoid uploading large files in production without chunked upload or validation
- Consider using CDN or NGINX to serve static .ts files in production for better performance