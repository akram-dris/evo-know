<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const auditLogs = ref([]);

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('fr-FR', options);
};

const fetchAuditLogs = async () => {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/v1/audit`);
    auditLogs.value = response.data;
  } catch (error) {
    console.error("Error fetching audit logs:", error);
  }
};

onMounted(() => {
  fetchAuditLogs();
});
</script>

<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-slate-900">Registre d'audit XAI</h1>
      <p class="text-slate-600 text-sm mt-1">Piste d'audit et descriptions d'IA explicables pour les décisions autonomes.</p>
    </div>
    
    <div class="bg-white border border-slate-200 rounded-2xl overflow-hidden glass-panel">
      <table class="w-full text-left border-collapse">
        <thead class="bg-slate-50 text-slate-500 text-xs font-semibold uppercase tracking-wider">
          <tr>
            <th class="p-4 border-b border-slate-200">Horodatage</th>
            <th class="p-4 border-b border-slate-200">Action</th>
            <th class="p-4 border-b border-slate-200">Composant Système</th>
            <th class="p-4 border-b border-slate-200">Explication IA</th>
            <th class="p-4 border-b border-slate-200">Statut</th>
          </tr>
        </thead>
        <tbody class="text-sm divide-y divide-slate-200">
          <tr v-for="log in auditLogs" :key="log.id" class="hover:bg-slate-50">
            <td class="p-4 text-slate-500 font-mono text-xs">{{ formatDate(log.performed_at) }}</td>
            <td class="p-4 font-medium text-slate-800">{{ log.action }}</td>
            <td class="p-4"><span class="bg-indigo-50 text-indigo-700 text-xs px-2 py-0.5 rounded">{{ log.service }}</span></td>
            <td class="p-4 text-slate-600 italic">{{ log.explanation }}</td>
            <td class="p-4">
              <span class="text-xs text-emerald-600 font-semibold">Vérifié</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
