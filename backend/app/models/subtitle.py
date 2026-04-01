"""
字幕数据模型
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class SubtitleItem(BaseModel):
    """单个字幕片段"""
    index: int = Field(..., description="字幕序号")
    begin_time: float = Field(..., description="开始时间（秒）")
    end_time: float = Field(..., description="结束时间（秒）")
    text: str = Field(..., description="字幕文本")
    status: Optional[str] = Field(None, description="状态: matched/unmatched/low_confidence")
    confidence: Optional[float] = Field(None, description="匹配置信度")


class SubtitleList(BaseModel):
    """字幕列表"""
    subtitles: List[SubtitleItem] = Field(default_factory=list)
    total: int = Field(0, description="字幕总数")


class AlignmentRequest(BaseModel):
    """对齐请求"""
    audio_url: str = Field(..., description="音频文件公网URL")
    text: str = Field(..., description="用户文案（每行一句）")
    language: str = Field("zh", description="语言: zh/en/ja")


class AlignmentResponse(BaseModel):
    """对齐响应"""
    success: bool
    task_id: Optional[str] = None
    subtitles: List[SubtitleItem] = []
    message: Optional[str] = None


class UpdateSubtitleRequest(BaseModel):
    """更新字幕请求"""
    index: int = Field(..., description="字幕序号")
    begin_time: Optional[float] = None
    end_time: Optional[float] = None
    text: Optional[str] = None


class ExportSRTRequest(BaseModel):
    """导出 SRT 请求"""
    subtitles: List[SubtitleItem] = Field(..., description="字幕列表")
    filename: Optional[str] = Field("subtitle.srt", description="导出文件名")
