<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import MarkdownIt from 'markdown-it';

const md = new MarkdownIt();

const reports = ref([]);
const selectedReport = ref(null);
const compareMode = ref(false);

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('fr-FR', options);
};

const fetchReports = async () => {
  try {
    const response = await axios.get(`${import.meta.env.VITE_API_URL}/reports`);
    reports.value = response.data.map(report => ({
      ...report,
      content_html: md.render(report.content_md) // Convert markdown to HTML
    }));
    if (reports.value.length > 0) {
      selectedReport.value = reports.value[0]; // Select the first report by default
    }
  } catch (error) {
    console.error("Error fetching reports:", error);
  }
};

const selectReport = (report) => {
  selectedReport.value = report;
};

onMounted(() => {
  fetchReports();
});
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-100 p-6 rounded-2xl border border-slate-200 glass-panel shadow-xs">
      <h1 class="text-2xl font-bold text-slate-900">T2 : Rapports générés automatiquement</h1>
      <p class="text-slate-600 text-sm mt-1">Rapports markdown automatiques et synthèse de contenu LLM NLG.</p>
    </div>

    <div class="grid grid-cols-3 gap-6">
      <!-- Left Column: Report List -->
      <div class="col-span-1 bg-white border border-slate-200 rounded-xl p-4 space-y-4 glass-panel shadow-xs">
        <h3 class="font-semibold text-slate-900">Historical Reports</h3>
        <div class="space-y-2">
          <div v-for="rep in reports" :key="rep.id" @click="selectReport(rep)" 
               class="p-3 rounded-lg bg-slate-50 border border-slate-200 hover:border-indigo-500 cursor-pointer transition">
            <div class="flex justify-between text-xs text-slate-500">
              <span>{{ rep.report_type }}</span>
              <span>{{ formatDate(rep.generated_at) }}</span>
            </div>
            <p class="text-sm font-medium text-slate-800 mt-1">{{ rep.report_type }} Report</p>
          </div>
        </div>
      </div>
      
      <!-- Right Column: Document Viewer and Comparison -->
      <div class="col-span-2 bg-white border border-slate-200 rounded-xl p-6 glass-panel shadow-xs space-y-4">
        <div v-if="selectedReport" class="space-y-4">
          <div class="flex justify-between items-center border-b border-slate-200 pb-3">
            <h2 class="text-xl font-bold text-slate-900">{{ selectedReport.report_type }} Report</h2>
            <div class="flex space-x-2">
              <button class="bg-indigo-600 text-white text-xs px-3 py-1.5 rounded-lg hover:bg-indigo-500 transition">Download PDF</button>
              <button class="bg-slate-800 text-white text-xs px-3 py-1.5 rounded-lg hover:bg-slate-700 transition" @click="compareMode = !compareMode">Compare Versions</button>
            </div>
          </div>
          
          <div class="prose prose-sm max-w-none text-slate-700 leading-relaxed" v-html="selectedReport.content_html"></div>
        </div>
        <div v-else class="text-slate-500 text-center py-20">Select a report from the list to view its contents.</div>
      </div>
    </div>
  </div>
</template>

<style>
@reference "tailwindcss";

/* Basic prose styling for markdown content */
.prose {
  h1 { @apply text-2xl font-bold mb-4; }
  h2 { @apply text-xl font-semibold mb-3; }
  h3 { @apply text-lg font-medium mb-2; }
  ul { @apply list-disc pl-5; }
  ol { @apply list-decimal pl-5; }
  li { @apply mb-1; }
  p { @apply mb-3; }
  table { @apply w-full border-collapse my-4; }
  th, td { @apply border border-slate-300 p-2 text-left; }
  th { @apply bg-slate-100 font-semibold; }
}
</style>
