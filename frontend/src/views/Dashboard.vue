<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
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

const stats = ref([])
const recentAlerts = ref([])
const recentActivity = ref([])
const loading = ref(true)

const fetchDashboardData = async () => {
  try {
    const res = await axios.get('/api/v1/dashboard/stats')
    stats.value = res.data.stats.map((item, idx) => {
      const icons = [TrendingUp, FileCheck, GitMerge, ShieldCheck, Lightbulb]
      const colors = [
        'text-rose-600 bg-rose-500/10 border-rose-200',
        'text-blue-600 bg-blue-500/10 border-blue-200',
        'text-emerald-600 bg-emerald-500/10 border-emerald-200',
        'text-indigo-600 bg-indigo-500/10 border-indigo-200',
        'text-amber-600 bg-amber-500/10 border-amber-200'
      ]
      const glows = [
        'hover:shadow-rose-500/10 hover:border-rose-300',
        'hover:shadow-blue-500/10 hover:border-blue-300',
        'hover:shadow-emerald-500/10 hover:border-emerald-300',
        'hover:shadow-indigo-500/10 hover:border-indigo-300',
        'hover:shadow-amber-500/10 hover:border-amber-300'
      ]
      return {
        ...item,
        icon: icons[idx],
        color: colors[idx],
        hoverGlow: glows[idx]
      }
    })
    recentAlerts.value = res.data.recentAlerts
    recentActivity.value = res.data.recentActivity
  } catch (err) {
    console.error("Error fetching dashboard data:", err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<template>
  <div class="space-y-6 transition-colors duration-300">
    <!-- Hero Header -->
    <div class="relative overflow-hidden bg-gradient-to-br from-indigo-50/90 via-white to-purple-50/60 p-6 md:p-8 rounded-3xl border border-slate-200/80 glass-panel shadow-sm">
      <!-- Decorative Background Blur Blobs -->
      <div class="absolute -right-16 -top-16 w-32 h-32 rounded-full bg-indigo-400/20 blur-2xl pointer-events-none"></div>
      <div class="absolute left-1/3 -bottom-8 w-24 h-24 rounded-full bg-purple-400/10 blur-xl pointer-events-none"></div>
      
      <div class="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-700 mb-3 border border-indigo-500/20">
            Surveillance du système
          </span>
          <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight">
            <span class="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-800 bg-clip-text text-transparent">
              Tableau de bord de mise à jour
            </span>
          </h1>
          <p class="text-slate-600 text-sm mt-2 max-w-xl leading-relaxed">
            Surveillance de l'orchestration autonome et analyses d'IA explicables sur la base de connaissances de l'entreprise.
          </p>
        </div>
        <button class="bg-gradient-to-r from-indigo-600 to-indigo-700 hover:from-indigo-500 hover:to-indigo-600 text-white font-semibold text-sm px-5 py-3 rounded-2xl flex items-center space-x-2.5 shadow-lg shadow-indigo-600/25 hover:shadow-indigo-600/35 hover:-translate-y-0.5 transition-all duration-200 cursor-pointer group">
          <Play class="h-4 w-4 fill-current transition-transform group-hover:scale-110" />
          <span>Lancer le scan du pipeline</span>
        </button>
      </div>
    </div>

    <!-- Metrics Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      <div v-for="stat in stats" :key="stat.name" 
           class="p-5 rounded-2xl border border-slate-200/80 bg-white/90 flex flex-col justify-between space-y-5 hover:-translate-y-1 transition-all duration-300"
           :class="stat.hoverGlow">
        <div class="flex justify-between items-start">
          <span class="text-xs font-semibold text-slate-500 leading-tight w-2/3">{{ stat.name }}</span>
          <div class="p-2.5 rounded-xl border flex items-center justify-center transition-all duration-300" :class="stat.color">
            <component :is="stat.icon" class="h-4.5 w-4.5" />
          </div>
        </div>
        <div>
          <h3 class="text-2xl font-bold tracking-tight text-slate-900">{{ stat.value }}</h3>
          <p class="text-[10px] mt-1 text-slate-500 font-semibold font-mono flex items-center">
            <ChevronRight class="h-3 w-3 text-slate-400 mr-0.5" />
            <span>{{ stat.change }}</span>
          </p>
        </div>
      </div>
    </div>

    <!-- Alerts and Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Alerts Column -->
      <div class="lg:col-span-1 bg-white/90 border border-slate-200/80 p-6 rounded-3xl space-y-5 glass-panel shadow-sm">
        <div class="flex justify-between items-center">
          <h2 class="font-bold text-slate-800 text-sm flex items-center space-x-2">
            <AlertTriangle class="h-4.5 w-4.5 text-rose-500" />
            <span>Alertes d'IA actives</span>
          </h2>
          <span class="bg-rose-500/10 border border-rose-500/20 text-rose-600 text-[10px] font-mono px-2.5 py-0.5 rounded-full font-bold">2 Avertissements</span>
        </div>
        
        <div class="space-y-3.5">
          <div v-for="alert in recentAlerts" :key="alert.id" 
               class="p-4 border-l-4 rounded-r-2xl border border-slate-200/50 space-y-2.5 hover:shadow-xs transition-all duration-200 cursor-pointer"
               :class="alert.bgClass">
            <div class="flex justify-between items-start">
              <h4 class="text-xs font-bold text-slate-800">{{ alert.title }}</h4>
              <span class="text-[9px] text-slate-500 flex items-center space-x-1 font-mono">
                <Clock class="h-3 w-3" />
                <span>{{ alert.time }}</span>
              </span>
            </div>
            <p class="text-[11px] text-slate-600 leading-relaxed font-medium">{{ alert.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Activity Column -->
      <div class="lg:col-span-2 bg-white/90 border border-slate-200/80 p-6 rounded-3xl space-y-5 glass-panel shadow-sm">
        <h2 class="font-bold text-slate-800 text-sm flex items-center space-x-2">
          <CheckCircle2 class="h-4.5 w-4.5 text-indigo-600" />
          <span>Journaux d'exécution récents</span>
        </h2>
        
        <div class="divide-y divide-slate-100 space-y-3.5">
          <div v-for="act in recentActivity" :key="act.id" class="pt-3.5 first:pt-0 flex items-start space-x-4">
            <span class="text-[10px] font-bold font-mono uppercase px-2.5 py-1 rounded-lg border shrink-0" :class="act.badgeColor">
              {{ act.type }}
            </span>
            <div class="flex-1 space-y-1">
              <p class="text-xs text-slate-700 leading-relaxed font-medium">{{ act.message }}</p>
              <p class="text-[9px] text-slate-500 font-mono">{{ act.time }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

