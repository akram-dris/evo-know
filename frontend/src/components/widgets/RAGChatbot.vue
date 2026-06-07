<script setup>
import { ref } from 'vue';
import axios from 'axios';

const query = ref('');
const messages = ref([
  { sender: 'bot', text: 'Hello! Ask me anything about our enterprise knowledge repository.' }
]);
const loading = ref(false);

const sendMessage = async () => {
  if (!query.value.trim()) return;
  
  messages.value.push({ sender: 'user', text: query.value });
  const userQuery = query.value;
  query.value = '';
  loading.value = true;
  
  try {
    const res = await axios.post('/api/v1/query', { question: userQuery });
    messages.value.push({ 
      sender: 'bot', 
      text: res.data.answer,
      sources: res.data.sources,
      confidence: res.data.confidence
    });
  } catch (err) {
    messages.value.push({ sender: 'bot', text: 'Error contacting LLM API.' });
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="flex flex-col h-[500px] bg-slate-950 border border-slate-800 rounded-xl overflow-hidden glass-panel">
    <div class="p-4 border-b border-slate-850 bg-slate-900/50 flex justify-between items-center">
      <h3 class="font-medium text-slate-200">AI Knowledge Assistant</h3>
      <span class="text-xs text-slate-400 font-mono">Ollama - llama3</span>
    </div>
    <!-- Message Feed -->
    <div class="flex-1 p-4 overflow-y-auto space-y-3">
      <div v-for="(msg, idx) in messages" :key="idx" 
           :class="['p-3 rounded-lg max-w-[85%] text-sm', msg.sender === 'user' ? 'bg-indigo-600 ml-auto' : 'bg-slate-850']">
        <p>{{ msg.text }}</p>
        <div v-if="msg.sources" class="mt-2 pt-2 border-t border-slate-800 text-xs text-slate-400">
          <span>Sources: {{ msg.sources.join(', ') }}</span>
          <span class="ml-2">| Confidence: {{ (msg.confidence * 100).toFixed(0) }}%</span>
        </div>
      </div>
      <div v-if="loading" class="text-slate-400 text-xs animate-pulse">Searching vector store & synthesizing answer...</div>
    </div>
    <!-- Input Box -->
    <div class="p-3 border-t border-slate-850 flex space-x-2">
      <input v-model="query" @keyup.enter="sendMessage" placeholder="Ask a question..." 
             class="flex-1 bg-slate-900 border border-slate-800 rounded-lg px-3 text-sm focus:outline-none focus:border-indigo-500" />
      <button @click="sendMessage" class="bg-indigo-600 hover:bg-indigo-500 px-4 py-2 rounded-lg text-sm font-medium">Send</button>
    </div>
  </div>
</template>
