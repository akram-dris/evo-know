<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { Lightbulb, RefreshCw, Check, Link2, Cpu } from 'lucide-vue-next';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';

const relations = ref([]);
const loading = ref(true);
const approving = ref({});
const toast = useToast();

const approveRelation = async (id) => {
  approving.value[id] = true;
  try {
    await axios.post(`/api/v1/tasks/discovery/approve/${id}`);
    toast.add({ severity: 'success', summary: 'Succès', detail: 'La relation a été approuvée et créée avec succès dans Neo4j.', life: 4000 });
    await fetchRelations();
  } catch (err) {
    console.error("Error approving relation:", err);
    toast.add({ severity: 'error', summary: 'Erreur', detail: 'Échec de la validation de la relation.', life: 4000 });
  } finally {
    approving.value[id] = false;
  }
};

const fetchRelations = async () => {
  loading.value = true;
  try {
    const res = await axios.get('/api/v1/tasks/discovery');
    relations.value = res.data;
  } catch (err) {
    console.error("Error fetching discovered relations:", err);
  } finally {
    loading.value = false;
  }
};

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric' };
  return new Date(dateString).toLocaleDateString('fr-FR', options);
};

onMounted(() => {
  fetchRelations();
});
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">T5 : Découverte automatique de connaissances</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Identifie de nouvelles relations sémantiques mûries par NER (CamemBERT) et Apriori.</p>
      </div>
      <Button @click="fetchRelations" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2.5! rounded-xl! font-bold! border-slate-200/80! border! transition! flex! items-center! cursor-pointer!">
        <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': loading}" />
        <span>Actualiser</span>
      </Button>
    </div>

    <div v-if="loading" class="text-center py-24 text-slate-500 font-medium">Chargement des relations découvertes...</div>
    
    <div v-else class="bg-white border border-slate-200/50 rounded-3xl overflow-hidden shadow-[0_12px_35px_rgba(0,0,0,0.025)]">
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
              <th class="p-5 text-right">Action</th>
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
              <td class="p-5 font-bold text-slate-800">{{ rel.entity_b }}</td>
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
                <Button 
                  @click="approveRelation(rel.id)" 
                  :disabled="approving[rel.id]" 
                  class="bg-emerald-600! hover:bg-emerald-550! text-white! text-xs! px-4! py-2! rounded-xl! font-bold! shadow-md! shadow-emerald-600/10! transition! flex! items-center! ml-auto! border-none! cursor-pointer disabled:opacity-50"
                >
                  <RefreshCw v-if="approving[rel.id]" class="h-4 w-4 mr-1.5 animate-spin" />
                  <Check v-else class="h-4 w-4 mr-1.5" />
                  <span>{{ approving[rel.id] ? 'Approbation...' : 'Approuver & Créer Link Neo4j' }}</span>
                </Button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
