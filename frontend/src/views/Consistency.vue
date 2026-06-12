<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ShieldAlert, ShieldCheck, Check, RefreshCw } from 'lucide-vue-next';

const issues = ref([]);
const loading = ref(true);

const fetchIssues = async () => {
  loading.value = true;
  try {
    const res = await axios.get('/api/v1/tasks/consistency');
    issues.value = res.data;
  } catch (err) {
    console.error("Error fetching consistency issues:", err);
  } finally {
    loading.value = false;
  }
};

const resolveIssue = async (id, choice) => {
  try {
    await axios.post(`/api/v1/tasks/consistency/resolve/${id}`, {
      choice: choice,
      user: "Akram Dris"
    });
    fetchIssues(); // Refresh list after resolving
  } catch (err) {
    console.error("Error resolving consistency issue:", err);
  }
};

onMounted(() => {
  fetchIssues();
});
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-100 p-6 rounded-2xl border border-slate-200 glass-panel shadow-xs flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">T4 : Analyse de cohérence logique</h1>
        <p class="text-slate-600 text-sm mt-1">Détecte et résout les contradictions logiques et structurelles dans le graphe de connaissances.</p>
      </div>
      <button @click="fetchIssues" class="bg-indigo-600 hover:bg-indigo-500 text-white p-2.5 rounded-xl transition flex items-center space-x-1.5 text-xs font-semibold">
        <RefreshCw class="h-4 w-4" :class="{'animate-spin': loading}" />
        <span>Actualiser</span>
      </button>
    </div>

    <div v-if="loading" class="text-center py-20 text-slate-500">Chargement des contradictions en cours...</div>
    <div v-else class="space-y-4">
      <div v-for="issue in issues" :key="issue.id" class="p-6 bg-white border border-slate-200 rounded-2xl shadow-xs space-y-4">
        <div class="flex justify-between items-start">
          <div class="space-y-1">
            <div class="flex items-center space-x-2">
              <span class="inline-flex items-center space-x-1 text-xs font-semibold px-2 py-0.5 rounded-lg"
                    :class="issue.resolved ? 'bg-emerald-50 text-emerald-700 border border-emerald-200/50' : 'bg-rose-50 text-rose-700 border border-rose-200/50'">
                <ShieldCheck v-if="issue.resolved" class="h-3.5 w-3.5" />
                <ShieldAlert v-else class="h-3.5 w-3.5" />
                <span>{{ issue.resolved ? 'Résolu' : 'Contradiction Active' }}</span>
              </span>
              <span class="text-slate-400 text-xs font-mono">Similitude: {{ (issue.confidence * 100).toFixed(0) }}%</span>
            </div>
            <p class="text-slate-800 font-semibold mt-2 text-sm">{{ issue.description }}</p>
          </div>
          <span class="bg-slate-100 text-slate-700 text-xs px-2 py-1 rounded-md font-semibold font-mono">
            T4 API Gateway
          </span>
        </div>

        <div class="bg-slate-50 border border-slate-150 p-4 rounded-xl space-y-2 text-xs text-slate-600 leading-relaxed font-mono">
          <div class="grid grid-cols-2 gap-4 divide-x divide-slate-200">
            <div class="space-y-1">
              <p class="font-bold text-slate-700">Fragment A (ID: {{ issue.chunk_a_id.substring(0, 8) }}):</p>
              <p class="italic">"Sauvegarde incrémentielle quotidienne programmée chaque nuit à 02:00 du matin..."</p>
            </div>
            <div class="pl-4 space-y-1">
              <p class="font-bold text-slate-700">Fragment B (ID: {{ issue.chunk_b_id.substring(0, 8) }}):</p>
              <p class="italic">"Toutes les sauvegardes de serveurs de production doivent s'exécuter strictement à 04:00 du matin..."</p>
            </div>
          </div>
        </div>

        <div class="flex justify-between items-center pt-2">
          <div class="text-xs text-slate-500">
            <span v-if="issue.resolved">Résolu par <strong>{{ issue.resolved_by }}</strong></span>
            <span v-else>Arbitrage manuel recommandé via LLM ou règles temporelles.</span>
          </div>
          
          <div v-if="!issue.resolved" class="flex space-x-2">
            <button @click="resolveIssue(issue.id, 'keep_a')" class="bg-slate-100 hover:bg-slate-200 text-slate-750 text-xs px-4 py-2 rounded-lg font-semibold transition">
              Conserver A (02:00)
            </button>
            <button @click="resolveIssue(issue.id, 'keep_b')" class="bg-slate-100 hover:bg-slate-200 text-slate-750 text-xs px-4 py-2 rounded-lg font-semibold transition">
              Conserver B (04:00)
            </button>
            <button @click="resolveIssue(issue.id, 'merge')" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-4 py-2 rounded-lg font-semibold transition flex items-center space-x-1">
              <Check class="h-3.5 w-3.5" />
              <span>Fusionner via LLM</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
