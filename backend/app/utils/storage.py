"""
服务器本地文件存储工具
"""
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
from app.core.config import settings


class LocalStorage:
    """服务器本地文件存储工具"""
    
    def __init__(self, base_dir: str = None, base_url: str = None):
        """
        初始化本地存储
        
        Args:
            base_dir: 存储根目录（容器内路径）
            base_url: 访问基础 URL
        """
        self.base_dir = Path(base_dir or settings.storage_base_dir)
        self.audio_dir = self.base_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        
        # Nginx 反向代理地址
        self.base_url = base_url or settings.storage_base_url
    
    def save_file(self, file_content: bytes, original_filename: str) -> dict:
        """
        保存上传的文件
        
        Args:
            file_content: 文件字节内容
            original_filename: 原始文件名
            
        Returns:
            {
                "local_path": "/app/data/audio/xxx.mp3",
                "public_url": "http://your-server-ip:8080/audio/xxx.mp3",
                "filename": "xxx.mp3"
            }
        """
        # 获取文件扩展名
        ext = Path(original_filename).suffix.lower()
        if not ext:
            ext = ".mp3"
        
        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = self.audio_dir / filename
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # 生成公网访问 URL
        public_url = f"{self.base_url}/audio/{filename}"
        
        return {
            "local_path": str(file_path),
            "public_url": public_url,
            "filename": filename
        }
    
    async def save_upload_file(self, upload_file: UploadFile) -> dict:
        """
        保存 FastAPI UploadFile
        
        Args:
            upload_file: FastAPI 上传的文件对象
            
        Returns:
            保存结果字典
        """
        # 读取文件内容
        content = await upload_file.read()
        
        # 保存文件
        original_filename = upload_file.filename or "unknown.mp3"
        return self.save_file(content, original_filename)
    
    def delete_file(self, filename: str):
        """删除文件"""
        file_path = self.audio_dir / filename
        if file_path.exists():
            file_path.unlink()
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """清理超过指定时间的文件"""
        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        deleted = []
        for file_path in self.audio_dir.iterdir():
            if file_path.is_file():
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    deleted.append(file_path.name)
        
        return deleted
    
    def get_file_path(self, filename: str) -> Optional[Path]:
        """获取文件路径"""
        file_path = self.audio_dir / filename
        if file_path.exists():
            return file_path
        return None


# 全局存储实例
storage = LocalStorage()


def get_storage() -> LocalStorage:
    """获取存储实例"""
    return storage
