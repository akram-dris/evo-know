<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ShieldAlert, ShieldCheck, Check, RefreshCw, Layers } from 'lucide-vue-next';
import Button from 'primevue/button';

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
    // Dynamically retrieve username
    const savedUser = localStorage.getItem('user');
    const username = savedUser ? JSON.parse(savedUser).username : 'admin';

    await axios.post(`/api/v1/tasks/consistency/resolve/${id}`, {
      choice: choice,
      user: username
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
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">T4 : Analyse de cohérence logique</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Détecte et résout les contradictions logiques et structurelles dans le graphe de connaissances.</p>
      </div>
      <Button @click="fetchIssues" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2.5! rounded-xl! font-bold! border-slate-200/80! border! transition! flex! items-center! cursor-pointer!">
        <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': loading}" />
        <span>Actualiser</span>
      </Button>
    </div>

    <div v-if="loading" class="text-center py-24 text-slate-500 font-medium">Chargement des contradictions en cours...</div>
    
    <div v-else class="space-y-6">
      <div v-for="issue in issues" :key="issue.id" class="p-6 bg-white border border-slate-200/50 rounded-3xl shadow-[0_12px_35px_rgba(0,0,0,0.02)] space-y-5">
        <div class="flex justify-between items-start">
          <div class="space-y-1.5">
            <div class="flex items-center space-x-2.5">
              <span class="inline-flex items-center space-x-1.5 text-xs font-bold px-3 py-1 rounded-full border"
                    :class="issue.resolved 
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-250/20' 
                            : 'bg-rose-50 text-rose-700 border-rose-250/20'">
                <ShieldCheck v-if="issue.resolved" class="h-3.5 w-3.5" />
                <ShieldAlert v-else class="h-3.5 w-3.5" />
                <span>{{ issue.resolved ? 'Résolu' : 'Contradiction Active' }}</span>
              </span>
              <span class="text-slate-400 text-xs font-bold font-mono">Similitude: {{ (issue.confidence * 100).toFixed(0) }}%</span>
            </div>
            <p class="text-slate-800 font-extrabold mt-3 text-sm leading-snug">{{ issue.description }}</p>
          </div>
          <span class="bg-slate-50 text-slate-600 text-[10px] px-2.5 py-1 rounded-lg border border-slate-200/40 font-bold font-mono">
            T4 API Gateway
          </span>
        </div>

        <!-- Comparative split layout for Fragment A and B -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Fragment A -->
          <div class="bg-indigo-50/25 border border-indigo-200/20 p-4.5 rounded-2xl space-y-2.5">
            <div class="flex items-center space-x-1.5 text-indigo-700 font-bold text-[10px] uppercase font-mono tracking-wider">
              <Layers class="h-3.5 w-3.5" />
              <span>Fragment A (ID: {{ issue.chunk_a_id.substring(0, 8) }})</span>
            </div>
            <p class="text-xs text-slate-600 leading-relaxed font-semibold italic bg-white p-3 rounded-xl border border-slate-200/30">
              "Sauvegarde incrémentielle quotidienne programmée chaque nuit à 02:00 du matin..."
            </p>
          </div>

          <!-- Fragment B -->
          <div class="bg-amber-50/25 border border-amber-200/20 p-4.5 rounded-2xl space-y-2.5">
            <div class="flex items-center space-x-1.5 text-amber-700 font-bold text-[10px] uppercase font-mono tracking-wider">
              <Layers class="h-3.5 w-3.5" />
              <span>Fragment B (ID: {{ issue.chunk_b_id.substring(0, 8) }})</span>
            </div>
            <p class="text-xs text-slate-600 leading-relaxed font-semibold italic bg-white p-3 rounded-xl border border-slate-200/30">
              "Toutes les sauvegardes de serveurs de production doivent s'exécuter strictement à 04:00 du matin..."
            </p>
          </div>
        </div>

        <div class="flex justify-between items-center pt-2.5 border-t border-slate-100/60">
          <div class="text-xs text-slate-450 font-bold">
            <span v-if="issue.resolved">Résolu par <strong class="text-slate-700 capitalize">{{ issue.resolved_by }}</strong></span>
            <span v-else class="flex items-center space-x-1 text-slate-400">Arbitrage manuel recommandé via LLM ou règles temporelles.</span>
          </div>
          
          <div v-if="!issue.resolved" class="flex space-x-2">
            <Button @click="resolveIssue(issue.id, 'keep_a')" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2! rounded-xl! font-bold! border-slate-200/60! border! transition! cursor-pointer!">
              Conserver A (02:00)
            </Button>
            <Button @click="resolveIssue(issue.id, 'keep_b')" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2! rounded-xl! font-bold! border-slate-200/60! border! transition! cursor-pointer!">
              Conserver B (04:00)
            </Button>
            <Button @click="resolveIssue(issue.id, 'merge')" class="bg-indigo-600! hover:bg-indigo-550! text-white! text-xs! px-4! py-2! rounded-xl! font-bold! shadow-md! shadow-indigo-600/10! transition! flex! items-center! cursor-pointer! border-none!">
              <Check class="h-3.5 w-3.5 mr-1.5" />
              <span>Fusionner via LLM</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
