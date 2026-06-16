<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import axios from 'axios';
import MarkdownIt from 'markdown-it';
import Button from 'primevue/button';

const md = new MarkdownIt();

const reports = ref([]);
const selectedReport = ref(null);
const compareMode = ref(false);
const compareReportId = ref(null);

const otherReportsOfSameType = computed(() => {
  if (!selectedReport.value) return [];
  return reports.value.filter(r => r.id !== selectedReport.value.id && r.report_type === selectedReport.value.report_type);
});

const compareReport = computed(() => {
  if (!compareReportId.value) return null;
  return reports.value.find(r => r.id === compareReportId.value);
});

watch(selectedReport, (newVal) => {
  if (newVal) {
    const alternatives = reports.value.filter(r => r.id !== newVal.id && r.report_type === newVal.report_type);
    if (alternatives.length > 0) {
      compareReportId.value = alternatives[0].id;
    } else {
      compareReportId.value = null;
    }
  }
});

watch(compareMode, (newVal) => {
  if (newVal && selectedReport.value && !compareReportId.value) {
    const alternatives = reports.value.filter(r => r.id !== selectedReport.value.id && r.report_type === selectedReport.value.report_type);
    if (alternatives.length > 0) {
      compareReportId.value = alternatives[0].id;
    }
  }
});

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
  return new Date(dateString).toLocaleDateString('fr-FR', options);
};

