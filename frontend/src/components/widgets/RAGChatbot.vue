<script setup>
import { ref } from 'vue';
import axios from 'axios';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';

const query = ref('');
const messages = ref([
  { sender: 'bot', text: 'Bonjour ! Posez-moi vos questions sur le référentiel de connaissances de l\'entreprise.' }
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
    messages.value.push({ sender: 'bot', text: 'Erreur lors de la communication avec l\'API du LLM.' });
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <div class="flex flex-col h-[520px] bg-white/70 border border-slate-200/70 rounded-3xl overflow-hidden shadow-lg shadow-slate-100/50 backdrop-blur-xl">
    <div class="p-4.5 border-b border-slate-150 bg-slate-50/60 flex justify-between items-center">
      <div class="flex items-center space-x-2">
        <span class="h-2 w-2 rounded-full bg-indigo-600 animate-pulse"></span>
        <h3 class="font-bold text-slate-800 text-sm">Assistant IA Intelligent</h3>
      </div>
      <span class="text-[9px] text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-200/30 font-bold font-mono">FastAPI RAG + Llama3</span>
    </div>
    
    <!-- Message Feed -->
    <div class="flex-1 p-5 overflow-y-auto space-y-4 bg-slate-50/20">
      <div v-for="(msg, idx) in messages" :key="idx" 
           :class="['p-4 rounded-2xl max-w-[85%] text-sm leading-relaxed shadow-[0_2px_12px_rgba(0,0,0,0.015)] transition-all duration-200', 
                    msg.sender === 'user' ? 'bg-indigo-600 text-white ml-auto rounded-tr-xs' : 'bg-white border border-slate-200/60 text-slate-800 rounded-tl-xs']">
        <p class="font-medium">{{ msg.text }}</p>
        <div v-if="msg.sources" class="mt-2.5 pt-2.5 border-t border-slate-100 text-[10px] text-slate-500 font-semibold font-mono flex flex-wrap gap-2 items-center justify-between">
          <span>Sources : {{ msg.sources.join(', ') }}</span>
          <span class="bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded border border-indigo-200/10">Confiance : {{ (msg.confidence * 100).toFixed(0) }}%</span>
        </div>
      </div>
      <div v-if="loading" class="text-indigo-600 text-xs font-semibold flex items-center space-x-2 animate-pulse pl-2">
        <span class="h-1.5 w-1.5 rounded-full bg-indigo-600 animate-ping"></span>
        <span>Recherche sémantique et synthèse de réponse...</span>
      </div>
    </div>
    
    <!-- Input Box -->
    <div class="p-4 border-t border-slate-150 bg-white/90 flex space-x-2.5 items-center">
      <InputText 
        v-model="query" 
        @keyup.enter="sendMessage" 
        placeholder="Posez une question sur vos documents..." 
        class="flex-1! bg-slate-50! border-slate-200/80! rounded-xl! px-4! py-2.5! text-sm! text-slate-800! placeholder:text-slate-400! outline-none! focus:bg-white! focus:border-indigo-500! focus:ring-2! focus:ring-indigo-500/10! transition-all! font-medium!" 
      />
      <Button 
        @click="sendMessage" 
        :loading="loading"
        label="Envoyer" 
        class="bg-indigo-600! hover:bg-indigo-550! text-white! px-5! py-2.5! rounded-xl! text-sm! font-bold! shadow-md! shadow-indigo-600/10! hover:shadow-indigo-600/20! transition-all! duration-200! cursor-pointer! border-none! shrink-0!" 
      />
    </div>
  </div>
</template>
