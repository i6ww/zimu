<template>
  <div class="card">
    <div class="card-title">
      <span>🎵</span> 上传音频
    </div>
    
    <div
      v-if="!audioFile"
      class="upload-area"
      :class="{ dragover: isDragover }"
      @dragover.prevent="isDragover = true"
      @dragleave="isDragover = false"
      @drop.prevent="handleDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInput"
        type="file"
        accept="audio/*"
        style="display: none"
        @change="handleFileSelect"
      />
      <div class="upload-icon">📁</div>
      <div class="upload-text">
        拖拽音频文件到此处，或点击选择<br />
        支持 MP3、WAV、M4A、OGG 等格式，最大 500MB
      </div>
    </div>
    
    <div v-else class="audio-info">
      <el-space>
        <span>📄</span>
        <span>{{ audioFile.name }}</span>
        <span class="file-size">({{ formatFileSize(audioFile.size) }})</span>
        <el-button type="danger" size="small" @click="removeFile">
          删除
        </el-button>
      </el-space>
      
      <el-progress
        v-if="uploadProgress > 0 && uploadProgress < 100"
        :percentage="uploadProgress"
        :stroke-width="8"
        style="margin-top: 12px"
      />
      
      <div v-if="uploadUrl" class="upload-success">
        <el-tag type="success">上传成功</el-tag>
        <span class="upload-url">{{ uploadUrl }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadAudio } from '../api'

const emit = defineEmits(['uploaded'])

const fileInput = ref(null)
const audioFile = ref(null)
const uploadUrl = ref('')
const uploadProgress = ref(0)
const isDragover = ref(false)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleDrop = (e) => {
  isDragover.value = false
  const files = e.dataTransfer?.files
  if (files?.length > 0) {
    handleFile(files[0])
  }
}

const handleFileSelect = (e) => {
  const files = e.target.files
  if (files?.length > 0) {
    handleFile(files[0])
  }
}

const handleFile = async (file) => {
  // 验证文件类型
  const allowedTypes = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/ogg', 
                        'audio/flac', 'audio/aac', 'audio/x-m4a', 'video/mp4',
                        'video/avi', 'video/x-matroska']
  const allowedExts = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac', 
                     '.mp4', '.avi', '.mkv', '.mov', '.wma']
  
  const ext = '.' + file.name.split('.').pop().toLowerCase()
  
  if (!allowedTypes.includes(file.type) && !allowedExts.includes(ext)) {
    ElMessage.error('不支持的文件格式')
    return
  }
  
  // 验证文件大小
  if (file.size > 500 * 1024 * 1024) {
    ElMessage.error('文件过大，最大支持 500MB')
    return
  }
  
  audioFile.value = file
  uploadProgress.value = 0
  
  try {
    const result = await uploadAudio(file, (progress) => {
      uploadProgress.value = progress
    })
    
    uploadUrl.value = result.public_url
    emit('uploaded', {
      file: file,
      url: result.public_url,
      filename: result.filename
    })
    
    ElMessage.success('音频上传成功')
  } catch (error) {
    ElMessage.error('上传失败: ' + (error.message || '未知错误'))
    audioFile.value = null
  }
}

const removeFile = () => {
  audioFile.value = null
  uploadUrl.value = ''
  uploadProgress.value = 0
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.audio-info {
  padding: 16px;
  background-color: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
}

.file-size {
  color: #a0a0a0;
  font-size: 13px;
}

.upload-success {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.upload-url {
  font-size: 12px;
  color: #a0a0a0;
  word-break: break-all;
}
</style>
