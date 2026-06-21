<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axiosInstance from 'axios';
import { ShieldAlert, ShieldCheck, Check, RefreshCw, Layers } from 'lucide-vue-next';
import Button from 'primevue/button';

const issues = ref([]);
const loading = ref(true);
const triggeringConsistency = ref(false);
const totalIssues = ref(0);

const fetchIssues = async (isLoadMore = false) => {
  if (isLoadMore && loading.value) return;
  loading.value = true;
  const limit = 10;
  const offset = isLoadMore ? issues.value.length : 0;
  try {
    const res = await axiosInstance.get(`/api/v1/tasks/consistency?limit=${limit}&offset=${offset}`);
    if (isLoadMore) {
      issues.value = [...issues.value, ...res.data.items];
    } else {
      issues.value = res.data.items;
    }
    totalIssues.value = res.data.total;
  } catch (err) {
    console.error("Error fetching consistency issues:", err);
  } finally {
    loading.value = false;
  }
};

const triggerConsistency = async () => {
  if (triggeringConsistency.value) return;
  triggeringConsistency.value = true;
  
  const latestIssueIdBefore = issues.value.length > 0 ? issues.value[0].id : null;
  const initialCount = issues.value.length;
  
  try {
    await axiosInstance.post('/api/v1/tasks/trigger/consistency');
    
    let attempts = 0;
    const maxAttempts = 15; // 15 * 1.5s = 22.5s max
    
    const poll = setInterval(async () => {
      attempts++;
      try {
        const res = await axiosInstance.get('/api/v1/tasks/consistency?limit=10&offset=0');
        const newIssuesData = res.data;
        
        if (newIssuesData.items.length > initialCount || (newIssuesData.items.length > 0 && newIssuesData.items[0].id !== latestIssueIdBefore)) {
          clearInterval(poll);
          issues.value = newIssuesData.items;
          totalIssues.value = newIssuesData.total;
          triggeringConsistency.value = false;
        }
      } catch (err) {
        console.error("Error polling consistency issues:", err);
      }
      
      if (attempts >= maxAttempts) {
        clearInterval(poll);
        triggeringConsistency.value = false;
        fetchIssues(false);
      }
    }, 1500);
  } catch (err) {
    console.error("Error triggering consistency check:", err);
    triggeringConsistency.value = false;
  }
};

const resolveIssue = async (id, choice) => {
  try {
    const savedUser = localStorage.getItem('user');
    const username = savedUser ? JSON.parse(savedUser).username : 'admin';

    await axiosInstance.post(`/api/v1/tasks/consistency/resolve/${id}`, {
      choice: choice,
      user: username
    });
    fetchIssues(false);
  } catch (err) {
    console.error("Error resolving consistency issue:", err);
  }
};

const handleWindowScroll = async (event) => {
  const target = event.target || document.documentElement;
  const isDoc = target === document || target === document.documentElement || target === window || target === document.body;
  const scrollHeight = isDoc ? document.documentElement.scrollHeight : target.scrollHeight;
  const scrollTop = isDoc ? (document.documentElement.scrollTop || document.body.scrollTop) : target.scrollTop;
  const clientHeight = isDoc ? document.documentElement.clientHeight : target.clientHeight;
  
  if (scrollHeight - scrollTop - clientHeight < 100) {
    if (issues.value.length < totalIssues.value && !loading.value) {
      await fetchIssues(true);
    }
  }
};

onMounted(() => {
  fetchIssues(false);
  window.addEventListener('scroll', handleWindowScroll, true);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleWindowScroll, true);
});
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">T4 : Analyse de cohérence logique</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Détecte et résout les contradictions logiques et structurelles dans le graphe de connaissances.</p>
      </div>
      <div class="flex items-center space-x-3">
        <Button @click="triggerConsistency" :disabled="triggeringConsistency" class="bg-indigo-600! hover:bg-indigo-550! text-white! text-xs! px-4! py-2.5! rounded-xl! font-bold! transition! flex! items-center! border-none! cursor-pointer! disabled:opacity-50">
          <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': triggeringConsistency}" />
          <span>{{ triggeringConsistency ? 'Analyse...' : 'Dépister les conflits' }}</span>
        </Button>
        <Button @click="fetchIssues(false)" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2.5! rounded-xl! font-bold! border-slate-200/80! border! transition! flex! items-center! cursor-pointer!">
          <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': loading}" />
          <span>Actualiser</span>
        </Button>
      </div>
    </div>

    <div v-if="loading && issues.length === 0" class="text-center py-24 text-slate-500 font-medium">Chargement des contradictions en cours...</div>
    
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
            <p class="text-xs text-slate-650 leading-relaxed font-semibold italic bg-white p-3 rounded-xl border border-slate-200/30">
              "Sauvegarde incrémentielle quotidienne programmée chaque nuit à 02:00 du matin..."
            </p>
          </div>

          <!-- Fragment B -->
          <div class="bg-amber-50/25 border border-amber-200/20 p-4.5 rounded-2xl space-y-2.5">
            <div class="flex items-center space-x-1.5 text-amber-750 font-bold text-[10px] uppercase font-mono tracking-wider">
              <Layers class="h-3.5 w-3.5" />
              <span>Fragment B (ID: {{ issue.chunk_b_id.substring(0, 8) }})</span>
            </div>
            <p class="text-xs text-slate-650 leading-relaxed font-semibold italic bg-white p-3 rounded-xl border border-slate-200/30">
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
      
      <!-- Scroll pagination indicator -->
      <div v-if="issues.length < totalIssues" class="text-center py-6 text-xs text-slate-400 font-bold bg-slate-50/50 rounded-2xl border border-dashed border-slate-200/80">
        Faites défiler vers le bas pour charger plus de conflits ({{ issues.length }} affichés sur {{ totalIssues }})
      </div>
    </div>
  </div>
</template>
