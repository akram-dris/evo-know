<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { Lightbulb, RefreshCw, Check, Link2, Cpu } from 'lucide-vue-next';

const relations = ref([]);
const loading = ref(true);

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
    <div class="bg-gradient-to-r from-white to-slate-100 p-6 rounded-2xl border border-slate-200 glass-panel shadow-xs flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">T5 : Découverte automatique de connaissances</h1>
        <p class="text-slate-600 text-sm mt-1">Identifie de nouvelles relations sémantiques mûries par NER (CamemBERT) et Apriori.</p>
      </div>
      <button @click="fetchRelations" class="bg-indigo-600 hover:bg-indigo-500 text-white p-2.5 rounded-xl transition flex items-center space-x-1.5 text-xs font-semibold">
        <RefreshCw class="h-4 w-4" :class="{'animate-spin': loading}" />
        <span>Actualiser</span>
      </button>
    </div>

    <div v-if="loading" class="text-center py-20 text-slate-500">Chargement des relations découvertes...</div>
    <div v-else class="bg-white border border-slate-200 rounded-2xl overflow-hidden glass-panel shadow-xs">
      <table class="w-full text-left border-collapse">
        <thead class="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider">
          <tr>
            <th class="p-4 border-b border-slate-200">Concept Source (A)</th>
            <th class="p-4 border-b border-slate-200">Type de Relation</th>
            <th class="p-4 border-b border-slate-200">Concept Cible (B)</th>
            <th class="p-4 border-b border-slate-200">Score de Confiance</th>
            <th class="p-4 border-b border-slate-200">Méthode Extraction</th>
            <th class="p-4 border-b border-slate-200">Découvert le</th>
            <th class="p-4 border-b border-slate-200">Action</th>
          </tr>
        </thead>
        <tbody class="text-sm divide-y divide-slate-200">
          <tr v-for="rel in relations" :key="rel.id" class="hover:bg-slate-50">
            <td class="p-4 font-bold text-slate-800 flex items-center space-x-2">
              <span class="h-2 w-2 rounded-full bg-indigo-500"></span>
              <span>{{ rel.entity_a }}</span>
            </td>
            <td class="p-4 text-slate-600 font-mono text-xs text-indigo-700 font-semibold">{{ rel.relation_type }}</td>
            <td class="p-4 font-bold text-slate-800">{{ rel.entity_b }}</td>
            <td class="p-4">
              <span class="font-bold text-indigo-600 bg-indigo-50/70 border border-indigo-200/50 px-2 py-0.5 rounded text-xs font-mono">
                {{ (rel.confidence * 100).toFixed(0) }}%
              </span>
            </td>
            <td class="p-4"><span class="bg-slate-100 text-slate-700 text-xs px-2 py-0.5 rounded font-mono">{{ rel.method }}</span></td>
            <td class="p-4 text-slate-500 font-mono text-xs">{{ formatDate(rel.discovered_at) }}</td>
            <td class="p-4">
              <button class="bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-3 py-1.5 rounded-lg transition flex items-center space-x-1 font-semibold">
                <Check class="h-3.5 w-3.5" />
                <span>Approuver & Créer Link Neo4j</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
