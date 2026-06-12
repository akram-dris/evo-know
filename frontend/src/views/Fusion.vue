<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { GitMerge, RefreshCw, Calendar, Cpu } from 'lucide-vue-next';

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
    <div class="bg-gradient-to-r from-white to-slate-100 p-6 rounded-2xl border border-slate-200 glass-panel shadow-xs flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">T3 : Fusion de connaissances intelligente</h1>
        <p class="text-slate-600 text-sm mt-1">Consolidation historique des doublons détectés et résolus par DBSCAN et LLM.</p>
      </div>
      <button @click="fetchFusions" class="bg-indigo-600 hover:bg-indigo-500 text-white p-2.5 rounded-xl transition flex items-center space-x-1.5 text-xs font-semibold">
        <RefreshCw class="h-4 w-4" :class="{'animate-spin': loading}" />
        <span>Actualiser</span>
      </button>
    </div>

    <div v-if="loading" class="text-center py-20 text-slate-500">Chargement des fusions complétées...</div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="event in fusions" :key="event.id" class="p-6 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-4 hover:border-indigo-400 transition-all duration-300 relative overflow-hidden">
        <!-- Floating Indigo background decoration -->
        <div class="absolute -right-8 -top-8 w-24 h-24 rounded-full bg-indigo-500/5 blur-lg pointer-events-none"></div>

        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div class="flex items-center space-x-2 text-indigo-600">
            <GitMerge class="h-5 w-5" />
            <span class="font-bold text-sm">Fusion ID: {{ event.id.substring(0, 8) }}</span>
          </div>
          <span class="bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded-full border border-indigo-150 font-medium font-mono uppercase">
            {{ event.method }}
          </span>
        </div>

        <div class="space-y-2.5">
          <div class="text-slate-600 text-xs flex items-center space-x-2">
            <Cpu class="h-4 w-4 text-slate-400" />
            <span>Score de similitude : <strong class="text-slate-800">{{ (event.similarity_score * 100).toFixed(0) }}%</strong></span>
          </div>
          <div class="text-slate-600 text-xs flex items-center space-x-2">
            <Calendar class="h-4 w-4 text-slate-400" />
            <span>Date d'exécution : <strong class="text-slate-800">{{ formatDate(event.performed_at) }}</strong></span>
          </div>
        </div>

        <div class="bg-slate-50 border border-slate-150 p-3.5 rounded-xl space-y-1.5 text-xs text-slate-500 leading-relaxed font-mono">
          <p class="font-bold text-slate-700">Fragments Source fusionnés :</p>
          <ul class="list-disc pl-4 space-y-1">
            <li v-for="cid in event.source_chunks" :key="cid" class="truncate">
              {{ cid }}
            </li>
          </ul>
          <p class="font-bold text-slate-700 mt-2">Fragment final généré :</p>
          <div class="text-indigo-600 font-semibold truncate">{{ event.merged_chunk }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
