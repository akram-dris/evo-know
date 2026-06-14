<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { GitMerge, RefreshCw, Calendar, Cpu } from 'lucide-vue-next';
import Button from 'primevue/button';

const fusions = ref([]);
const loading = ref(true);

const fetchFusions = async () => {
  loading.value = true;
  try {
    const res = await axios.get('/api/v1/tasks/fusions');
    fusions.value = res.data;
  } catch (err) {
    console.error("Error fetching fusions:", err);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('fr-FR', options);
};

onMounted(() => {
  fetchFusions();
});
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">T3 : Fusion de connaissances intelligente</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Consolidation historique des doublons détectés et résolus par DBSCAN et LLM.</p>
      </div>
      <Button @click="fetchFusions" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2.5! rounded-xl! font-bold! border-slate-200/80! border! transition! flex! items-center! cursor-pointer!">
        <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': loading}" />
        <span>Actualiser</span>
      </Button>
    </div>

    <div v-if="loading" class="text-center py-24 text-slate-500 font-medium">Chargement des fusions complétées...</div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="event in fusions" :key="event.id" 
           class="p-6 bg-white border border-slate-200/50 rounded-3xl shadow-[0_10px_35px_rgba(0,0,0,0.02)] space-y-5 hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group">
        <!-- Floating Indigo background decoration -->
        <div class="absolute -right-8 -top-8 w-24 h-24 rounded-full bg-gradient-to-tr from-indigo-500/5 to-violet-500/5 blur-lg pointer-events-none group-hover:scale-125 transition-transform duration-500"></div>

        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div class="flex items-center space-x-2 text-indigo-600">
            <GitMerge class="h-5 w-5" />
            <span class="font-bold text-xs font-mono">ID: {{ event.id.substring(0, 8) }}</span>
          </div>
          <span class="bg-indigo-50 text-indigo-700 text-[9px] font-bold font-mono uppercase tracking-wider px-2.5 py-1 rounded-lg border border-indigo-200/20">
            {{ event.method }}
          </span>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="text-slate-500 text-xs flex items-center space-x-2 font-semibold">
            <Cpu class="h-4 w-4 text-indigo-600" />
            <span>Similitude : <strong class="text-slate-800">{{ (event.similarity_score * 100).toFixed(0) }}%</strong></span>
          </div>
          <div class="text-slate-500 text-xs flex items-center space-x-2 font-semibold justify-end">
            <Calendar class="h-4 w-4 text-indigo-600" />
            <span>{{ formatDate(event.performed_at) }}</span>
          </div>
        </div>

        <div class="bg-slate-50/70 border border-slate-200/40 p-4.5 rounded-2xl space-y-3.5 text-xs">
          <div>
            <p class="font-extrabold text-[10px] text-slate-400 uppercase tracking-widest font-mono mb-2">Fragments Source fusionnés :</p>
            <ul class="list-none space-y-1.5">
              <li v-for="cid in event.source_chunks" :key="cid" class="flex items-center space-x-2 text-slate-600 font-medium truncate">
                <span class="h-1.5 w-1.5 rounded-full bg-indigo-400 shrink-0"></span>
                <span class="font-mono text-[10px] bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200/35">{{ cid.substring(0, 8) }}</span>
              </li>
            </ul>
          </div>
          <div class="border-t border-slate-200/50 pt-3">
            <p class="font-extrabold text-[10px] text-slate-400 uppercase tracking-widest font-mono mb-2">Fragment final consolidé :</p>
            <div class="bg-indigo-50/30 border border-indigo-200/20 text-indigo-700 font-semibold p-3 rounded-xl leading-relaxed text-xs">
              {{ event.merged_chunk }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
