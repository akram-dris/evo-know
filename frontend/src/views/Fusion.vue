<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import { GitMerge, RefreshCw, Calendar, Cpu, Eye, X } from 'lucide-vue-next';
import Button from 'primevue/button';

const fusions = ref([]);
const loading = ref(true);
const selectedFusion = ref(null);
const showDetailModal = ref(false);
const triggeringFusion = ref(false);
const totalFusions = ref(0);

const fetchFusions = async (isLoadMore = false) => {
  if (isLoadMore && loading.value) return;
  loading.value = true;
  const limit = 10;
  const offset = isLoadMore ? fusions.value.length : 0;
  try {
    const res = await axios.get(`/api/v1/tasks/fusions?limit=${limit}&offset=${offset}`);
    if (isLoadMore) {
      fusions.value = [...fusions.value, ...res.data.items];
    } else {
      fusions.value = res.data.items;
    }
    totalFusions.value = res.data.total;
  } catch (err) {
    console.error("Error fetching fusions:", err);
  } finally {
    loading.value = false;
  }
};

const triggerFusion = async () => {
  if (triggeringFusion.value) return;
  triggeringFusion.value = true;
  
  const latestFusionIdBefore = fusions.value.length > 0 ? fusions.value[0].id : null;
  const initialCount = fusions.value.length;
  
  try {
    await axios.post('/api/v1/tasks/trigger/fusion');
    
    let attempts = 0;
    const maxAttempts = 15; // 15 * 1.5 = 22.5s max
    
    const poll = setInterval(async () => {
      attempts++;
      try {
        const res = await axios.get('/api/v1/tasks/fusions?limit=10&offset=0');
        const newFusionsData = res.data;
        
        if (newFusionsData.items.length > initialCount || (newFusionsData.items.length > 0 && newFusionsData.items[0].id !== latestFusionIdBefore)) {
          clearInterval(poll);
          fusions.value = newFusionsData.items;
          totalFusions.value = newFusionsData.total;
          triggeringFusion.value = false;
        }
      } catch (err) {
        console.error("Error polling fusions:", err);
      }
      
      if (attempts >= maxAttempts) {
        clearInterval(poll);
        triggeringFusion.value = false;
        fetchFusions(false);
      }
    }, 1500);
  } catch (err) {
    console.error("Error triggering fusion:", err);
    triggeringFusion.value = false;
  }
};

const viewDetails = (event) => {
  selectedFusion.value = event;
  showDetailModal.value = true;
};

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('fr-FR', options);
};

const handleWindowScroll = async (event) => {
  const target = event.target || document.documentElement;
  const isDoc = target === document || target === document.documentElement || target === window || target === document.body;
  const scrollHeight = isDoc ? document.documentElement.scrollHeight : target.scrollHeight;
  const scrollTop = isDoc ? (document.documentElement.scrollTop || document.body.scrollTop) : target.scrollTop;
  const clientHeight = isDoc ? document.documentElement.clientHeight : target.clientHeight;
  
  if (scrollHeight - scrollTop - clientHeight < 100) {
    if (fusions.value.length < totalFusions.value && !loading.value) {
      await fetchFusions(true);
    }
  }
};

