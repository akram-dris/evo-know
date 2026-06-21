<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import { Lightbulb, RefreshCw, Check, Link2, Cpu, Eye, X } from 'lucide-vue-next';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';

const relations = ref([]);
const loading = ref(true);
const approving = ref({});
const toast = useToast();

const showDetailModal = ref(false);
const selectedRelation = ref(null);
const loadingDetails = ref(false);
const triggeringDiscovery = ref(false);
const totalRelations = ref(0);

const approveRelation = async (id) => {
  approving.value[id] = true;
  try {
    await axios.post(`/api/v1/tasks/discovery/approve/${id}`);
    toast.add({ severity: 'success', summary: 'Succès', detail: 'La relation a été approuvée et créée avec succès dans Neo4j.', life: 4000 });
    await fetchRelations(false);
  } catch (err) {
    console.error("Error approving relation:", err);
    toast.add({ severity: 'error', summary: 'Erreur', detail: 'Échec de la validation de la relation.', life: 4000 });
  } finally {
    approving.value[id] = false;
  }
};

const fetchRelations = async (isLoadMore = false) => {
  if (isLoadMore && loading.value) return;
  loading.value = true;
  const limit = 10;
  const offset = isLoadMore ? relations.value.length : 0;
  try {
    const res = await axios.get(`/api/v1/tasks/discovery?limit=${limit}&offset=${offset}`);
    if (isLoadMore) {
      relations.value = [...relations.value, ...res.data.items];
    } else {
      relations.value = res.data.items;
    }
    totalRelations.value = res.data.total;
  } catch (err) {
    console.error("Error fetching discovered relations:", err);
  } finally {
    loading.value = false;
  }
};

const triggerDiscovery = async () => {
  if (triggeringDiscovery.value) return;
  triggeringDiscovery.value = true;
  
  const latestRelationIdBefore = relations.value.length > 0 ? relations.value[0].id : null;
  const initialCount = relations.value.length;
  
  try {
    const res = await axios.post('/api/v1/tasks/trigger/discovery');
    if (res.data.status === 'error') {
      toast.add({ severity: 'warn', summary: 'Avertissement', detail: res.data.message, life: 4000 });
      triggeringDiscovery.value = false;
      return;
    }
    
    let attempts = 0;
    const maxAttempts = 15; // 15 * 1.5s = 22.5s max
    
    const poll = setInterval(async () => {
      attempts++;
      try {
        const response = await axios.get('/api/v1/tasks/discovery?limit=10&offset=0');
        const newRelationsData = response.data;
        
        if (newRelationsData.items.length > initialCount || (newRelationsData.items.length > 0 && newRelationsData.items[0].id !== latestRelationIdBefore)) {
          clearInterval(poll);
          relations.value = newRelationsData.items;
          totalRelations.value = newRelationsData.total;
          triggeringDiscovery.value = false;
          toast.add({ severity: 'success', summary: 'Succès', detail: 'Nouvelles relations découvertes avec succès.', life: 4000 });
        }
      } catch (err) {
        console.error("Error polling relations:", err);
      }
      
      if (attempts >= maxAttempts) {
        clearInterval(poll);
        triggeringDiscovery.value = false;
        fetchRelations(false);
      }
    }, 1500);
  } catch (err) {
    console.error("Error triggering discovery:", err);
    triggeringDiscovery.value = false;
  }
};

const fetchRelationDetails = async (rel) => {
  selectedRelation.value = rel;
  showDetailModal.value = true;
  loadingDetails.value = true;
  try {
    const res = await axios.get(`/api/v1/tasks/discovery/details/${rel.id}`);
    selectedRelation.value = res.data;
  } catch (err) {
    console.error("Error fetching relation details:", err);
  } finally {
    loadingDetails.value = false;
  }
};

