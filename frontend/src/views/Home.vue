<template>
  <div class="home">
    <header class="header">
      <div class="header-content">
        <h1 class="logo">🎬 自动打轴工具</h1>
        <div class="header-actions">
          <el-button @click="showHelp = true" circle>❓</el-button>
        </div>
      </div>
    </header>
    
    <main class="main">
      <div class="container">
        <!-- 步骤指示器 -->
        <el-steps :active="currentStep" finish-status="success" class="steps">
          <el-step title="上传音频" />
          <el-step title="输入文案" />
          <el-step title="自动对齐" />
          <el-step title="导出字幕" />
        </el-steps>
        
        <!-- 第一步：上传音频 -->
        <AudioUploader @uploaded="onAudioUploaded" />
        
        <!-- 第二步：输入文案 -->
        <TextInput ref="textInputRef" @change="onTextChange" />
        
        <!-- 操作按钮 -->
        <div class="action-bar">
          <el-button
            type="primary"
            size="large"
            :loading="isProcessing"
            :disabled="!canStart"
            @click="startAlign"
          >
            🎤 {{ isProcessing ? '处理中...' : '开始识别与对齐' }}
          </el-button>
        </div>
        
        <!-- 第三步：预览与编辑 -->
        <SubtitlePreview
          ref="previewRef"
          :audioUrl="audioUrl"
          :subtitles="subtitles"
          @timechange="onTimeChange"
        />
        
        <SubtitleEditor
          v-model:subtitles="subtitles"
          @play="playFromTime"
        />
        
        <!-- 第四步：导出 -->
        <div class="card export-card" v-if="subtitles.length > 0">
          <div class="card-title">
            <span>💾</span> 导出字幕
          </div>
          
          <div class="export-actions">
            <el-button type="primary" @click="exportSRT">
              📥 导出 SRT 文件
            </el-button>
            <el-button @click="previewContent">
              👁️ 预览内容
            </el-button>
          </div>
          
          <el-input
            v-model="exportFilename"
            placeholder="文件名"
            style="width: 200px; margin-top: 12px"
          >
            <template #append>.srt</template>
          </el-input>
        </div>
      </div>
    </main>
    
    <!-- 帮助对话框 -->
    <el-dialog v-model="showHelp" title="使用帮助" width="600px">
      <div class="help-content">
        <h3>使用流程</h3>
        <ol>
          <li>上传音频文件（支持 MP3、WAV、M4A 等格式）</li>
          <li>在文案输入框中输入字幕文本，每行一句</li>
          <li>点击"开始识别与对齐"按钮</li>
          <li>系统会自动识别音频并匹配时间轴</li>
          <li>检查并手动调整对齐结果</li>
          <li>导出 SRT 字幕文件</li>
        </ol>
        
        <h3>注意事项</h3>
        <ul>
          <li>音频文件最大支持 500MB</li>
          <li>文案顺序应与音频中的说话顺序一致</li>
          <li>可以通过拖拽时间轴来手动调整</li>
          <li>识别需要网络连接阿里云服务</li>
        </ul>
      </div>
    </el-dialog>
    
    <!-- 预览对话框 -->
    <el-dialog v-model="showPreview" title="SRT 预览" width="700px">
      <pre class="srt-preview">{{ srtPreview }}</pre>
    </el-dialog>
    
    <!-- 加载遮罩 -->
    <div class="loading-overlay" v-if="isProcessing">
      <el-icon class="loading-icon" :size="60"><Loading /></el-icon>
      <p class="loading-text">{{ loadingText }}</p>
      <p class="loading-tip">首次使用可能需要等待模型加载...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import AudioUploader from '../components/AudioUploader.vue'
import TextInput from '../components/TextInput.vue'
import SubtitleEditor from '../components/SubtitleEditor.vue'
import SubtitlePreview from '../components/SubtitlePreview.vue'
import { alignAudioText, exportSRT as exportSRTApi, previewSRT } from '../api'

const textInputRef = ref(null)
const previewRef = ref(null)

// 状态
const audioFile = ref(null)
const audioUrl = ref('')
const textContent = ref('')
const subtitles = ref([])
const isProcessing = ref(false)
const loadingText = ref('正在提交识别任务...')
const currentStep = ref(0)
const showHelp = ref(false)
const showPreview = ref(false)
const srtPreview = ref('')
const exportFilename = ref('subtitle')

const canStart = computed(() => {
  return audioUrl.value && textContent.value.trim()
})

const onAudioUploaded = (data) => {
  audioFile.value = data.file
  audioUrl.value = data.url
  currentStep.value = 0
}

const onTextChange = (text) => {
  textContent.value = text
  currentStep.value = 1
}

const onTimeChange = (time) => {
  // 可以用于高亮当前字幕
}

const playFromTime = (time) => {
  previewRef.value?.playAt(time)
}

const startAlign = async () => {
  if (!canStart.value) {
    ElMessage.warning('请先上传音频并输入文案')
    return
  }
  
  isProcessing.value = true
  loadingText.value = '正在提交识别任务...'
  currentStep.value = 2
  
  try {
    const result = await alignAudioText(
      audioUrl.value,
      textContent.value,
      'zh'
    )
    
    if (result.success) {
      subtitles.value = result.subtitles.map(s => ({
        ...s,
        begin_time: s.begin_time || 0,
        end_time: s.end_time || 0
      }))
      
      currentStep.value = 3
      ElMessage.success(`对齐完成！共生成 ${subtitles.value.length} 条字幕`)
    } else {
      ElMessage.error(result.message || '对齐失败')
    }
  } catch (error) {
    console.error('对齐失败:', error)
    ElMessage.error('对齐失败: ' + (error.message || '未知错误'))
  } finally {
    isProcessing.value = false
  }
}

const exportSRT = async () => {
  try {
    const filename = exportFilename.value + '.srt'
    await exportSRTApi(subtitles.value, filename)
    ElMessage.success('导出成功！')
  } catch (error) {
    ElMessage.error('导出失败: ' + (error.message || '未知错误'))
  }
}

const previewContent = async () => {
  try {
    const result = await previewSRT(subtitles.value)
    srtPreview.value = result.content
    showPreview.value = true
  } catch (error) {
    ElMessage.error('预览失败')
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

.header {
  background-color: #16213e;
  padding: 16px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 24px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.main {
  padding: 20px 0;
}

.steps {
  margin-bottom: 24px;
  padding: 0 20px;
}

.action-bar {
  text-align: center;
  margin: 24px 0;
}

.export-card {
  text-align: center;
}

.export-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

.srt-preview {
  background-color: rgba(0, 0, 0, 0.3);
  padding: 16px;
  border-radius: 8px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 400px;
  overflow-y: auto;
}

.help-content h3 {
  margin-top: 20px;
  margin-bottom: 12px;
  color: #409EFF;
}

.help-content h3:first-child {
  margin-top: 0;
}

.help-content ol,
.help-content ul {
  padding-left: 24px;
  line-height: 2;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-icon {
  color: #409EFF;
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 20px;
  font-size: 18px;
  color: #fff;
}

.loading-tip {
  margin-top: 8px;
  font-size: 14px;
  color: #a0a0a0;
}
</style>
