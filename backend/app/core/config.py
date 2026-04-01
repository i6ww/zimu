"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 阿里云百炼 API Key
    dashscope_api_key: str = ""
    
    # 存储配置
    storage_base_dir: str = "/app/data"
    storage_base_url: str = "http://localhost:8080"
    
    # 文件上传限制
    max_upload_size: int = 500 * 1024 * 1024  # 500MB
    
    # 允许的音频格式
    allowed_audio_formats: list = ["mp3", "wav", "m4a", "ogg", "flac", "aac", "wma", "mp4", "avi", "mkv", "mov"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局配置实例
settings = Settings()
