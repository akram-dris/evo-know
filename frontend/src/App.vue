<script setup>
import { ref, onMounted } from 'vue'
import { 
  LayoutDashboard, 
  TrendingUp, 
  FileText, 
  GitMerge, 
  ShieldAlert, 
  Cpu, 
  History, 
  Bell, 
  Database,
  Sliders,
  LogOut,
  User,
  Sun,
  Moon
} from 'lucide-vue-next'

const notificationsCount = ref(3)
const systemStatus = ref('Online')

// Theme management (White Theme as default)
const isDark = ref(false)

const toggleTheme = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  }
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 dark:bg-slate-950 dark:text-slate-100 flex overflow-hidden transition-colors duration-300">
    <!-- Sidebar Navigation -->
    <aside class="w-64 border-r border-slate-200 dark:border-slate-800 bg-white/70 dark:bg-slate-900/40 backdrop-blur-md flex flex-col p-4 space-y-6 shrink-0 shadow-xs">
      <!-- Logo Header -->
      <div class="flex items-center space-x-3 px-2 py-3">
        <div class="h-9 w-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/30">
          <Cpu class="h-5 w-5 text-white" />
        </div>
        <div>
          <span class="font-bold text-lg tracking-tight bg-gradient-to-r from-slate-900 to-slate-600 dark:from-white dark:to-slate-400 bg-clip-text text-transparent">EvoKnow</span>
          <p class="text-[10px] text-slate-500 dark:text-slate-400 font-mono">v1.0.0-CloudNative</p>
        </div>
      </div>
      
      <!-- Nav Links -->
      <nav class="flex-1 space-y-1">
        <router-link to="/" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/40 dark:hover:text-white transition-all group">
          <LayoutDashboard class="h-5 w-5 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
          <span class="text-sm font-medium">Dashboard</span>
        </router-link>
        <router-link to="/prediction" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/40 dark:hover:text-white transition-all group">
          <TrendingUp class="h-5 w-5 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
          <span class="text-sm font-medium">T1: Prediction</span>
        </router-link>
        <router-link to="/reports" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/40 dark:hover:text-white transition-all group">
          <FileText class="h-5 w-5 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
          <span class="text-sm font-medium">T2: Reports</span>
        </router-link>
        <router-link to="/fusion" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/40 dark:hover:text-white transition-all group">
          <GitMerge class="h-5 w-5 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
          <span class="text-sm font-medium">T3: Fusion</span>
        </router-link>
        <router-link to="/consistency" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/40 dark:hover:text-white transition-all group">
          <ShieldAlert class="h-5 w-5 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
          <span class="text-sm font-medium">T4: Consistency</span>
        </router-link>
        <router-link to="/discovery" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/40 dark:hover:text-white transition-all group">
          <Cpu class="h-5 w-5 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
          <span class="text-sm font-medium">T5: Discovery</span>
        </router-link>
        <router-link to="/knowledge-base" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800/40 dark:hover:text-white transition-all group">
          <Database class="h-5 w-5 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
          <span class="text-sm font-medium">Knowledge Base</span>
        </router-link>
      </nav>

      <!-- Bottom Profile / Meta Actions -->
      <div class="border-t border-slate-200 dark:border-slate-800/60 pt-4 space-y-1">
        <router-link to="/audit" class="flex items-center space-x-3 px-3 py-2 rounded-lg text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors text-xs">
          <History class="h-4 w-4" />
          <span>Audit Ledger (XAI)</span>
        </router-link>
        <router-link to="/settings" class="flex items-center space-x-3 px-3 py-2 rounded-lg text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 transition-colors text-xs">
          <Sliders class="h-4 w-4" />
          <span>System Settings</span>
        </router-link>
        <div class="flex items-center justify-between px-3 py-2 mt-4 bg-slate-100 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-800/60">
          <div class="flex items-center space-x-2">
            <div class="h-7 w-7 rounded-lg bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center border border-indigo-200 dark:border-indigo-800/40">
              <User class="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            </div>
            <div class="truncate w-24">
              <p class="text-xs font-medium text-slate-700 dark:text-slate-200 truncate">Akram Dris</p>
              <p class="text-[9px] text-slate-500 font-mono uppercase">KM Admin</p>
            </div>
          </div>
          <button class="text-slate-500 hover:text-slate-700 dark:hover:text-slate-300">
            <LogOut class="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content Workspace -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Navbar / Top Header -->
      <header class="h-16 border-b border-slate-200 dark:border-slate-800/60 bg-white/80 dark:bg-slate-950/60 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10 transition-colors duration-300">
        <div class="flex items-center space-x-3">
          <h2 class="font-semibold text-lg text-slate-900 dark:text-white">KM Update Hub</h2>
          <div class="flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600 dark:text-emerald-400">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 dark:bg-emerald-400 animate-pulse"></span>
            <span class="text-[10px] font-mono font-medium">{{ systemStatus }}</span>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <!-- Theme Toggle Button -->
          <button @click="toggleTheme" class="p-2 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800/40 transition-all" title="Toggle theme">
            <Sun v-if="isDark" class="h-5 w-5" />
            <Moon v-else class="h-5 w-5" />
          </button>

          <!-- Notification bell -->
          <button class="relative p-2 text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800/40 transition-all">
            <Bell class="h-5 w-5" />
            <span v-if="notificationsCount > 0" class="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full bg-indigo-500"></span>
          </button>
        </div>
      </header>

      <!-- Main Router view wrapper -->
      <main class="flex-1 overflow-y-auto p-6 transition-colors duration-300">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style>
@reference "tailwindcss";

/* Custom Router active classes styling */
.router-link-active {
  @apply bg-indigo-500/10 text-indigo-600 dark:bg-indigo-600/15 dark:text-indigo-400 border-l-2 border-indigo-500 rounded-l-none pl-2.5!;
}
</style>
