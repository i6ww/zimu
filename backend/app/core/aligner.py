"""
文案与识别结果对齐器
"""
import re
from difflib import SequenceMatcher
from typing import List, Dict, Tuple


class TextAligner:
    """文案与识别结果对齐器"""
    
    def __init__(self, threshold: float = 0.6):
        """
        初始化对齐器
        
        Args:
            threshold: 匹配阈值，低于此值的匹配将被标记为未匹配
        """
        self.threshold = threshold
    
    def align(self, user_texts: List[str], asr_sentences: List[Dict]) -> List[Dict]:
        """
        将用户文案与 ASR 识别结果对齐
        
        Args:
            user_texts: 用户输入的文案列表（每行一句）
            asr_sentences: ASR 识别的句子列表 [{begin_time, end_time, text}]
            
        Returns:
            对齐后的字幕列表
        """
        subtitles = []
        used_indices = set()
        
        # 预处理用户文案
        processed_texts = []
        for text in user_texts:
            text = text.strip()
            if text:  # 跳过空行
                processed_texts.append(text)
        
        # 按顺序匹配
        for user_text in processed_texts:
            best_match = None
            best_score = 0
            best_idx = -1
            
            # 找到最佳匹配的 ASR 句子
            for i, sentence in enumerate(asr_sentences):
                if i in used_indices:
                    continue
                    
                score = self._similarity(user_text, sentence.get('text', ''))
                
                if score > best_score:
                    best_score = score
                    best_match = sentence
                    best_idx = i
            
            if best_match and best_score >= self.threshold:
                subtitles.append({
                    'begin_time': best_match['begin_time'],
                    'end_time': best_match['end_time'],
                    'text': user_text  # 使用用户原文
                })
                used_indices.add(best_idx)
            else:
                # 未找到匹配，尝试智能推断位置
                inferred = self._infer_time_position(
                    len(subtitles), 
                    len(asr_sentences),
                    asr_sentences
                )
                subtitles.append({
                    'begin_time': inferred['begin_time'],
                    'end_time': inferred['end_time'],
                    'text': user_text,
                    'status': 'unmatched' if not best_match else 'low_confidence',
                    'confidence': best_score if best_match else 0
                })
        
        # 添加序号
        for i, sub in enumerate(subtitles, 1):
            sub['index'] = i
            
        return subtitles
    
    def _similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        Args:
            text1: 文本1
            text2: 文本2
            
        Returns:
            相似度分数 0-1
        """
        # 去除标点后比较
        t1 = re.sub(r'[^\w\s]', '', text1).lower()
        t2 = re.sub(r'[^\w\s]', '', text2).lower()
        
        # 完全匹配
        if t1 == t2:
            return 1.0
        
        # 使用序列匹配器计算相似度
        return SequenceMatcher(None, t1, t2).ratio()
    
    def _infer_time_position(self, current_index: int, total_asr: int, 
                             asr_sentences: List[Dict]) -> Dict:
        """
        智能推断未匹配文案的时间位置
        
        Args:
            current_index: 当前处理的字幕索引
            total_asr: ASR 句子总数
            asr_sentences: ASR 句子列表
            
        Returns:
            推断的时间位置
        """
        if not asr_sentences:
            return {'begin_time': 0.0, 'end_time': 0.0}
        
        # 根据文案数量平均分配时间
        total_duration = asr_sentences[-1]['end_time'] if asr_sentences else 0
        segment_duration = total_duration / max(len(asr_sentences), 1)
        
        # 计算大致位置
        estimated_begin = current_index * segment_duration
        estimated_end = estimated_begin + segment_duration * 0.8
        
        return {
            'begin_time': round(estimated_begin, 2),
            'end_time': round(estimated_end, 2)
        }
    
    def batch_align(self, user_texts: List[str], asr_sentences: List[Dict],
                   batch_size: int = 10) -> List[Dict]:
        """
        批量对齐（用于长文本）
        
        Args:
            user_texts: 用户文案列表
            asr_sentences: ASR 句子列表
            batch_size: 每批处理数量
            
        Returns:
            对齐后的字幕列表
        """
        all_subtitles = []
        
        for i in range(0, len(user_texts), batch_size):
            batch_texts = user_texts[i:i + batch_size]
            batch_subtitles = self.align(batch_texts, asr_sentences)
            
            # 调整索引
            offset = i
            for sub in batch_subtitles:
                sub['index'] = sub['index'] + offset
            
            all_subtitles.extend(batch_subtitles)
        
        return all_subtitles


# 全局对齐器实例
aligner = TextAligner()
