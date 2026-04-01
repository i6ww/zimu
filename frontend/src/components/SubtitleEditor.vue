<template>
  <div class="card">
    <div class="card-title">
      <span>✂️</span> 字幕编辑
      <span class="subtitle-count">{{ subtitles.length }} 条</span>
    </div>
    
    <div class="subtitle-list" v-if="subtitles.length > 0">
      <div
        v-for="(item, index) in subtitles"
        :key="item.index"
        class="subtitle-item"
        :class="{ active: currentIndex === index }"
        @click="selectSubtitle(index)"
      >
        <div class="subtitle-index">{{ item.index }}</div>
        
        <div class="subtitle-time">
          <el-time-select
            v-model="item._beginTimeStr"
            step="00:01"
            start="00:00"
            end="12:00"
            style="width: 100px"
            size="small"
            @change="(val) => handleBeginTimeChange(index, val)"
          />
          <span class="time-separator">→</span>
          <el-time-select
            v-model="item._endTimeStr"
            step="00:01"
            start="00:00"
            end="12:00"
            style="width: 100px"
            size="small"
            @change="(val) => handleEndTimeChange(index, val)"
          />
        </div>
        
        <div class="subtitle-text">
          <el-input
            v-model="item.text"
            size="small"
            @change="handleTextChange(index)"
          />
        </div>
        
        <div class="subtitle-status" v-if="item.status">
          <el-tag
            :type="getStatusType(item.status)"
            size="small"
          >
            {{ getStatusText(item.status) }}
          </el-tag>
        </div>
        
        <div class="subtitle-actions">
          <el-button
            size="small"
            :icon="Playing"
            circle
            @click.stop="playFromHere(item)"
          />
          <el-button
            size="small"
            :icon="Delete"
            type="danger"
            circle
            @click.stop="deleteSubtitle(index)"
          />
        </div>
      </div>
    </div>
    
    <div v-else class="empty-state">
      <span>暂无字幕，请上传音频并输入文案后开始识别</span>
    </div>
    
    <div class="editor-actions" v-if="subtitles.length > 0">
      <el-button @click="addSubtitle">
        <el-icon><Plus /></el-icon>
        添加片段
      </el-button>
      <el-button @click="undo" :disabled="historyIndex <= 0">
        <el-icon><RefreshLeft /></el-icon>
        撤销
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Plus, RefreshLeft, Playing } from '@element-plus/icons-vue'

const props = defineProps({
  subtitles: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:subtitles', 'play'])

const currentIndex = ref(-1)
const history = ref([])
const historyIndex = ref(-1)

// 秒数转时间字符串 "HH:MM"
const secondsToTimeStr = (seconds) => {
  if (!seconds && seconds !== 0) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

// 时间字符串转秒数
const timeStrToSeconds = (timeStr) => {
  if (!timeStr) return 0
  const [mins, secs] = timeStr.split(':').map(Number)
  return mins * 60 + (secs || 0)
}

// 获取字幕的开始时间字符串
const getBeginTimeStr = (item) => secondsToTimeStr(item.begin_time)

// 获取字幕的结束时间字符串
const getEndTimeStr = (item) => secondsToTimeStr(item.end_time)

watch(() => props.subtitles, (newVal) => {
  // 保存历史记录
  if (newVal.length > 0) {
    // 初始化时间字符串
    initTimeStr(newVal)
    saveHistory(JSON.parse(JSON.stringify(newVal)))
  }
}, { deep: true })

const saveHistory = (data) => {
  // 移除当前位置之后的历史
  history.value = history.value.slice(0, historyIndex.value + 1)
  history.value.push(data)
  historyIndex.value = history.value.length - 1
}

const selectSubtitle = (index) => {
  currentIndex.value = index
}

const handleTextChange = () => {
  emit('update:subtitles', [...props.subtitles])
}

const deleteSubtitle = async (index) => {
  try {
    await ElMessageBox.confirm('确定要删除这条字幕吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    const newSubtitles = [...props.subtitles]
    newSubtitles.splice(index, 1)
    
    // 重新编号
    newSubtitles.forEach((sub, i) => {
      sub.index = i + 1
    })
    
    emit('update:subtitles', newSubtitles)
    ElMessage.success('已删除')
  } catch {
    // 用户取消
  }
}

const addSubtitle = () => {
  const newSubtitle = {
    index: props.subtitles.length + 1,
    begin_time: 0,
    end_time: 0,
    text: '新字幕',
    _beginTimeStr: '00:00',
    _endTimeStr: '00:00'
  }
  
  emit('update:subtitles', [...props.subtitles, newSubtitle])
  ElMessage.success('已添加新片段')
}

const undo = () => {
  if (historyIndex.value > 0) {
    historyIndex.value--
    emit('update:subtitles', JSON.parse(JSON.stringify(history.value[historyIndex.value])))
    ElMessage.info('已撤销')
  }
}

const playFromHere = (item) => {
  emit('play', item.begin_time)
}

// 初始化字幕的时间字符串（用于 el-time-select 绑定）
const initTimeStr = (subtitles) => {
  subtitles.forEach(item => {
    if (!item._beginTimeStr) {
      item._beginTimeStr = secondsToTimeStr(item.begin_time || 0)
    }
    if (!item._endTimeStr) {
      item._endTimeStr = secondsToTimeStr(item.end_time || 0)
    }
  })
}

// 处理开始时间变化
const handleBeginTimeChange = (index, val) => {
  const item = props.subtitles[index]
  item.begin_time = timeStrToSeconds(val)
  emit('update:subtitles', [...props.subtitles])
}

// 处理结束时间变化
const handleEndTimeChange = (index, val) => {
  const item = props.subtitles[index]
  item.end_time = timeStrToSeconds(val)
  emit('update:subtitles', [...props.subtitles])
}

const getStatusType = (status) => {
  switch (status) {
    case 'matched': return 'success'
    case 'unmatched': return 'warning'
    case 'low_confidence': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'matched': return '已匹配'
    case 'unmatched': return '未匹配'
    case 'low_confidence': return '低置信'
    default: return status
  }
}
</script>

<style scoped>
.subtitle-count {
  font-size: 14px;
  color: #a0a0a0;
  font-weight: normal;
  margin-left: 12px;
}

.subtitle-list {
  max-height: 400px;
  overflow-y: auto;
  margin-bottom: 16px;
}

.subtitle-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  background-color: rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
  gap: 12px;
}

.subtitle-item:hover {
  background-color: rgba(64, 158, 255, 0.1);
}

.subtitle-item.active {
  background-color: rgba(64, 158, 255, 0.2);
  border: 1px solid #409EFF;
}

.subtitle-index {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #409EFF;
  border-radius: 50%;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
}

.subtitle-time {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.time-separator {
  color: #a0a0a0;
}

.subtitle-text {
  flex: 1;
  min-width: 0;
}

.subtitle-status {
  flex-shrink: 0;
}

.subtitle-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #a0a0a0;
}

.editor-actions {
  display: flex;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}
</style>
