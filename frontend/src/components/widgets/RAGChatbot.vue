<script setup>
import { ref } from 'vue';
import axios from 'axios';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { Eye, FileText, X } from 'lucide-vue-next';

const query = ref('');
const messages = ref([
  { sender: 'bot', text: 'Bonjour ! Posez-moi vos questions sur le référentiel de connaissances de l\'entreprise.' }
]);
const loading = ref(false);

// Document Viewer Modal State
const showViewModal = ref(false);
const selectedDocContent = ref('');
const selectedDocTitle = ref('');
const loadingContent = ref(false);

const openViewDoc = async (docId, title) => {
  showViewModal.value = true;
  selectedDocTitle.value = title;
  selectedDocContent.value = '';
  loadingContent.value = true;
  try {
    const res = await axios.get(`/api/v1/query/documents/${docId}/content`);
    selectedDocContent.value = res.data.content;
  } catch (err) {
    console.error("Error fetching doc content:", err);
    selectedDocContent.value = "Erreur lors de la lecture du document.";
  } finally {
    loadingContent.value = false;
  }
};

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
  <div class="flex flex-col h-[calc(100vh-290px)] min-h-[420px] bg-white/70 border border-slate-200/70 rounded-3xl overflow-hidden shadow-lg shadow-slate-100/50 backdrop-blur-xl">
    <div class="p-4.5 border-b border-slate-150 bg-slate-50/60 flex justify-between items-center">
      <div class="flex items-center space-x-2">
        <span class="h-2 w-2 rounded-full bg-indigo-600 animate-pulse"></span>
        <h3 class="font-bold text-slate-800 text-sm">Assistant IA Intelligent</h3>
      </div>
      <span class="text-[9px] text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md border border-indigo-200/30 font-bold font-mono">FastAPI RAG + Gemini</span>
    </div>
    
    <!-- Message Feed -->
    <div class="flex-1 p-5 overflow-y-auto space-y-4 bg-slate-50/20">
      <div v-for="(msg, idx) in messages" :key="idx" 
           :class="['p-4 rounded-2xl max-w-[85%] text-sm leading-relaxed shadow-[0_2px_12px_rgba(0,0,0,0.015)] transition-all duration-200', 
                    msg.sender === 'user' ? 'bg-indigo-600 text-white ml-auto rounded-tr-xs' : 'bg-white border border-slate-200/60 text-slate-800 rounded-tl-xs']">
        <p class="font-medium">{{ msg.text }}</p>
        <div v-if="msg.sources && msg.sources.length" class="mt-2.5 pt-2.5 border-t border-slate-100 text-[10px] text-slate-500 font-semibold font-mono flex flex-wrap gap-2 items-center justify-between">
          <div class="flex flex-wrap gap-1.5 items-center">
            <span>Sources :</span>
            <span v-for="source in msg.sources" :key="source.id" class="inline-flex items-center space-x-1 bg-slate-100 hover:bg-slate-200/60 text-indigo-750 px-2 py-0.5 rounded border border-slate-200/50 transition">
              <span>{{ source.title }}</span>
              <button 
                @click="openViewDoc(source.id, source.title)"
                class="p-0.5 hover:bg-slate-300/50 text-indigo-650 rounded transition cursor-pointer flex items-center justify-center"
                title="Lire la source"
              >
                <Eye class="h-3 w-3" />
              </button>
            </span>
          </div>
          <span class="bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded border border-indigo-200/10">Confiance : {{ (msg.confidence * 100).toFixed(0) }}%</span>
        </div>
      </div>

      <!-- Suggestion Cards (ChatGPT style) -->
      <div v-if="messages.length === 1" class="max-w-xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-3 pt-8 pb-4">
        <div 
          v-for="sug in [
            { text: 'Quelle est la planification de sauvegarde ?', desc: 'Consulter la politique de backup' },
            { text: 'Quelles sont les spécifications de l\'architecture cloud ?', desc: 'Vérifier l\'infrastructure technique' }
          ]"
          :key="sug.text"
          @click="query = sug.text; sendMessage()"
          class="p-4 bg-white/85 hover:bg-white border border-slate-200/75 rounded-2xl cursor-pointer hover:border-indigo-300 hover:shadow-md transition-all duration-200 flex flex-col justify-between group"
        >
          <span class="text-xs font-bold text-slate-700 group-hover:text-indigo-600 transition">{{ sug.text }}</span>
          <span class="text-[9px] text-slate-400 mt-2 font-semibold font-mono uppercase tracking-wider">{{ sug.desc }}</span>
        </div>
      </div>

      <div v-if="loading" class="text-indigo-600 text-xs font-semibold flex items-center space-x-2 animate-pulse pl-2">
        <span class="h-1.5 w-1.5 rounded-full bg-indigo-600 animate-ping"></span>
        <span>Recherche sémantique et synthèse de réponse...</span>
      </div>
    </div>
    
    <!-- Input Box (ChatGPT style) -->
    <div class="p-5 border-t border-slate-150 bg-white/90">
      <div class="relative max-w-3xl mx-auto flex items-center">
        <InputText 
          v-model="query" 
          @keyup.enter="sendMessage" 
          placeholder="Demandez n'importe quoi à propos de vos manuels techniques..." 
          class="w-full! pl-5! pr-14! py-3.5! bg-slate-50! border-slate-200! rounded-2xl! text-sm! text-slate-800! placeholder:text-slate-450! outline-none! focus:bg-white! focus:border-indigo-500! focus:ring-4! focus:ring-indigo-500/5! transition-all! font-medium! shadow-sm!" 
        />
        <button 
          @click="sendMessage" 
          :disabled="loading || !query.trim()"
          class="absolute right-2.5 p-2 bg-indigo-600 hover:bg-indigo-550 text-white rounded-xl transition disabled:opacity-40 disabled:hover:bg-indigo-600 cursor-pointer flex items-center justify-center shadow-md shadow-indigo-600/10"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4.5 w-4.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>
      <p class="text-center text-[9px] text-slate-400 mt-2 font-medium">Gemini peut faire des erreurs. Veuillez vérifier les informations importantes.</p>
    </div>
  </div>

  <!-- Document Viewer Modal -->
  <div v-if="showViewModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="bg-white border border-slate-200/80 p-6 rounded-3xl w-full max-w-2xl shadow-2xl relative flex flex-col max-h-[85vh]">
      <button @click="showViewModal = false" class="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition cursor-pointer">
        <X class="h-4 w-4" />
      </button>

      <div class="flex items-center space-x-3 mb-4 pb-3 border-b border-slate-100">
        <div class="h-10 w-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center shrink-0">
          <FileText class="h-5 w-5 text-indigo-600" />
        </div>
        <div>
          <h3 class="font-extrabold text-slate-800 text-sm truncate max-w-md">{{ selectedDocTitle }}</h3>
          <p class="text-[10px] text-slate-400 font-medium font-mono uppercase">Contenu extrait</p>
        </div>
      </div>

      <!-- Scrollable text content -->
      <div class="flex-1 overflow-y-auto pr-1 bg-slate-50 border border-slate-200/60 rounded-2xl p-4 text-xs text-slate-700 leading-relaxed whitespace-pre-wrap font-medium">
        <div v-if="loadingContent" class="flex flex-col items-center justify-center py-20 space-y-3">
          <span class="h-2 w-2 rounded-full bg-indigo-600 animate-ping"></span>
          <span class="text-slate-450 font-bold font-mono">Chargement du contenu...</span>
        </div>
        <template v-else>
          {{ selectedDocContent }}
        </template>
      </div>

      <div class="flex items-center justify-end pt-3 border-t border-slate-100 mt-4">
        <button @click="showViewModal = false" class="px-5 py-2.5 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition cursor-pointer">
          Fermer
        </button>
      </div>
    </div>
  </div>
</template>
