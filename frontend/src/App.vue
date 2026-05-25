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
  User
} from 'lucide-vue-next'

const notificationsCount = ref(3)
const systemStatus = ref('Online')

onMounted(() => {
  // Ensure the document does not have the dark class
  document.documentElement.classList.remove('dark')
  localStorage.removeItem('theme')
})
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 flex overflow-hidden relative">
    <!-- Glowing background blobs for a beautiful, organic glassmorphic gradient glow -->
    <div class="fixed -top-40 -left-40 w-[600px] h-[600px] rounded-full bg-indigo-400/15 blur-[130px] pointer-events-none"></div>
    <div class="fixed -bottom-40 -right-40 w-[600px] h-[600px] rounded-full bg-purple-400/15 blur-[130px] pointer-events-none"></div>
    <div class="fixed top-1/3 right-1/4 w-[400px] h-[400px] rounded-full bg-pink-400/8 blur-[110px] pointer-events-none"></div>

    <!-- Sidebar Navigation -->
    <aside class="w-64 border-r border-slate-200/80 bg-white/75 backdrop-blur-xl flex flex-col p-4 space-y-6 shrink-0 shadow-xs z-10">
      <!-- Logo Header -->
      <div class="flex items-center space-x-3 px-2 py-3">
        <div class="h-9 w-9 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-600/30">
          <Cpu class="h-5 w-5 text-white" />
        </div>
        <div>
          <span class="font-bold text-lg tracking-tight bg-gradient-to-r from-slate-900 to-slate-600 bg-clip-text text-transparent">EvoKnow</span>
          <p class="text-[10px] text-slate-500 font-mono">v1.0.0-CloudNative</p>
        </div>
      </div>
      
      <!-- Nav Links -->
      <nav class="flex-1 space-y-1">
        <router-link to="/" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all group">
          <LayoutDashboard class="h-5 w-5 group-hover:text-indigo-600 transition-colors" />
          <span class="text-sm font-medium">Dashboard</span>
        </router-link>
        <router-link to="/prediction" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all group">
          <TrendingUp class="h-5 w-5 group-hover:text-indigo-600 transition-colors" />
          <span class="text-sm font-medium">T1: Prediction</span>
        </router-link>
        <router-link to="/reports" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all group">
          <FileText class="h-5 w-5 group-hover:text-indigo-600 transition-colors" />
          <span class="text-sm font-medium">T2: Reports</span>
        </router-link>
        <router-link to="/fusion" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all group">
          <GitMerge class="h-5 w-5 group-hover:text-indigo-600 transition-colors" />
          <span class="text-sm font-medium">T3: Fusion</span>
        </router-link>
        <router-link to="/consistency" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all group">
          <ShieldAlert class="h-5 w-5 group-hover:text-indigo-600 transition-colors" />
          <span class="text-sm font-medium">T4: Consistency</span>
        </router-link>
        <router-link to="/discovery" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all group">
          <Cpu class="h-5 w-5 group-hover:text-indigo-600 transition-colors" />
          <span class="text-sm font-medium">T5: Discovery</span>
        </router-link>
        <router-link to="/knowledge-base" class="flex items-center space-x-3 px-3 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-all group">
          <Database class="h-5 w-5 group-hover:text-indigo-600 transition-colors" />
          <span class="text-sm font-medium">Knowledge Base</span>
        </router-link>
      </nav>

      <!-- Bottom Profile / Meta Actions -->
      <div class="border-t border-slate-200 pt-4 space-y-1">
        <router-link to="/audit" class="flex items-center space-x-3 px-3 py-2 rounded-lg text-slate-500 hover:text-slate-800 transition-colors text-xs">
          <History class="h-4 w-4" />
          <span>Audit Ledger (XAI)</span>
        </router-link>
        <router-link to="/settings" class="flex items-center space-x-3 px-3 py-2 rounded-lg text-slate-500 hover:text-slate-800 transition-colors text-xs">
          <Sliders class="h-4 w-4" />
          <span>System Settings</span>
        </router-link>
        <div class="flex items-center justify-between px-3 py-2 mt-4 bg-slate-100 rounded-xl border border-slate-200">
          <div class="flex items-center space-x-2">
            <div class="h-7 w-7 rounded-lg bg-indigo-100 flex items-center justify-center border border-indigo-200">
              <User class="h-4 w-4 text-indigo-600" />
            </div>
            <div class="truncate w-24">
              <p class="text-xs font-medium text-slate-700 truncate">Akram Dris</p>
              <p class="text-[9px] text-slate-500 font-mono uppercase">KM Admin</p>
            </div>
          </div>
          <button class="text-slate-500 hover:text-slate-700">
            <LogOut class="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content Workspace -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Navbar / Top Header -->
      <header class="h-16 border-b border-slate-200 bg-white/80 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10">
        <div class="flex items-center space-x-3">
          <h2 class="font-semibold text-lg text-slate-900">KM Update Hub</h2>
          <div class="flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="text-[10px] font-mono font-medium">{{ systemStatus }}</span>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <!-- Notification bell -->
          <button class="relative p-2 text-slate-600 hover:text-slate-900 rounded-lg hover:bg-slate-100 transition-all">
            <Bell class="h-5 w-5" />
            <span v-if="notificationsCount > 0" class="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full bg-indigo-500"></span>
          </button>
        </div>
      </header>

      <!-- Main Router view wrapper -->
      <main class="flex-1 overflow-y-auto p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style>
@reference "tailwindcss";

/* Custom Router active classes styling */
.router-link-active {
  @apply bg-gradient-to-r from-indigo-500/10 to-indigo-500/[0.02] text-indigo-600 border-l-4 border-indigo-500 rounded-r-xl pl-3!;
}
</style>
