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
  CheckCircle2,
  ChevronRight
} from 'lucide-vue-next'

const stats = ref([
  { 
    name: 'T1: Obsolescence Risk', 
    value: '12 Docs', 
    change: '+3 this week', 
    icon: TrendingUp, 
    color: 'text-rose-600 dark:text-rose-400 bg-rose-500/10 dark:bg-rose-500/20 border-rose-200 dark:border-rose-500/30',
    hoverGlow: 'hover:shadow-rose-500/10 hover:border-rose-300 dark:hover:border-rose-500/40'
  },
  { 
    name: 'T2: Auto Reports', 
    value: '38 Reports', 
    change: '5 templates active', 
    icon: FileCheck, 
    color: 'text-blue-600 dark:text-blue-400 bg-blue-500/10 dark:bg-blue-500/20 border-blue-200 dark:border-blue-500/30',
    hoverGlow: 'hover:shadow-blue-500/10 hover:border-blue-300 dark:hover:border-blue-500/40'
  },
  { 
    name: 'T3: Semantic Fusions', 
    value: '87 Merges', 
    change: '-12% redundancy', 
    icon: GitMerge, 
    color: 'text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 dark:bg-emerald-500/20 border-emerald-200 dark:border-emerald-500/30',
    hoverGlow: 'hover:shadow-emerald-500/10 hover:border-emerald-300 dark:hover:border-emerald-500/40'
  },
  { 
    name: 'T4: Consistency Index', 
    value: '96.4%', 
    change: '0 conflicts outstanding', 
    icon: ShieldCheck, 
    color: 'text-indigo-600 dark:text-indigo-400 bg-indigo-500/10 dark:bg-indigo-500/20 border-indigo-200 dark:border-indigo-500/30',
    hoverGlow: 'hover:shadow-indigo-500/10 hover:border-indigo-300 dark:hover:border-indigo-500/40'
  },
  { 
    name: 'T5: Mined Relations', 
    value: '143 Links', 
    change: '+18 GNN predictions', 
    icon: Lightbulb, 
    color: 'text-amber-600 dark:text-amber-400 bg-amber-500/10 dark:bg-amber-500/20 border-amber-200 dark:border-amber-500/30',
    hoverGlow: 'hover:shadow-amber-500/10 hover:border-amber-300 dark:hover:border-amber-500/40'
  },
])

const recentAlerts = ref([
  { id: 1, title: 'Obsolescence Imminent', desc: 'Document "OSS-4G-Procedure-v2" access declined by 82% over 30 days.', time: '12 mins ago', severity: 'high', bgClass: 'bg-rose-500/5 dark:bg-rose-500/10 border-rose-100 dark:border-rose-950/40 border-l-rose-500' },
  { id: 2, title: 'Knowledge Contradiction Detected', desc: 'T4 identified conflict between backup schedules in Doc-A & Doc-B.', time: '1 hr ago', severity: 'medium', bgClass: 'bg-amber-500/5 dark:bg-amber-500/10 border-amber-100 dark:border-amber-950/40 border-l-amber-500' },
])