const fetchReports = async () => {
  try {
    const response = await axios.get(`/api/v1/reports`);
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

const downloadPDF = () => {
  if (!selectedReport.value) return;
  
  // Create a hidden iframe for printing
  const iframe = document.createElement('iframe');
  iframe.style.position = 'fixed';
  iframe.style.right = '0';
  iframe.style.bottom = '0';
  iframe.style.width = '0';
  iframe.style.height = '0';
  iframe.style.border = '0';
  document.body.appendChild(iframe);
  
  const doc = iframe.contentWindow.document;
  doc.write(`
    <html>
      <head>
        <title>Rapport - ${selectedReport.value.report_type}</title>
        <style>
          body {
            font-family: sans-serif;
            padding: 40px;
            color: #1e293b;
            line-height: 1.6;
          }
          h1 {
            color: #0f172a;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 10px;
            font-size: 24px;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
          }
          th, td {
            border: 1px solid #cbd5e1;
            padding: 10px;
            text-align: left;
            font-size: 12px;
          }
          th {
            background-color: #f8fafc;
            font-weight: bold;
          }
          .meta {
            font-size: 11px;
            color: #64748b;
            margin-bottom: 30px;
            font-family: monospace;
          }
        </style>
      </head>
      <body>
        <h1>Rapport ${selectedReport.value.report_type}</h1>
        <div class="meta">Généré le : ${formatDate(selectedReport.value.generated_at)}</div>
        <div>${selectedReport.value.content_html}</div>
      </body>
    </html>
  `);
  doc.close();
  
  // Wait for content rendering and launch print
  setTimeout(() => {
    iframe.contentWindow.focus();
    iframe.contentWindow.print();
    // Clean up iframe
    setTimeout(() => {
      document.body.removeChild(iframe);
    }, 1000);
  }, 150);
};

onMounted(() => {
  fetchReports();
});
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl">
      <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">T2 : Rapports générés automatiquement</h1>
      <p class="text-slate-500 text-sm mt-2 font-medium">Rapports markdown automatiques et synthèse de contenu LLM NLG.</p>
    </div>

    <div class="grid grid-cols-3 gap-6">
      <!-- Left Column: Report List -->
      <div class="col-span-1 bg-white border border-slate-200/50 rounded-3xl p-5 space-y-4 shadow-sm flex flex-col h-[600px]">
        <h3 class="font-bold text-slate-800 text-sm border-b border-slate-100 pb-2.5">Rapports Historiques</h3>
        <div class="space-y-3 overflow-y-auto flex-1 pr-1">
          <div v-for="rep in reports" :key="rep.id" @click="selectReport(rep)" 
               class="p-4 rounded-2xl border cursor-pointer transition-all duration-200"
               :class="selectedReport && selectedReport.id === rep.id 
                       ? 'bg-indigo-50/50 border-indigo-400/80 shadow-xs' 
                       : 'bg-slate-50/50 border-slate-200/60 hover:bg-slate-50 hover:border-slate-350'">
            <div class="flex justify-between items-center text-[10px] font-bold font-mono tracking-wider text-slate-400 uppercase">
              <span class="text-indigo-600">{{ rep.report_type }}</span>
              <span>{{ formatDate(rep.generated_at) }}</span>
            </div>
            <p class="text-xs font-bold text-slate-800 mt-2">Rapport {{ rep.report_type }}</p>
          </div>
        </div>
      </div>
      
      <!-- Right Column: Document Viewer and Comparison -->
      <div class="col-span-2 bg-white border border-slate-200/50 rounded-3xl p-6 shadow-sm flex flex-col h-[600px] overflow-hidden">
        <div v-if="selectedReport" class="flex flex-col h-full space-y-4">
          <div class="flex justify-between items-center border-b border-slate-100 pb-4 shrink-0">
            <div>
              <h2 class="text-lg font-bold text-slate-900">Rapport {{ selectedReport.report_type }}</h2>
              <p class="text-[10px] text-slate-400 font-bold font-mono uppercase mt-1">Généré le {{ formatDate(selectedReport.generated_at) }}</p>
            </div>
            <div class="flex space-x-2.5">
              <Button @click="downloadPDF" class="bg-indigo-600! hover:bg-indigo-550! text-white! text-xs! font-bold! px-4! py-2.5! rounded-xl! shadow-xs! transition! cursor-pointer! border-none!">
                <span>Télécharger PDF</span>
              </Button>
              <Button class="bg-slate-100! hover:bg-slate-200! text-slate-700! text-xs! font-bold! px-4! py-2.5! rounded-xl! border-none! transition! cursor-pointer!" @click="compareMode = !compareMode">
                <span>{{ compareMode ? 'Mode Lecture' : 'Comparer les Versions' }}</span>
              </Button>
            </div>
          </div>
          
          <div class="flex-1 overflow-hidden">
            <!-- Normal Mode -->
            <div v-if="!compareMode" class="h-full overflow-y-auto pr-1">
              <div class="prose prose-sm max-w-none text-slate-600 leading-relaxed font-medium p-2" v-html="selectedReport.content_html"></div>
            </div>
            
            <!-- Compare Mode (Side-by-Side) -->
            <div v-else class="h-full grid grid-cols-2 gap-4 overflow-hidden">
              <!-- Left Column: Selected Version -->
              <div class="border-r border-slate-100 pr-4 flex flex-col h-full overflow-hidden">
                <span class="text-[10px] font-bold text-indigo-600 uppercase tracking-wider mb-2 font-mono">Version Actuelle (A)</span>
                <div class="flex-1 overflow-y-auto pr-1 prose prose-sm max-w-none text-slate-600 leading-relaxed font-medium" v-html="selectedReport.content_html"></div>
              </div>
              
              <!-- Right Column: Comparison Target -->
              <div class="pl-4 flex flex-col h-full overflow-hidden">
                <div class="flex justify-between items-center mb-3 shrink-0">
                  <span class="text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono">Comparer avec (B)</span>
                  <select v-if="otherReportsOfSameType.length > 0" v-model="compareReportId" class="text-xs bg-slate-50 border border-slate-200/80 rounded-xl px-2.5 py-1.5 font-bold text-slate-700 outline-none cursor-pointer">
                    <option v-for="rep in otherReportsOfSameType" :key="rep.id" :value="rep.id">
                      {{ formatDate(rep.generated_at) }}
                    </option>
                  </select>
                  <span v-else class="text-[10px] font-bold text-slate-400 font-mono">Aucune autre version</span>
                </div>
                <div v-if="compareReport" class="flex-1 overflow-y-auto pr-1 prose prose-sm max-w-none text-slate-600 leading-relaxed font-medium" v-html="compareReport.content_html"></div>
                <div v-else class="text-slate-400 font-medium text-center my-auto py-10">Sélectionnez une version pour comparer.</div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="text-slate-400 font-medium text-center my-auto py-20">Sélectionnez un rapport pour afficher son contenu.</div>
      </div>
    </div>
  </div>
</template>

<style>
@reference "tailwindcss";

/* Basic prose styling for markdown content */
.prose {
  h1 { @apply text-xl font-bold mb-4 text-slate-900 border-b border-slate-100 pb-2; }
  h2 { @apply text-base font-bold mb-3 text-slate-800 mt-4; }
  h3 { @apply text-sm font-bold mb-2 text-slate-700; }
  ul { @apply list-disc pl-5 mb-4 space-y-1; }
  ol { @apply list-decimal pl-5 mb-4 space-y-1; }
  li { @apply mb-1; }
  p { @apply mb-3.5; }
  table { @apply w-full border-collapse my-5 rounded-xl overflow-hidden border border-slate-200/60; }
  th, td { @apply border-b border-slate-200/50 p-3 text-left text-xs; }
  th { @apply bg-slate-50 font-bold text-slate-500 uppercase font-mono tracking-wider text-[10px]; }
  td { @apply text-slate-600 font-medium; }
}
</style>
