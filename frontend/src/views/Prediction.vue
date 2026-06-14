<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { ShieldAlert, CheckCircle, AlertTriangle, RefreshCw } from 'lucide-vue-next';
import Button from 'primevue/button';

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
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">T1 : Prédiction des besoins de mise à jour</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Surveillance en temps réel de l'obsolescence calculée par les modèles LSTM et Prophet.</p>
      </div>
      <Button @click="fetchPredictions" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2.5! rounded-xl! font-bold! border-slate-200/80! border! transition! flex! items-center! cursor-pointer!">
        <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': loading}" />
        <span>Actualiser</span>
      </Button>
    </div>

    <div v-if="loading" class="text-center py-24 text-slate-500 font-medium">Chargement des prédictions d'obsolescence...</div>
    
    <div v-else class="bg-white border border-slate-200/50 rounded-3xl overflow-hidden shadow-[0_12px_35px_rgba(0,0,0,0.025)]">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead class="bg-slate-50/70 text-slate-400 text-[10px] font-bold uppercase tracking-wider font-mono border-b border-slate-200/40">
            <tr>
              <th class="p-5">Nom du Document</th>
              <th class="p-5">Département</th>
              <th class="p-5">Modèle Utilisé</th>
              <th class="p-5">Score d'Obsolescence</th>
              <th class="p-5">Priorité</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-100/80">
            <tr v-for="item in predictions" :key="item.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="p-5 font-bold text-slate-800">{{ item.title }}</td>
              <td class="p-5 text-slate-500 font-semibold">{{ item.department }}</td>
              <td class="p-5">
                <span class="bg-slate-50 text-slate-600 text-[10px] px-2.5 py-1 rounded-lg border border-slate-200/40 font-bold font-mono">
                  {{ item.model_version }}
                </span>
              </td>
              <td class="p-5">
                <div class="flex items-center space-x-3">
                  <span class="font-bold text-xs font-mono w-10 text-right" :class="item.score > 0.7 ? 'text-rose-600' : (item.score > 0.4 ? 'text-amber-500' : 'text-emerald-600')">
                    {{ (item.score * 100).toFixed(0) }}%
                  </span>
                  <div class="w-32 bg-slate-100 rounded-full h-2 overflow-hidden shadow-inner">
                    <div class="h-full rounded-full transition-all duration-500" 
                         :class="item.score > 0.7 ? 'bg-gradient-to-r from-rose-500 to-rose-600' : (item.score > 0.4 ? 'bg-gradient-to-r from-amber-400 to-amber-500' : 'bg-gradient-to-r from-emerald-500 to-emerald-600')"
                         :style="{ width: (item.score * 100) + '%' }"></div>
                  </div>
                </div>
              </td>
              <td class="p-5">
                <span class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold"
                      :class="item.priority === 'Critical' ? 'bg-rose-50 text-rose-700 border border-rose-250/30' : (item.priority === 'High' ? 'bg-amber-50 text-amber-700 border border-amber-250/30' : 'bg-emerald-50 text-emerald-700 border border-emerald-250/30')">
                  <ShieldAlert v-if="item.priority === 'Critical'" class="h-3.5 w-3.5" />
                  <AlertTriangle v-else-if="item.priority === 'High'" class="h-3.5 w-3.5" />
                  <CheckCircle v-else class="h-3.5 w-3.5" />
                  <span>{{ item.priority === 'Critical' ? 'Critique' : (item.priority === 'High' ? 'Haute' : 'Normale') }}</span>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
