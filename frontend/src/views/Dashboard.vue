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
  ChevronRight,
  RefreshCw
} from 'lucide-vue-next'
import Button from 'primevue/button'
import { useToast } from 'primevue/usetoast'

const stats = ref([])
const recentAlerts = ref([])
const recentActivity = ref([])
const loading = ref(true)
const scanning = ref(false)
const toast = useToast()

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

const triggerScan = async () => {
  scanning.value = true
  try {
    await axios.post('/api/v1/dashboard/scan')
    toast.add({ severity: 'success', summary: 'Scan Démarré', detail: 'Le scan du pipeline de connaissances a été lancé avec succès.', life: 4000 })
    await fetchDashboardData()
  } catch (err) {
    console.error("Error triggering pipeline scan:", err)
    toast.add({ severity: 'error', summary: 'Erreur', detail: 'Échec du lancement du scan du pipeline.', life: 4000 })
  } finally {
    scanning.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<template>
  <div class="space-y-8 transition-colors duration-300">
    <!-- Hero Header -->
    <div class="relative overflow-hidden bg-gradient-to-br from-indigo-50/70 via-white to-violet-50/40 p-6 md:p-8 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.02)] backdrop-blur-xl">
      <!-- Decorative Background Blur Blobs -->
      <div class="absolute -right-16 -top-16 w-36 h-36 rounded-full bg-gradient-to-tr from-indigo-400/10 to-violet-400/10 blur-2xl pointer-events-none"></div>
      <div class="absolute left-1/3 -bottom-8 w-28 h-28 rounded-full bg-pink-400/5 blur-xl pointer-events-none"></div>
      
      <div class="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
        <div>
          <span class="inline-flex items-center px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-50 text-indigo-700 mb-3.5 border border-indigo-200/20 font-mono">
            Surveillance Active
          </span>
          <h1 class="text-2xl md:text-3xl font-extrabold tracking-tight text-slate-900 leading-none">
            Tableau de bord de mise à jour
          </h1>
          <p class="text-slate-500 text-sm mt-3.5 max-w-2xl leading-relaxed font-medium">
            Surveillance de l'orchestration autonome et analyses d'IA explicables sur la base de connaissances de l'entreprise.
          </p>
        </div>
        <Button 
          @click="triggerScan" 
          :disabled="scanning" 
          class="bg-indigo-600! hover:bg-indigo-550! text-white! font-bold! text-xs! px-5.5! py-3.5! rounded-2xl! shadow-lg! shadow-indigo-600/15! hover:shadow-indigo-600/25! hover:-translate-y-0.5! transition-all! duration-200! cursor-pointer! border-none! flex! items-center! shrink-0! group! disabled:opacity-50"
        >
          <RefreshCw v-if="scanning" class="h-4 w-4 animate-spin mr-2" />
          <Play v-else class="h-4 w-4 fill-current transition-transform group-hover:scale-110 mr-2 inline-block" />
          <span>{{ scanning ? 'Scan en cours...' : 'Lancer le scan du pipeline' }}</span>
        </Button>
      </div>
    </div>

    <!-- Metrics Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
      <div v-for="stat in stats" :key="stat.name" 
           class="p-5.5 rounded-2xl premium-card flex flex-col justify-between space-y-6">
        <div class="flex justify-between items-start">
          <span class="text-xs font-bold text-slate-500 leading-tight w-2/3 tracking-tight">{{ stat.name }}</span>
          <div class="p-2.5 rounded-xl border flex items-center justify-center transition-all duration-300" :class="stat.color">
            <component :is="stat.icon" class="h-4.5 w-4.5" />
          </div>
        </div>
        <div>
          <h3 class="text-2xl font-extrabold tracking-tight text-slate-900 leading-none">{{ stat.value }}</h3>
          <p class="text-[9px] mt-2 text-slate-400 font-bold font-mono uppercase tracking-wider flex items-center">
            <ChevronRight class="h-3 w-3 text-slate-400 mr-0.5" />
            <span>{{ stat.change }}</span>
          </p>
        </div>
      </div>
    </div>

    <!-- Alerts and Activity -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Alerts Column -->
      <div class="lg:col-span-1 bg-white/70 border border-slate-200/50 p-6 rounded-3xl space-y-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] backdrop-blur-xl">
        <div class="flex justify-between items-center pb-2 border-b border-slate-100">
          <h2 class="font-bold text-slate-800 text-sm flex items-center space-x-2">
            <AlertTriangle class="h-4.5 w-4.5 text-rose-500" />
            <span>Alertes d'IA actives</span>
          </h2>
          <span class="bg-rose-50 border border-rose-200 text-rose-700 text-[9px] font-mono px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider">{{ recentAlerts.length }} Alerte{{ recentAlerts.length !== 1 ? 's' : '' }}</span>
        </div>
        
        <div class="space-y-4">
          <div v-for="alert in recentAlerts" :key="alert.id" 
               class="p-4 border-l-4 rounded-2xl border bg-slate-50/50 border-slate-100 space-y-2.5 hover:shadow-xs transition-all duration-200 cursor-pointer"
               :class="alert.bgClass">
            <div class="flex justify-between items-start">
              <h4 class="text-xs font-bold text-slate-800 tracking-tight">{{ alert.title }}</h4>
              <span class="text-[9px] text-slate-400 flex items-center space-x-1 font-mono font-bold">
                <Clock class="h-3 w-3" />
                <span>{{ alert.time }}</span>
              </span>
            </div>
            <p class="text-[11px] text-slate-500 leading-relaxed font-semibold">{{ alert.desc }}</p>
          </div>
        </div>
      </div>

      <!-- Activity Column -->
      <div class="lg:col-span-2 bg-white/70 border border-slate-200/50 p-6 rounded-3xl space-y-5 shadow-[0_8px_30px_rgba(0,0,0,0.015)] backdrop-blur-xl">
        <div class="flex justify-between items-center pb-2 border-b border-slate-100">
          <h2 class="font-bold text-slate-800 text-sm flex items-center space-x-2">
            <CheckCircle2 class="h-4.5 w-4.5 text-indigo-650" />
            <span>Journaux d'exécution récents</span>
          </h2>
        </div>
        
        <div class="divide-y divide-slate-100/80 space-y-4 max-h-[350px] overflow-y-auto pr-1">
          <div v-for="act in recentActivity" :key="act.id" class="pt-4 first:pt-0 flex items-start space-x-4">
            <span class="text-[9px] font-extrabold font-mono uppercase tracking-wider px-2.5 py-1 rounded-lg border shrink-0" :class="act.badgeColor">
              {{ act.type }}
            </span>
            <div class="flex-1 space-y-1">
              <p class="text-xs text-slate-700 leading-relaxed font-semibold">{{ act.message }}</p>
              <p class="text-[9px] text-slate-400 font-mono font-bold">{{ act.time }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

