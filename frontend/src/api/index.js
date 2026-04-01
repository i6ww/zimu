/**
 * API 请求封装
 */
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const api = axios.create({
  baseURL: API_BASE,
  timeout: 600000 // 10分钟，用于 ASR 处理
})

// 上传音频文件
export const uploadAudio = async (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  
  const response = await api.post('/upload/audio', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (onProgress && e.total) {
        onProgress(Math.round((e.loaded * 100) / e.total))
      }
    }
  })
  
  return response.data
}

// 提交对齐任务
export const alignAudioText = async (audioUrl, text, language = 'zh') => {
  const response = await api.post('/asr/align', {
    audio_url: audioUrl,
    text: text,
    language: language
  })
  
  return response.data
}

// 查询任务状态
export const getTaskStatus = async (taskId) => {
  const response = await api.get(`/asr/status/${taskId}`)
  return response.data
}

// 获取任务结果
export const getTaskResult = async (taskId) => {
  const response = await api.get(`/asr/result/${taskId}`)
  return response.data
}

// 导出 SRT
export const exportSRT = async (subtitles, filename = 'subtitle.srt') => {
  const response = await api.post('/export/srt', {
    subtitles: subtitles,
    filename: filename
  }, {
    responseType: 'blob'
  })
  
  // 创建下载链接
  const blob = new Blob([response.data], { type: 'text/plain;charset=utf-8' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// 预览 SRT
export const previewSRT = async (subtitles) => {
  const response = await api.post('/export/preview', {
    subtitles: subtitles
  })
  return response.data
}

export default api
