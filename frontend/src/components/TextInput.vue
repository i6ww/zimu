<template>
  <div class="card">
    <div class="card-title">
      <span>📝</span> 输入文案
    </div>
    
    <el-input
      v-model="textContent"
      type="textarea"
      :rows="8"
      placeholder="请输入字幕文案，每行一句，例如：&#10;这是第一句文案&#10;这是第二句文案&#10;这是第三句文案"
      @input="handleInput"
    />
    
    <div class="text-stats">
      <span>行数: {{ lineCount }}</span>
      <span>字符数: {{ charCount }}</span>
    </div>
    
    <div class="text-tips">
      <el-alert
        title="提示"
        type="info"
        :closable="false"
        show-icon
      >
        <template #default>
          请确保文案顺序与音频中的说话顺序一致，系统将自动匹配时间轴
        </template>
      </el-alert>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['change'])

const textContent = ref('')

const lineCount = computed(() => {
  const lines = textContent.value.split('\n').filter(l => l.trim())
  return lines.length
})

const charCount = computed(() => {
  return textContent.value.length
})

const handleInput = () => {
  emit('change', textContent.value)
}

const getText = () => textContent.value

const setText = (text) => {
  textContent.value = text
}

const clear = () => {
  textContent.value = ''
}

defineExpose({ getText, setText, clear })
</script>

<style scoped>
.text-stats {
  margin-top: 12px;
  display: flex;
  gap: 20px;
  color: #a0a0a0;
  font-size: 13px;
}

.text-tips {
  margin-top: 16px;
}
</style>
