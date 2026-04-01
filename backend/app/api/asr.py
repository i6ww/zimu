"""
ASR 对齐接口
"""
from fastapi import APIRouter, HTTPException
from app.models.subtitle import (
    AlignmentRequest, 
    AlignmentResponse, 
    SubtitleItem
)
from app.core.funasr import get_funasr_service
from app.core.aligner import aligner
import uuid

router = APIRouter(prefix="/api/asr", tags=["语音识别"])

# 任务存储（生产环境应使用 Redis）
tasks = {}


@router.post("/align", response_model=AlignmentResponse)
async def align_audio_text(request: AlignmentRequest):
    """
    提交音频与文案对齐任务
    
    流程:
    1. 提交音频到 funASR 进行语音识别
    2. 获取识别结果
    3. 将用户文案与识别结果对齐
    """
    try:
        # 验证音频 URL
        if not request.audio_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="音频 URL 无效")
        
        # 生成任务 ID
        task_id = str(uuid.uuid4())
        
        # 初始化任务状态
        tasks[task_id] = {
            "status": "processing",
            "audio_url": request.audio_url,
            "text": request.text
        }
        
        # 提交 ASR 任务
        funasr = get_funasr_service()
        asr_task_id = funasr.submit_task(
            file_urls=[request.audio_url],
            language_hints=request.language
        )
        
        tasks[task_id]["asr_task_id"] = asr_task_id
        
        # 等待识别结果
        result = funasr.wait_for_result(asr_task_id)
        
        # 解析字幕
        asr_sentences = funasr.parse_subtitles(result)
        
        # 用户文案按行分割
        user_texts = request.text.strip().split('\n')
        
        # 对齐
        aligned_subtitles = aligner.align(user_texts, asr_sentences)
        
        # 转换为响应格式
        subtitles = [
            SubtitleItem(
                index=sub['index'],
                begin_time=sub['begin_time'],
                end_time=sub['end_time'],
                text=sub['text'],
                status=sub.get('status'),
                confidence=sub.get('confidence')
            )
            for sub in aligned_subtitles
        ]
        
        # 更新任务状态
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["subtitles"] = [
            {"index": s.index, "begin_time": s.begin_time, 
             "end_time": s.end_time, "text": s.text}
            for s in subtitles
        ]
        
        return AlignmentResponse(
            success=True,
            task_id=task_id,
            subtitles=subtitles,
            message="对齐完成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return AlignmentResponse(
            success=False,
            message=f"处理失败: {str(e)}"
        )


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """查询任务状态"""
    task = tasks.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return {
        "task_id": task_id,
        "status": task["status"]
    }


@router.get("/result/{task_id}")
async def get_task_result(task_id: str):
    """获取任务结果"""
    task = tasks.get(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task["status"] != "completed":
        return {
            "success": False,
            "status": task["status"],
            "message": "任务尚未完成"
        }
    
    return {
        "success": True,
        "subtitles": task["subtitles"]
    }