const recentActivity = ref([
  { id: 1, type: 'Fusion', message: 'T3 semantic cluster consolidated 4 overlapping documents in department "IT Support".', time: '2 hrs ago', badgeColor: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-200/50 dark:border-emerald-800/40' },
  { id: 2, type: 'Report', message: 'T2 compiled weekly execution summary. Saved to centralized reports catalog.', time: '4 hrs ago', badgeColor: 'bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-400 border-blue-200/50 dark:border-blue-800/40' },
  { id: 3, type: 'Discovery', message: 'T5 extracted 8 new Concepts (NER) and linked them in Neo4j Knowledge Graph.', time: '1 day ago', badgeColor: 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border-amber-200/50 dark:border-amber-800/40' },
])
</script>

<template>
  <div class="space-y-6 transition-colors duration-300">
    <!-- Hero Header -->
    <div class="relative overflow-hidden bg-gradient-to-br from-indigo-50/90 via-white to-purple-50/60 dark:from-slate-900/80 dark:via-slate-900 dark:to-indigo-950/30 p-6 md:p-8 rounded-3xl border border-slate-200/80 dark:border-slate-800/60 glass-panel shadow-sm">
      <!-- Decorative Background Blur Blobs -->
      <div class="absolute -right-16 -top-16 w-32 h-32 rounded-full bg-indigo-400/20 blur-2xl pointer-events-none"></div>
      <div class="absolute left-1/3 -bottom-8 w-24 h-24 rounded-full bg-purple-400/10 blur-xl pointer-events-none"></div>
      
      <div class="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-700 dark:text-indigo-400 mb-3 border border-indigo-500/20">
            System Monitoring
          </span>
          <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight">
            <span class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-800 bg-clip-text text-transparent dark:from-white dark:via-slate-200 dark:to-slate-400">
              KM Update Dashboard
            </span>
          </h1>
          <p class="text-slate-600 dark:text-slate-400 text-sm mt-2 max-w-xl leading-relaxed">
            Autonomous orchestration monitoring and explainable AI insights across the enterprise knowledge base.
          </p>
        </div>
        <button class="bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 dark:from-indigo-600 dark:to-purple-600 dark:hover:from-indigo-500 dark:hover:to-purple-500 text-white font-semibold text-sm px-5 py-3 rounded-2xl flex items-center space-x-2.5 shadow-lg shadow-indigo-600/25 hover:shadow-indigo-600/35 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer group">
          <Play class="h-4 w-4 fill-current transition-transform group-hover:scale-110" />
          <span>Run Pipeline Scan</span>
        </button>
      </div>
    </div>

    <!-- Metrics Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div v-for="stat in stats" :key="stat.name" 
           class="p-5 rounded-2xl border border-slate-200/80 dark:border-slate-800/80 bg-white/90 dark:bg-slate-900/30 flex flex-col justify-between space-y-5 hover:-translate-y-1 transition-all duration-300"
           :class="stat.hoverGlow">
        <div class="flex justify-between items-start">
          <span class="text-xs font-semibold text-slate-500 dark:text-slate-400 leading-tight w-2/3">{{ stat.name }}</span>
          <div class="p-2.5 rounded-xl border flex items-center justify-center transition-all duration-300" :class="stat.color">
            <component :is="stat.icon" class="h-4.5 w-4.5" />
          </div>
        </div>
        <div>
          <h3 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">{{ stat.value }}</h3>
          <p class="text-[10px] mt-1 text-slate-500 dark:text-slate-400 font-semibold font-mono flex items-center">
            <ChevronRight class="h-3 w-3 text-slate-400 mr-0.5" />
            <span>{{ stat.change }}</span>
          </p>
        </div>
      </div>
    </div>

    <!-- Alerts and Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Alerts Column -->
      <div class="lg:col-span-1 bg-white/90 dark:bg-slate-900/20 border border-slate-200/80 dark:border-slate-800/60 p-6 rounded-3xl space-y-5 glass-panel shadow-sm">
        <div class="flex justify-between items-center">
          <h2 class="font-bold text-slate-800 dark:text-slate-200 text-sm flex items-center space-x-2">
            <AlertTriangle class="h-4.5 w-4.5 text-rose-500" />
            <span>Active AI Alerts</span>
          </h2>
          <span class="bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 text-[10px] font-mono px-2.5 py-0.5 rounded-full font-bold">2 Warning</span>
        </div>
        
        <div class="space-y-3.5">
          <div v-for="alert in recentAlerts" :key="alert.id" 
               class="p-4 border-l-4 rounded-r-2xl border border-slate-200/50 dark:border-slate-800/60 space-y-2.5 hover:shadow-xs transition-all duration-200 cursor-pointer"
               :class="alert.bgClass">
            <div class="flex justify-between items-start">
              <h4 class="text-xs font-bold text-slate-800 dark:text-slate-200">{{ alert.title }}</h4>
              <span class="text-[9px] text-slate-500 dark:text-slate-400 flex items-center space-x-1 font-mono">
                <Clock class="h-3 w-3" />
                <span>{{ alert.time }}</span>
              </span>
            </div>
            <p class="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed font-medium">{{ alert.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Activity Column -->
      <div class="lg:col-span-2 bg-white/90 dark:bg-slate-900/20 border border-slate-200/80 dark:border-slate-800/60 p-6 rounded-3xl space-y-5 glass-panel shadow-sm">
        <h2 class="font-bold text-slate-800 dark:text-slate-200 text-sm flex items-center space-x-2">
          <CheckCircle2 class="h-4.5 w-4.5 text-indigo-600 dark:text-indigo-400" />
          <span>Recent Execution Logs</span>
        </h2>
        
        <div class="divide-y divide-slate-100 dark:divide-slate-800/40 space-y-3.5">
          <div v-for="act in recentActivity" :key="act.id" class="pt-3.5 first:pt-0 flex items-start space-x-4">
            <span class="text-[10px] font-bold font-mono uppercase px-2.5 py-1 rounded-lg border shrink-0" :class="act.badgeColor">
              {{ act.type }}
            </span>
            <div class="flex-1 space-y-1">
              <p class="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-medium">{{ act.message }}</p>
              <p class="text-[9px] text-slate-500 dark:text-slate-400 font-mono">{{ act.time }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