onMounted(() => {
  fetchFusions(false);
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
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">T3 : Fusion de connaissances intelligente</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Consolidation historique des doublons détectés et résolus par DBSCAN et LLM.</p>
      </div>
      <div class="flex items-center space-x-3">
        <Button @click="triggerFusion" :disabled="triggeringFusion" class="bg-indigo-600! hover:bg-indigo-550! text-white! text-xs! px-4! py-2.5! rounded-xl! font-bold! transition! flex! items-center! border-none! cursor-pointer! disabled:opacity-50">
          <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': triggeringFusion}" />
          <span>{{ triggeringFusion ? 'Analyse...' : 'Dépister les fusions' }}</span>
        </Button>
        <Button @click="fetchFusions(false)" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2.5! rounded-xl! font-bold! border-slate-200/80! border! transition! flex! items-center! cursor-pointer!">
          <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': loading}" />
          <span>Actualiser</span>
        </Button>
      </div>
    </div>

    <div v-if="loading && fusions.length === 0" class="text-center py-24 text-slate-500 font-medium">Chargement des fusions complétées...</div>
    
    <div v-else-if="fusions.length === 0" class="bg-white border border-slate-200/50 rounded-3xl p-12 text-center shadow-[0_8px_30px_rgba(0,0,0,0.015)] space-y-5 max-w-xl mx-auto mt-10">
      <div class="h-16 w-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto shadow-sm">
        <GitMerge class="h-8 w-8" />
      </div>
      <div class="space-y-2">
        <h3 class="font-extrabold text-slate-800 text-lg">Aucune fusion de connaissances</h3>
        <p class="text-slate-500 text-sm leading-relaxed max-w-xs mx-auto font-medium">Aucun événement de fusion sémantique n'a été enregistré. Lancez le scan ou importez de nouveaux documents pour fusionner les doublons.</p>
      </div>
    </div>
    
    <div v-else class="space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div v-for="event in fusions" :key="event.id" 
             class="p-6 bg-white border border-slate-200/50 rounded-3xl shadow-[0_10px_35px_rgba(0,0,0,0.02)] space-y-5 hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group flex flex-col justify-between">
          <!-- Floating Indigo background decoration -->
          <div class="absolute -right-8 -top-8 w-24 h-24 rounded-full bg-gradient-to-tr from-indigo-500/5 to-violet-500/5 blur-lg pointer-events-none group-hover:scale-125 transition-transform duration-500"></div>

          <div class="space-y-5">
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
                <p class="font-extrabold text-[10px] text-slate-400 uppercase tracking-widest font-mono mb-2">Documents Source fusionnés :</p>
                <ul class="list-none space-y-2">
                  <li v-for="chunk in event.source_chunks" :key="chunk.id" class="flex flex-col text-slate-700 font-semibold bg-white p-2.5 rounded-xl border border-slate-200/50">
                    <span class="text-[10px] text-indigo-600 font-extrabold uppercase font-mono truncate mb-1">
                      📄 {{ chunk.document_title }}
                    </span>
                    <span class="text-slate-500 font-medium line-clamp-2 leading-relaxed text-[11px]">
                      {{ chunk.content }}
                    </span>
                  </li>
                </ul>
              </div>
              <div class="border-t border-slate-200/50 pt-3">
                <p class="font-extrabold text-[10px] text-slate-400 uppercase tracking-widest font-mono mb-2">Fragment final consolidé :</p>
                <div class="bg-indigo-50/30 border border-indigo-200/20 text-indigo-700 font-medium p-3 rounded-xl leading-relaxed text-[11px] line-clamp-3">
                  {{ event.merged_chunk ? event.merged_chunk.content : 'N/A' }}
                </div>
              </div>
            </div>
          </div>

          <div class="flex justify-end pt-3 border-t border-slate-100/60 mt-4">
            <Button @click="viewDetails(event)" class="bg-indigo-600! hover:bg-indigo-550! text-white! text-xs! px-4! py-2! rounded-xl! font-bold! transition! flex! items-center! border-none! cursor-pointer!">
              <Eye class="h-4 w-4 mr-1.5" />
              <span>Détails de la fusion</span>
            </Button>
          </div>
        </div>
      </div>

      <!-- Scroll pagination indicator -->
      <div v-if="fusions.length < totalFusions" class="text-center py-6 text-xs text-slate-400 font-bold bg-slate-50/50 rounded-2xl border border-dashed border-slate-200/80">
        Faites défiler vers le bas pour charger plus de fusions ({{ fusions.length }} affichées sur {{ totalFusions }})
      </div>
    </div>

    <!-- Fusion Detail Modal -->
    <div v-if="showDetailModal && selectedFusion" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl max-w-4xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-slate-200/50 relative overflow-hidden">
        <!-- Header -->
        <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <div>
            <h3 class="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <GitMerge class="h-5 w-5 text-indigo-600 mr-2" />
              <span>Inspection de la Fusion Sémantique</span>
            </h3>
            <p class="text-xs text-slate-500 mt-1">Comparaison des fragments originaux et du résultat consolidé (Similitude : {{ (selectedFusion.similarity_score * 100).toFixed(0) }}%)</p>
          </div>
          <button @click="showDetailModal = false" class="p-1.5 rounded-lg hover:bg-slate-200 text-slate-400 hover:text-slate-700 transition cursor-pointer">
            <X class="h-5 w-5" />
          </button>
        </div>
        
        <!-- Content -->
        <div class="p-6 overflow-y-auto space-y-6 flex-1">
          <!-- Source chunks -->
          <div>
            <h4 class="text-xs font-extrabold text-slate-400 uppercase tracking-widest font-mono mb-3">Fragments Sources (Avant la fusion)</h4>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div v-for="(chunk, idx) in selectedFusion.source_chunks" :key="chunk.id" class="p-4 bg-slate-50 border border-slate-200/60 rounded-2xl flex flex-col justify-between">
                <div>
                  <span class="bg-slate-200/70 text-slate-700 text-[10px] font-bold px-2 py-0.5 rounded-lg font-mono mb-2 inline-block">
                    Fragment #{{ idx + 1 }}
                  </span>
                  <div class="text-xs text-indigo-700 font-bold mb-2 flex items-center">
                    <span class="mr-1">📄</span> {{ chunk.document_title }}
                  </div>
                  <p class="text-slate-600 text-xs leading-relaxed whitespace-pre-wrap font-medium">
                    {{ chunk.content }}
                  </p>
                </div>
                <div class="text-[9px] text-slate-400 font-mono mt-3 text-right">
                  ID: {{ chunk.id }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- Merged chunk -->
          <div class="border-t border-slate-100 pt-5">
            <h4 class="text-xs font-extrabold text-slate-400 uppercase tracking-widest font-mono mb-3">Fragment Final Consolidé (Après fusion par LLM)</h4>
            <div class="p-5 bg-indigo-50/20 border border-indigo-250/20 rounded-2xl">
              <div class="text-xs text-indigo-700 font-bold mb-2 flex items-center">
                <span class="mr-1">✨</span> {{ selectedFusion.merged_chunk ? selectedFusion.merged_chunk.document_title : 'N/A' }}
              </div>
              <p class="text-slate-800 text-xs leading-relaxed whitespace-pre-wrap font-semibold">
                {{ selectedFusion.merged_chunk ? selectedFusion.merged_chunk.content : 'N/A' }}
              </p>
              <div class="text-[9px] text-indigo-400 font-mono mt-3 text-right">
                ID: {{ selectedFusion.merged_chunk ? selectedFusion.merged_chunk.id : 'N/A' }}
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer -->
        <div class="p-4 bg-slate-50 border-t border-slate-100 flex justify-end">
          <Button @click="showDetailModal = false" class="bg-slate-700! hover:bg-slate-650! text-white! text-xs! px-4! py-2! rounded-xl! font-bold! transition! cursor-pointer! border-none!">
            Fermer
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
