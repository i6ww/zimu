<template>
  <div class="card">
    <div class="card-title">
      <span>▶️</span> 预览
    </div>
    
    <div class="audio-player">
      <audio ref="audioRef" :src="audioUrl" @timeupdate="onTimeUpdate" @loadedmetadata="onLoaded" />
      
      <div class="player-controls">
        <el-button-group>
          <el-button @click="togglePlay" size="large">
            {{ isPlaying ? '⏸️' : '▶️' }}
          </el-button>
        </el-button-group>
        
        <div class="time-display">
          {{ formatTime(currentTime) }} / {{ formatTime(duration) }}
        </div>
        
        <el-slider
          v-model="currentTime"
          :max="duration"
          :step="0.1"
          @input="seekTo"
          class="time-slider"
        />
        
        <div class="volume-control">
          <span>{{ volumeIcon }}</span>
          <el-slider v-model="volume" :min="0" :max="1" :step="0.1" @input="setVolume" style="width: 80px" />
        </div>
      </div>
    </div>
    
    <div class="subtitle-preview" v-if="currentSubtitle">
      <div class="preview-time">
        {{ formatTime(currentSubtitle.begin_time) }} → {{ formatTime(currentSubtitle.end_time) }}
      </div>
      <div class="preview-text">
        {{ currentSubtitle.text }}
      </div>
    </div>
    <div class="subtitle-preview empty" v-else>
      <span>当前时间暂无字幕</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  audioUrl: {
    type: String,
    default: ''
  },
  subtitles: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['timechange'])

const audioRef = ref(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)

const currentSubtitle = computed(() => {
  if (!props.subtitles.length) return null
  
  for (const sub of props.subtitles) {
    if (currentTime.value >= sub.begin_time && currentTime.value <= sub.end_time) {
      return sub
    }
  }
  return null
})

const volumeIcon = computed(() => {
  if (volume.value === 0) return '🔇'
  if (volume.value < 0.5) return '🔉'
  return '🔊'
})

watch(() => props.audioUrl, () => {
  isPlaying.value = false
  currentTime.value = 0
})

const togglePlay = () => {
  if (!audioRef.value) return
  
  if (isPlaying.value) {
    audioRef.value.pause()
  } else {
    audioRef.value.play()
  }
  isPlaying.value = !isPlaying.value
}

const onTimeUpdate = () => {
  if (audioRef.value) {
    currentTime.value = audioRef.value.currentTime
    emit('timechange', currentTime.value)
  }
}

const onLoaded = () => {
  if (audioRef.value) {
    duration.value = audioRef.value.duration
  }
}

const seekTo = (time) => {
  if (audioRef.value) {
    audioRef.value.currentTime = time
  }
}

const setVolume = (vol) => {
  if (audioRef.value) {
    audioRef.value.volume = vol
  }
}

const playAt = (time) => {
  if (audioRef.value) {
    audioRef.value.currentTime = time
    audioRef.value.play()
    isPlaying.value = true
  }
}

const formatTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '00:00.0'
  
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  const ms = Math.floor((seconds % 1) * 10)
  
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms}`
}

defineExpose({ playAt })
</script>

<style scoped>
.audio-player {
  background-color: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 16px;
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.time-display {
  font-family: 'Consolas', monospace;
  color: #a0a0a0;
  font-size: 14px;
  min-width: 100px;
}

.time-slider {
  flex: 1;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.subtitle-preview {
  background-color: rgba(64, 158, 255, 0.1);
  border: 1px solid rgba(64, 158, 255, 0.3);
  border-radius: 8px;
  padding: 16px;
  text-align: center;
}

.subtitle-preview.empty {
  background-color: rgba(0, 0, 0, 0.2);
  border-color: rgba(255, 255, 255, 0.1);
  color: #a0a0a0;
}

.preview-time {
  font-family: 'Consolas', monospace;
  font-size: 13px;
  color: #a0a0a0;
  margin-bottom: 8px;
}

.preview-text {
  font-size: 18px;
  line-height: 1.6;
}
</style>
