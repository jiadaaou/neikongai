<template>
  <div class="chat-page">
    <el-card class="chat-card" shadow="never">
      <div class="chat-container">
        <div class="messages-container" ref="messagesContainer">
          <div v-if="messages.length === 0" class="empty-state">
            <el-icon :size="64" color="#ddd"><ChatDotRound /></el-icon>
            <h3>开始您的法律咨询</h3>
            <p>输入您的法律问题，AI 将为您提供专业解答</p>
          </div>

          <div
            v-for="(message, index) in messages"
            :key="index"
            class="message"
            :class="message.role"
          >
            <div class="message-avatar">
              <el-avatar v-if="message.role === 'user'" :size="40" style="background: var(--primary-color)">
                {{ userStore.currentUser?.username?.charAt(0).toUpperCase() }}
              </el-avatar>
              <div v-else class="ai-avatar">
                <el-icon :size="24"><Cpu /></el-icon>
              </div>
            </div>
            <div class="message-content">
              <div class="message-header">
                <span class="message-name">{{ message.role === 'user' ? '我' : 'AI 助手' }}</span>
                <span class="message-time">{{ message.time }}</span>
              </div>
              <div class="message-text" v-html="formatMessage(message.content)"></div>
            </div>
          </div>

          <div v-if="loading" class="message assistant">
            <div class="message-avatar">
              <div class="ai-avatar">
                <el-icon :size="24"><Cpu /></el-icon>
              </div>
            </div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <div class="input-container">
          <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="输入您的法律问题..."
            @keydown.enter.exact.prevent="handleSend"
            :disabled="loading"
          />
          <el-button
            type="primary"
            :icon="Position"
            :loading="loading"
            @click="handleSend"
            :disabled="!inputMessage.trim()"
            size="large"
          >
            发送
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="suggestions-card" shadow="never">
      <template #header>
        <div class="card-header">
          <el-icon><QuestionFilled /></el-icon>
          <span>常见问题</span>
        </div>
      </template>
      <div class="suggestions">
        <el-tag
          v-for="(suggestion, index) in suggestions"
          :key="index"
          class="suggestion-tag"
          @click="inputMessage = suggestion"
          effect="plain"
        >
          {{ suggestion }}
        </el-tag>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { ChatDotRound, Cpu, Position, QuestionFilled } from '@element-plus/icons-vue'

const userStore = useUserStore()

const messages = ref([])
const inputMessage = ref('')
const loading = ref(false)
const messagesContainer = ref(null)

const suggestions = [
  '劳动合同应该包含哪些必要条款？',
  '如何处理员工试用期解除劳动合同？',
  '企业数据保护有哪些法律要求？',
  '商业秘密保护的法律措施有哪些？'
]

const formatMessage = (text) => {
  // 简单的 Markdown 格式化
  return text
    .replace(/\n/g, '<br>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const handleSend = async () => {
  if (!inputMessage.value.trim() || loading.value) return

  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  }

  messages.value.push(userMessage)
  const question = inputMessage.value
  inputMessage.value = ''
  scrollToBottom()

  loading.value = true

  try {
    const response = await fetch('/api/chat/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.token}`
      },
      body: JSON.stringify({ question })
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.detail || '请求失败')
    }

    const assistantMessage = {
      role: 'assistant',
      content: data.answer || '抱歉，我无法回答这个问题。',
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    }

    messages.value.push(assistantMessage)
    scrollToBottom()
  } catch (error) {
    ElMessage.error(error.message || '发送失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.chat-page {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 1.5rem;
  height: calc(100vh - 120px);
}

.chat-card,
.suggestions-card {
  border-radius: 12px;
  border: none;
}

.chat-card {
  display: flex;
  flex-direction: column;
}

:deep(.el-card__body) {
  flex: 1;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  scroll-behavior: smooth;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #999;
}

.empty-state h3 {
  margin: 1rem 0 0.5rem;
  color: #666;
}

.empty-state p {
  margin: 0;
  font-size: 0.95rem;
}

.message {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.ai-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.message-content {
  flex: 1;
  max-width: 70%;
}

.message.user .message-content {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.message.user .message-header {
  flex-direction: row-reverse;
}

.message-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: #1a1a1a;
}

.message-time {
  font-size: 0.875rem;
  color: #999;
}

.message-text {
  background: #f5f7fa;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  line-height: 1.6;
  color: #333;
}

.message.user .message-text {
  background: var(--primary-color);
  color: white;
}

.typing-indicator {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  background: #f5f7fa;
  border-radius: 12px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-10px);
    opacity: 1;
  }
}

.input-container {
  border-top: 1px solid #f0f0f0;
  padding: 1.5rem;
  display: flex;
  gap: 1rem;
  background: white;
}

.input-container :deep(.el-textarea__inner) {
  resize: none;
  border-radius: 8px;
}

.suggestions-card {
  max-height: 100%;
  overflow-y: auto;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.suggestions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.suggestion-tag {
  cursor: pointer;
  padding: 0.75rem;
  border-radius: 8px;
  transition: all 0.3s;
  white-space: normal;
  height: auto;
  line-height: 1.5;
}

.suggestion-tag:hover {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

@media (max-width: 1024px) {
  .chat-page {
    grid-template-columns: 1fr;
  }

  .suggestions-card {
    max-height: 300px;
  }
}
</style>