const highlightText = (text, termA, termB) => {
  if (!text) return '';
  const escapeRegExp = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const termAEscaped = escapeRegExp(termA);
  const termBEscaped = escapeRegExp(termB);
  
  const regex = new RegExp(`(${termAEscaped}|${termBEscaped})`, 'gi');
  return text.replace(regex, (match) => {
    const isTermA = match.toLowerCase() === termA.toLowerCase();
    const bgClass = isTermA 
      ? 'bg-indigo-100 text-indigo-800 font-extrabold px-1 py-0.5 rounded' 
      : 'bg-emerald-100 text-emerald-800 font-extrabold px-1 py-0.5 rounded';
    return `<mark class="${bgClass}">${match}</mark>`;
  });
};

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('fr-FR', options);
};

const handleWindowScroll = async (event) => {
  const target = event.target || document.documentElement;
  const isDoc = target === document || target === document.documentElement || target === window || target === document.body;
  const scrollHeight = isDoc ? document.documentElement.scrollHeight : target.scrollHeight;
  const scrollTop = isDoc ? (document.documentElement.scrollTop || document.body.scrollTop) : target.scrollTop;
  const clientHeight = isDoc ? document.documentElement.clientHeight : target.clientHeight;
  
  if (scrollHeight - scrollTop - clientHeight < 100) {
    if (relations.value.length < totalRelations.value && !loading.value) {
      await fetchRelations(true);
    }
  }
};

