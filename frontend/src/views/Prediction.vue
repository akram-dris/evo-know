<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ShieldAlert, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-vue-next';

const predictions = ref([]);
const loading = ref(true);

const fetchPredictions = async () => {
  loading.value = true;
  try {
    const res = await axios.get('/api/v1/tasks/predictions');
    predictions.value = res.data;
  } catch (err) {
    console.error("Error fetching predictions:", err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchPredictions();
});
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-100 p-6 rounded-2xl border border-slate-200 glass-panel shadow-xs flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-slate-900">T1 : Prédiction des besoins de mise à jour</h1>
        <p class="text-slate-600 text-sm mt-1">Surveillance en temps réel de l'obsolescence calculée par les modèles LSTM et Prophet.</p>
      </div>
      <button @click="fetchPredictions" class="bg-indigo-600 hover:bg-indigo-500 text-white p-2.5 rounded-xl transition flex items-center space-x-1.5 text-xs font-semibold">
        <RefreshCw class="h-4 w-4" :class="{'animate-spin': loading}" />
        <span>Actualiser</span>
      </button>
    </div>

    <div v-if="loading" class="text-center py-20 text-slate-500">Chargement des prédictions d'obsolescence...</div>
    <div v-else class="bg-white border border-slate-200 rounded-2xl overflow-hidden glass-panel shadow-xs">
      <table class="w-full text-left border-collapse">
        <thead class="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider">
          <tr>
            <th class="p-4 border-b border-slate-200">Nom du Document</th>
            <th class="p-4 border-b border-slate-200">Département</th>
            <th class="p-4 border-b border-slate-200">Modèle Utilisé</th>
            <th class="p-4 border-b border-slate-200">Score d'Obsolescence</th>
            <th class="p-4 border-b border-slate-200">Priorité</th>
          </tr>
        </thead>
        <tbody class="text-sm divide-y divide-slate-200">
          <tr v-for="item in predictions" :key="item.id" class="hover:bg-slate-50">
            <td class="p-4 font-medium text-slate-800">{{ item.title }}</td>
            <td class="p-4 text-slate-600">{{ item.department }}</td>
            <td class="p-4 text-slate-500 font-mono text-xs">{{ item.model_version }}</td>
            <td class="p-4">
              <div class="flex items-center space-x-2">
                <span class="font-bold" :class="item.score > 0.7 ? 'text-rose-600' : (item.score > 0.4 ? 'text-amber-500' : 'text-emerald-600')">
                  {{ (item.score * 100).toFixed(0) }}%
                </span>
                <div class="w-24 bg-slate-100 rounded-full h-1.5 overflow-hidden">
                  <div class="h-full rounded-full" 
                       :class="item.score > 0.7 ? 'bg-rose-500' : (item.score > 0.4 ? 'bg-amber-500' : 'bg-emerald-500')"
                       :style="{ width: (item.score * 100) + '%' }"></div>
                </div>
              </div>
            </td>
            <td class="p-4">
              <span class="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="item.priority === 'Critical' ? 'bg-rose-50 text-rose-700 border border-rose-200/50' : (item.priority === 'High' ? 'bg-amber-50 text-amber-700 border border-amber-200/50' : 'bg-emerald-50 text-emerald-700 border border-emerald-200/50')">
                <ShieldAlert v-if="item.priority === 'Critical'" class="h-3 w-3" />
                <AlertTriangle v-else-if="item.priority === 'High'" class="h-3 w-3" />
                <CheckCircle v-else class="h-3 w-3" />
                <span>{{ item.priority }}</span>
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
