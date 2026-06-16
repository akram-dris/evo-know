<script setup>
import { ref, onMounted } from 'vue';
import { History, ShieldCheck, RefreshCw } from 'lucide-vue-next';
import axios from 'axios';
import Button from 'primevue/button';

const auditLogs = ref([]);
const loading = ref(true);

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('fr-FR', options);
};

const fetchAuditLogs = async () => {
  loading.value = true;
  try {
    const response = await axios.get(`/api/v1/audit`);
    auditLogs.value = response.data;
  } catch (error) {
    console.error("Error fetching audit logs:", error);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchAuditLogs();
});
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Registre d'audit XAI</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Piste d'audit et descriptions d'IA explicables pour les décisions autonomes.</p>
      </div>
      <Button @click="fetchAuditLogs" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2.5! rounded-xl! font-bold! border-slate-200/80! border! transition! flex! items-center! cursor-pointer!">
        <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': loading}" />
        <span>Actualiser</span>
      </Button>
    </div>

    <div v-if="loading" class="text-center py-24 text-slate-500 font-medium">Chargement des registres d'audit...</div>
    
    <div v-else class="bg-white border border-slate-200/50 rounded-3xl overflow-hidden shadow-[0_12px_35px_rgba(0,0,0,0.025)]">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead class="bg-slate-50/70 text-slate-400 text-[10px] font-bold uppercase tracking-wider font-mono border-b border-slate-200/40">
            <tr>
              <th class="p-5">Horodatage</th>
              <th class="p-5">Action</th>
              <th class="p-5">Composant Système</th>
              <th class="p-5">Explication IA</th>
              <th class="p-5 text-right">Statut</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-100/80">
            <tr v-for="log in auditLogs" :key="log.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="p-5 text-slate-450 font-semibold text-xs font-mono">{{ formatDate(log.performed_at) }}</td>
              <td class="p-5 font-bold text-slate-800">{{ log.action }}</td>
              <td class="p-5">
                <span class="bg-indigo-50 text-indigo-700 text-[10px] px-2.5 py-1 rounded-lg border border-indigo-200/20 font-bold font-mono">
                  {{ log.service }}
                </span>
              </td>
              <td class="p-5 text-slate-600 italic font-medium leading-relaxed max-w-sm">{{ log.explanation }}</td>
              <td class="p-5 text-right">
                <span class="inline-flex items-center space-x-1 text-emerald-700 bg-emerald-50 border border-emerald-250/20 px-2.5 py-1 rounded-lg text-xs font-bold font-mono">
                  <ShieldCheck class="h-3.5 w-3.5 mr-1 text-emerald-600" />
                  <span>VÉRIFIÉ</span>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