onMounted(() => {
  fetchRelations(false);
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
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">T5 : Découverte automatique de connaissances</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Identifie de nouvelles relations sémantiques mûries par NER (CamemBERT) et Apriori.</p>
      </div>
      <div class="flex items-center space-x-3">
        <Button @click="triggerDiscovery" :disabled="triggeringDiscovery" class="bg-indigo-600! hover:bg-indigo-550! text-white! text-xs! px-4! py-2.5! rounded-xl! font-bold! transition! flex! items-center! border-none! cursor-pointer! disabled:opacity-50">
          <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': triggeringDiscovery}" />
          <span>{{ triggeringDiscovery ? 'Découverte...' : 'Lancer la découverte' }}</span>
        </Button>
        <Button @click="fetchRelations" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2.5! rounded-xl! font-bold! border-slate-200/80! border! transition! flex! items-center! cursor-pointer!">
          <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': loading}" />
          <span>Actualiser</span>
        </Button>
      </div>
    </div>

    <div v-if="loading && relations.length === 0" class="text-center py-24 text-slate-500 font-medium">Chargement des relations découvertes...</div>
    
    <div v-else-if="relations.length === 0" class="bg-white border border-slate-200/50 rounded-3xl p-12 text-center shadow-[0_8px_30px_rgba(0,0,0,0.015)] space-y-5 max-w-xl mx-auto mt-10">
      <div class="h-16 w-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto shadow-sm">
        <Lightbulb class="h-8 w-8" />
      </div>
      <div class="space-y-2">
        <h3 class="font-extrabold text-slate-800 text-lg">Aucune relation découverte</h3>
        <p class="text-slate-500 text-sm leading-relaxed max-w-xs mx-auto font-medium">Aucune nouvelle relation sémantique n'a été identifiée. Importez des documents ou lancez la découverte pour extraire de nouvelles connaissances.</p>
      </div>
    </div>
    
    <div v-else class="space-y-4">
      <div class="bg-white border border-slate-200/50 rounded-3xl overflow-hidden shadow-[0_12px_35px_rgba(0,0,0,0.025)]">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead class="bg-slate-50/70 text-slate-400 text-[10px] font-bold uppercase tracking-wider font-mono border-b border-slate-200/40">
              <tr>
                <th class="p-5">Concept Source (A)</th>
                <th class="p-5">Type de Relation</th>
                <th class="p-5">Concept Cible (B)</th>
                <th class="p-5">Score de Confiance</th>
                <th class="p-5">Méthode Extraction</th>
                <th class="p-5">Découvert le</th>
                <th class="p-5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="text-sm divide-y divide-slate-100/80">
              <tr v-for="rel in relations" :key="rel.id" class="hover:bg-slate-50/50 transition-colors">
                <td class="p-5 font-bold text-slate-800">
                  <div class="flex items-center space-x-2">
                    <span class="h-2 w-2 rounded-full bg-indigo-500 shadow-sm shadow-indigo-500/35"></span>
                    <span>{{ rel.entity_a }}</span>
                  </div>
                </td>
                <td class="p-5">
                  <span class="text-indigo-600 font-bold font-mono text-[10px] bg-indigo-50/80 border border-indigo-200/20 px-2.5 py-1 rounded-lg">
                    {{ rel.relation_type }}
                  </span>
                </td>
                <td class="p-5 font-bold text-slate-800">
                  <div class="flex items-center space-x-2">
                    <span class="h-2 w-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/35"></span>
                    <span>{{ rel.entity_b }}</span>
                  </div>
                </td>
                <td class="p-5">
                  <span class="font-extrabold text-xs font-mono text-indigo-600 bg-indigo-50 border border-indigo-200/20 px-2.5 py-1 rounded-lg">
                    {{ (rel.confidence * 100).toFixed(0) }}%
                  </span>
                </td>
                <td class="p-5">
                  <span class="bg-slate-50 text-slate-600 text-[10px] px-2.5 py-1 rounded-lg border border-slate-200/40 font-bold font-mono">
                    {{ rel.method }}
                  </span>
                </td>
                <td class="p-5 text-slate-550 font-semibold text-xs">{{ formatDate(rel.discovered_at) }}</td>
                <td class="p-5 text-right">
                  <div class="flex items-center justify-end space-x-2">
                    <Button 
                      @click="fetchRelationDetails(rel)" 
                      class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! p-2.5! rounded-xl! font-bold! border-slate-200/80! border! transition! flex! items-center! cursor-pointer!"
                      title="Inspecter la relation"
                    >
                      <Eye class="h-4.5 w-4.5 text-slate-650" />
                    </Button>
                    <Button 
                      @click="approveRelation(rel.id)" 
                      :disabled="approving[rel.id]" 
                      class="bg-emerald-600! hover:bg-emerald-550! text-white! text-xs! px-4! py-2! rounded-xl! font-bold! shadow-md! shadow-emerald-600/10! transition! flex! items-center! border-none! cursor-pointer! disabled:opacity-50"
                    >
                      <RefreshCw v-if="approving[rel.id]" class="h-4 w-4 mr-1.5 animate-spin" />
                      <Check v-else class="h-4 w-4 mr-1.5" />
                      <span>{{ approving[rel.id] ? 'Approbation...' : 'Approuver' }}</span>
                    </Button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Scroll pagination indicator -->
      <div v-if="relations.length < totalRelations" class="text-center py-6 text-xs text-slate-400 font-bold bg-slate-50/50 rounded-2xl border border-dashed border-slate-200/80">
        Faites défiler vers le bas pour charger plus de relations ({{ relations.length }} affichées sur {{ totalRelations }})
      </div>
    </div>

    <!-- Discovery Detail Modal -->
    <div v-if="showDetailModal && selectedRelation" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl border border-slate-200/50 relative overflow-hidden">
        <!-- Header -->
        <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <div>
            <h3 class="text-lg font-bold text-slate-900 flex items-center space-x-2">
              <Lightbulb class="h-5 w-5 text-indigo-650 mr-2" />
              <span>Inspection de la Relation Découverte</span>
            </h3>
            <p class="text-xs text-slate-500 mt-1">Vérification de la cohérence et extraction des contextes du corpus.</p>
          </div>
          <button @click="showDetailModal = false" class="p-1.5 rounded-lg hover:bg-slate-200 text-slate-400 hover:text-slate-700 transition cursor-pointer">
            <X class="h-5 w-5" />
          </button>
        </div>
        
        <!-- Content -->
        <div class="p-6 overflow-y-auto space-y-6 flex-1">
          <!-- Flow diagram concept representation -->
          <div class="bg-gradient-to-r from-indigo-50/50 via-slate-50 to-emerald-50/50 p-5 rounded-2xl border border-slate-200/45 flex items-center justify-center space-x-4">
            <div class="bg-white border border-indigo-200/60 shadow-sm px-4 py-2.5 rounded-xl font-bold text-indigo-800 text-sm flex items-center space-x-1.5">
              <span class="h-2 w-2 rounded-full bg-indigo-500"></span>
              <span>{{ selectedRelation.entity_a }}</span>
            </div>
            
            <div class="flex flex-col items-center">
              <span class="text-[9px] font-bold text-indigo-650 font-mono uppercase bg-indigo-50 border border-indigo-200/20 px-2 py-0.5 rounded-md mb-1 shadow-sm">
                {{ selectedRelation.relation_type }}
              </span>
              <div class="flex items-center text-slate-300 font-mono text-xs">
                <span>───────</span>
                <span class="text-slate-400 font-bold ml-0.5">▶</span>
              </div>
              <span class="text-[9px] text-slate-400 font-mono mt-1">Confiance : {{ (selectedRelation.confidence * 100).toFixed(0) }}%</span>
            </div>
            
            <div class="bg-white border border-emerald-200/60 shadow-sm px-4 py-2.5 rounded-xl font-bold text-emerald-800 text-sm flex items-center space-x-1.5">
              <span class="h-2 w-2 rounded-full bg-emerald-500"></span>
              <span>{{ selectedRelation.entity_b }}</span>
            </div>
          </div>
          
          <!-- Context / Documents list -->
          <div>
            <h4 class="text-xs font-extrabold text-slate-400 uppercase tracking-widest font-mono mb-3">Contextes et Preuves de Co-occurrence</h4>
            
            <div v-if="loadingDetails" class="text-center py-8 text-slate-500 font-semibold text-xs flex items-center justify-center space-x-2">
              <RefreshCw class="h-4 w-4 animate-spin text-indigo-600" />
              <span>Chargement des preuves contextuelles...</span>
            </div>
            
            <div v-else-if="!selectedRelation.contexts || selectedRelation.contexts.length === 0" class="text-center py-8 text-slate-400 text-xs font-semibold">
              Aucun document ou contexte direct n'a pu être extrait.
            </div>
            
            <div v-else class="space-y-4">
              <div v-for="ctx in selectedRelation.contexts" :key="ctx.document_id" class="p-4.5 bg-slate-50 border border-slate-200/50 rounded-2xl space-y-2">
                <div class="flex justify-between items-start">
                  <div class="text-xs font-extrabold text-slate-800 flex items-center">
                    <span class="mr-1.5 text-sm">📄</span> {{ ctx.document_title }}
                  </div>
                  <span class="bg-slate-200/50 text-slate-650 text-[9px] font-extrabold uppercase px-2 py-0.5 rounded-md font-mono">
                    {{ ctx.department }}
                  </span>
                </div>
                <p class="text-slate-650 text-xs leading-relaxed font-medium bg-white p-3 rounded-xl border border-slate-200/30 shadow-inner" v-html="highlightText(ctx.snippet, selectedRelation.entity_a, selectedRelation.entity_b)">
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Footer -->
        <div class="p-4 bg-slate-50 border-t border-slate-100 flex justify-between">
          <span class="text-[10px] text-slate-400 font-mono self-center">Méthode : {{ selectedRelation.method }}</span>
          <Button @click="showDetailModal = false" class="bg-slate-700! hover:bg-slate-650! text-white! text-xs! px-4! py-2! rounded-xl! font-bold! transition! cursor-pointer! border-none!">
            Fermer
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>
