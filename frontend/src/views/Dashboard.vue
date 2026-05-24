<script setup>
import { ref } from 'vue'
import { 
  TrendingUp, 
  FileCheck, 
  GitMerge, 
  ShieldCheck, 
  Lightbulb, 
  AlertTriangle,
  Play,
  Clock,
  CheckCircle2
} from 'lucide-vue-next'

const stats = ref([
  { name: 'T1: Obsolescence Risk', value: '12 Docs', change: '+3 this week', changeType: 'increase', icon: TrendingUp, color: 'text-rose-400 bg-rose-500/10 border-rose-500/20' },
  { name: 'T2: Auto Reports', value: '38 Reports', change: '5 templates active', changeType: 'neutral', icon: FileCheck, color: 'text-blue-400 bg-blue-500/10 border-blue-500/20' },
  { name: 'T3: Semantic Fusions', value: '87 Merges', change: '-12% data redundancy', changeType: 'decrease', icon: GitMerge, color: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20' },
  { name: 'T4: Consistency Index', value: '96.4%', change: '0 conflicts outstanding', changeType: 'neutral', icon: ShieldCheck, color: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20' },
  { name: 'T5: Mined Relations', value: '143 Links', change: '+18 GNN predictions', changeType: 'increase', icon: Lightbulb, color: 'text-amber-400 bg-amber-500/10 border-amber-500/20' },
])

const recentAlerts = ref([
  { id: 1, title: 'Obsolescence Imminent', desc: 'Document "OSS-4G-Procedure-v2" access declined by 82% over 30 days.', time: '12 mins ago', severity: 'high' },
  { id: 2, title: 'Knowledge Contradiction Detected', desc: 'T4 identified conflict between backup schedules in Doc-A & Doc-B.', time: '1 hr ago', severity: 'medium' },
])

const recentActivity = ref([
  { id: 1, type: 'Fusion', message: 'T3 semantic cluster consolidated 4 overlapping documents in department "IT Support".', time: '2 hrs ago' },
  { id: 2, type: 'Report', message: 'T2 compiled weekly execution summary. Saved to centralized reports catalog.', time: '4 hrs ago' },
  { id: 3, type: 'Discovery', message: 'T5 extracted 8 new Concepts (NER) and linked them in Neo4j Knowledge Graph.', time: '1 day ago' },
])
</script>

<template>
  <div class="space-y-6">
    <!-- Hero Header -->
    <div class="flex justify-between items-center bg-gradient-to-r from-slate-900 to-indigo-950/20 p-6 rounded-2xl border border-slate-800/60 glass-panel">
      <div>
        <h1 class="text-2xl font-bold text-white">KM Update Dashboard</h1>
        <p class="text-slate-400 text-sm mt-1">Autonomous orchestration monitoring and explainable AI insights.</p>
      </div>
      <button class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm px-4 py-2.5 rounded-xl flex items-center space-x-2 shadow-lg shadow-indigo-600/20 transition-all">
        <Play class="h-4 w-4 fill-current" />
        <span>Run Pipeline Scan</span>
      </button>
    </div>

    <!-- Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
      <div v-for="stat in stats" :key="stat.name" class="p-4 rounded-xl border border-slate-800/80 bg-slate-900/30 flex flex-col justify-between space-y-4 hover:border-slate-700/80 transition-all">
        <div class="flex justify-between items-start">
          <span class="text-xs font-medium text-slate-400 leading-tight w-2/3">{{ stat.name }}</span>
          <div class="p-2 rounded-lg border" :class="stat.color">
            <component :is="stat.icon" class="h-4 w-4" />
          </div>
        </div>
        <div>
          <h3 class="text-xl font-bold text-white">{{ stat.value }}</h3>
          <p class="text-[10px] mt-0.5 text-slate-500 font-medium">{{ stat.change }}</p>
        </div>
      </div>
    </div>

    <!-- Alerts and Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Alerts Column -->
      <div class="lg:col-span-1 bg-slate-900/20 border border-slate-800/60 p-5 rounded-2xl space-y-4 glass-panel">
        <div class="flex justify-between items-center">
          <h2 class="font-semibold text-slate-200 text-sm flex items-center space-x-2">
            <AlertTriangle class="h-4 w-4 text-rose-500" />
            <span>Active AI Alerts</span>
          </h2>
          <span class="bg-rose-500/10 border border-rose-500/20 text-rose-400 text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold">2 Warning</span>
        </div>
        
        <div class="space-y-3">
          <div v-for="alert in recentAlerts" :key="alert.id" 
               class="p-4 border-l-4 rounded-r-xl bg-slate-950/40 border-slate-800 space-y-2 hover:bg-slate-950/80 transition-colors"
               :class="alert.severity === 'high' ? 'border-l-rose-500' : 'border-l-amber-500'">
            <div class="flex justify-between items-start">
              <h4 class="text-xs font-semibold text-slate-200">{{ alert.title }}</h4>
              <span class="text-[9px] text-slate-500 flex items-center space-x-1">
                <Clock class="h-3 w-3" />
                <span>{{ alert.time }}</span>
              </span>
            </div>
            <p class="text-[11px] text-slate-400 leading-normal">{{ alert.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Activity Column -->
      <div class="lg:col-span-2 bg-slate-900/20 border border-slate-800/60 p-5 rounded-2xl space-y-4 glass-panel">
        <h2 class="font-semibold text-slate-200 text-sm flex items-center space-x-2">
          <CheckCircle2 class="h-4 w-4 text-indigo-400" />
          <span>Recent Execution Logs</span>
        </h2>
        
        <div class="divide-y divide-slate-800/40 space-y-3">
          <div v-for="act in recentActivity" :key="act.id" class="pt-3 first:pt-0 flex items-start space-x-4">
            <span class="bg-indigo-950 text-indigo-400 text-[9px] font-mono uppercase px-2 py-1 rounded border border-indigo-900/40 mt-0.5">
              {{ act.type }}
            </span>
            <div class="flex-1 space-y-1">
              <p class="text-xs text-slate-300 leading-relaxed">{{ act.message }}</p>
              <p class="text-[9px] text-slate-500 font-mono">{{ act.time }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
