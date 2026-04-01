"""
阿里云百炼 funASR 服务封装
"""
import dashscope
from dashscope.audio.asr import Transcription
from http import HTTPStatus
import json
import os
import time
from typing import Optional, List, Dict
from app.core.config import settings


class FunASRService:
    """阿里云百练 funASR 服务封装"""
    
    def __init__(self, api_key: str = None):
        """
        初始化 funASR 服务
        
        Args:
            api_key: 阿里云百炼 API Key
        """
        dashscope.api_key = api_key or settings.dashscope_api_key or os.getenv("DASHSCOPE_API_KEY")
        # 北京地域 API 地址
        dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'
    
    def submit_task(self, file_urls: List[str], language_hints: str = "zh") -> str:
        """
        提交录音文件识别任务
        
        Args:
            file_urls: 音频文件URL列表（公网可访问）
            language_hints: 语言提示，支持 zh/en/ja
            
        Returns:
            task_id: 任务ID
        """
        try:
            response = Transcription.async_call(
                model='fun-asr',
                file_urls=file_urls,
                language_hints=[language_hints]
            )
            
            if response.status_code == HTTPStatus.OK:
                return response.output.task_id
            else:
                raise Exception(f"提交任务失败: {response.output.message}")
                
        except Exception as e:
            raise Exception(f"提交 ASR 任务异常: {str(e)}")
    
    def wait_for_result(self, task_id: str, poll_interval: float = 2.0, timeout: int = 600) -> Dict:
        """
        同步等待任务完成并返回结果
        
        Args:
            task_id: 任务ID
            poll_interval: 轮询间隔（秒）
            timeout: 超时时间（秒）
            
        Returns:
            识别结果 JSON
        """
        start_time = time.time()
        
        while True:
            # 检查超时
            if time.time() - start_time > timeout:
                raise Exception(f"等待任务完成超时（{timeout}秒）")
            
            try:
                response = Transcription.fetch(task=task_id)
                
                if response.status_code != HTTPStatus.OK:
                    raise Exception(f"查询任务失败: {response.output.message if hasattr(response, 'output') else response}")
                
                status = response.output.task_status
                
                if status == 'SUCCEEDED':
                    # 获取结果 URL
                    results = response.output.results
                    for result in results:
                        if result['subtask_status'] == 'SUCCEEDED':
                            return self._fetch_result(result['transcription_url'])
                    
                    raise Exception("未找到成功的识别结果")
                        
                elif status == 'FAILED':
                    raise Exception("ASR 任务执行失败")
                
                # 继续等待
                time.sleep(poll_interval)
                
            except Exception as e:
                if "SUCCEEDED" in str(e) or "FAILED" in str(e):
                    raise
                time.sleep(poll_interval)
    
    def _fetch_result(self, transcription_url: str) -> Dict:
        """从结果 URL 获取识别结果"""
        from urllib import request
        result = json.loads(request.urlopen(transcription_url).read().decode('utf-8'))
        return result
    
    def parse_subtitles(self, result: Dict) -> List[Dict]:
        """
        解析识别结果为字幕列表
        
        Args:
            result: funASR 返回的 JSON 结果
            
        Returns:
            字幕列表 [{begin_time, end_time, text}, ...]
        """
        subtitles = []
        
        for transcript in result.get('transcripts', []):
            for sentence in transcript.get('sentences', []):
                begin_ms = sentence.get('begin_time', 0)
                end_ms = sentence.get('end_time', 0)
                text = sentence.get('text', '')
                
                subtitles.append({
                    'begin_time': begin_ms / 1000.0,  # 转换为秒
                    'end_time': end_ms / 1000.0,
                    'text': text
                })
        
        return subtitles


# 全局服务实例（延迟初始化）
_funasr_service: Optional[FunASRService] = None


def get_funasr_service() -> FunASRService:
    """获取 funASR 服务实例"""
    global _funasr_service
    if _funasr_service is None:
        _funasr_service = FunASRService()
    return _funasr_service
