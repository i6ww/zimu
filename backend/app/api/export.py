"""
导出接口
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.models.subtitle import SubtitleItem, ExportSRTRequest
from app.utils.srt import generate_srt, validate_subtitles
from typing import List

router = APIRouter(prefix="/api/export", tags=["导出"])


@router.post("/srt")
async def export_srt(request: ExportSRTRequest):
    """
    导出 SRT 字幕文件
    """
    try:
        # 转换为字典列表
        subtitles = [
            {
                "index": s.index,
                "begin_time": s.begin_time,
                "end_time": s.end_time,
                "text": s.text
            }
            for s in request.subtitles
        ]
        
        # 验证字幕
        is_valid, errors = validate_subtitles(subtitles)
        if not is_valid:
            return {
                "success": False,
                "message": "字幕验证失败",
                "errors": errors
            }
        
        # 生成 SRT 内容
        srt_content = generate_srt(subtitles)
        
        # 确定文件名
        filename = request.filename or "subtitle.srt"
        if not filename.endswith('.srt'):
            filename += '.srt'
        
        return Response(
            content=srt_content,
            media_type="text/plain",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/preview")
async def preview_srt(request: ExportSRTRequest):
    """
    预览 SRT 内容（不下载）
    """
    subtitles = [
        {
            "index": s.index,
            "begin_time": s.begin_time,
            "end_time": s.end_time,
            "text": s.text
        }
        for s in request.subtitles
    ]
    
    srt_content = generate_srt(subtitles)
    
    return {
        "success": True,
        "content": srt_content,
        "line_count": len(srt_content.split('\n'))
    }
