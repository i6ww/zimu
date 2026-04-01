"""
文件上传接口
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.core.config import settings
from app.utils.storage import get_storage

router = APIRouter(prefix="/api/upload", tags=["上传"])


@router.post("/audio")
async def upload_audio(file: UploadFile = File(...)):
    """
    上传音频文件
    
    - 支持格式: mp3, wav, m4a, ogg, flac, aac, wma, mp4, avi, mkv, mov
    - 最大大小: 500MB
    """
    # 检查文件类型
    if file.filename:
        ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        if ext not in settings.allowed_audio_formats:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {ext}，支持的格式: {', '.join(settings.allowed_audio_formats)}"
            )
    
    # 检查文件大小
    file_content = await file.read()
    if len(file_content) > settings.max_upload_size:
        raise HTTPException(
            status_code=400,
            detail=f"文件过大，最大支持 {settings.max_upload_size // (1024*1024)}MB"
        )
    
    # 保存文件
    storage = get_storage()
    result = await storage.save_upload_file(file)
    
    return {
        "success": True,
        "filename": result["filename"],
        "public_url": result["public_url"],
        "local_path": result["local_path"],
        "size": len(file_content)
    }


@router.get("/formats")
async def get_allowed_formats():
    """获取允许的文件格式"""
    return {
        "formats": settings.allowed_audio_formats,
        "max_size_mb": settings.max_upload_size // (1024 * 1024)
    }
