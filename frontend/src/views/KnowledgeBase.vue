<script setup>
import { ref, computed } from 'vue';
import RAGChatbot from '../components/widgets/RAGChatbot.vue';
import { Search, FolderOpen, FileText, Calendar, Tag } from 'lucide-vue-next';
import axios from 'axios';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';

// Configure axios base URL from environment variable
axios.defaults.baseURL = import.meta.env.VITE_API_URL;

const searchQuery = ref('');
const selectedDept = ref('Tous');

const departments = ['Tous', 'Support IT', 'Infrastructure', 'Sécurité', 'R&D'];

const mockDocs = [
  { id: 1, title: "OSS-4G-Procedure-v2", type: "pdf", dept: "Support IT", date: "2026-06-12", author: "admin", status: "Actif" },
  { id: 2, title: "Backup-Policy-2025", type: "docx", dept: "Infrastructure", date: "2026-06-11", author: "expert", status: "Actif" },
  { id: 3, title: "Security-Protocol-v1", type: "txt", dept: "Sécurité", date: "2026-06-10", author: "reader", status: "Actif" },
  { id: 4, title: "Cloud-Architecture-Specs", type: "pdf", dept: "R&D", date: "2026-06-09", author: "admin", status: "Actif" }
];

const filteredDocs = computed(() => {
  return mockDocs.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          doc.author.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesDept = selectedDept.value === 'Tous' || doc.dept === selectedDept.value;
    return matchesSearch && matchesDept;
  });
});
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl">
      <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Base de connaissances</h1>
      <p class="text-slate-500 text-sm mt-2 font-medium">Recherche sémantique, exploration du graphe de relations et requêtage RAG.</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <!-- Left Column: Document Catalog Search -->
      <div class="lg:col-span-7 bg-white border border-slate-200/50 rounded-3xl p-6 shadow-sm space-y-6 flex flex-col h-[520px]">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="font-bold text-slate-800 text-sm flex items-center space-x-2">
            <FolderOpen class="h-4.5 w-4.5 text-indigo-600" />
            <span>Catalogue de Documents</span>
          </h3>
          <span class="text-[9px] text-slate-400 font-bold font-mono uppercase">{{ filteredDocs.length }} documents trouvés</span>
        </div>

        <!-- Search Bar -->
        <div class="relative">
          <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 pointer-events-none z-10">
            <Search class="h-4.5 w-4.5" />
          </span>
          <InputText 
            v-model="searchQuery" 
            placeholder="Rechercher par titre ou auteur..." 
            class="w-full pl-10! pr-4! py-2.5! bg-slate-50! border-slate-200! rounded-2xl! focus:border-indigo-500! focus:bg-white! outline-none! text-sm! text-slate-800! transition-all! font-medium! placeholder:text-slate-400!"
          />
        </div>

        <!-- Department Filters -->
        <div class="flex flex-wrap gap-2">
          <Button 
            v-for="dept in departments" 
            :key="dept" 
            @click="selectedDept = dept"
            :class="selectedDept === dept 
                    ? 'px-3.5! py-1.5! rounded-full! text-xs! font-bold! bg-indigo-600! text-white! shadow-sm! shadow-indigo-600/10! border-none! cursor-pointer!' 
                    : 'px-3.5! py-1.5! rounded-full! text-xs! font-bold! bg-slate-50! text-slate-500! hover:bg-slate-100! border-slate-200/50! border! cursor-pointer!'"
          >
            <span>{{ dept }}</span>
          </Button>
        </div>

        <!-- Document List -->
        <div class="flex-1 overflow-y-auto pr-1 space-y-3.5">
          <div v-for="doc in filteredDocs" :key="doc.id" 
               class="p-4 rounded-2xl border border-slate-200/60 bg-slate-50/20 hover:bg-slate-50/80 transition-all duration-200 flex justify-between items-center group">
            <div class="flex items-center space-x-3.5 min-w-0">
              <div class="h-10 w-10 rounded-xl bg-indigo-50 border border-indigo-100/30 flex items-center justify-center shrink-0">
                <FileText class="h-5 w-5 text-indigo-600" />
              </div>
              <div class="min-w-0">
                <p class="text-sm font-bold text-slate-800 truncate">{{ doc.title }}</p>
                <div class="flex items-center space-x-3 text-[10px] text-slate-450 font-semibold font-mono mt-1 flex-wrap gap-y-1">
                  <span class="flex items-center space-x-1">
                    <Tag class="h-3 w-3 text-slate-400" />
                    <span>{{ doc.dept }}</span>
                  </span>
                  <span class="flex items-center space-x-1">
                    <Calendar class="h-3 w-3 text-slate-400" />
                    <span>{{ doc.date }}</span>
                  </span>
                </div>
              </div>
            </div>
            
            <div class="flex items-center space-x-3.5 shrink-0">
              <span class="bg-indigo-50 text-indigo-700 text-[8px] font-bold font-mono tracking-wider uppercase px-2 py-0.5 rounded border border-indigo-250/20">
                {{ doc.author }}
              </span>
              <span class="h-2 w-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/35"></span>
            </div>
          </div>
          <div v-if="filteredDocs.length === 0" class="text-slate-400 font-medium text-center py-12">Aucun document ne correspond à vos critères.</div>
        </div>
      </div>

      <!-- Right Column: AI Chatbot -->
      <div class="lg:col-span-5">
        <RAGChatbot />
      </div>
    </div>
  </div>
</template>
