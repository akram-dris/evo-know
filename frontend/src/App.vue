<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
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
  ChevronLeft,
  ChevronRight,
  Users
} from 'lucide-vue-next'
import AlertCard from './components/widgets/AlertCard.vue'

import Toast from 'primevue/toast'


const route = useRoute()
const router = useRouter()
const user = ref(null)
const role = ref('')
const alerts = ref([])
let eventSource = null;

// Collapsible Sidebar state
const isCollapsed = ref(localStorage.getItem('sidebar_collapsed') === 'true')
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  localStorage.setItem('sidebar_collapsed', isCollapsed.value ? 'true' : 'false')
}

// Profile Modal State
const showProfileModal = ref(false)
const profileEmail = ref('')
const profilePassword = ref('')
const profileError = ref('')
const profileSuccess = ref('')
const updatingProfile = ref(false)

const openProfileModal = () => {
  profileEmail.value = user.value?.email || ''
  profilePassword.value = ''
  profileError.value = ''
  profileSuccess.value = ''
  showProfileModal.value = true
}

const handleUpdateProfile = async () => {
  updatingProfile.value = true
  profileError.value = ''
  profileSuccess.value = ''
  try {
    const res = await axios.put('/api/v1/auth/profile', {
      email: profileEmail.value,
      password: profilePassword.value || null
    }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    
    // Update local user details
    const updatedUser = { ...user.value, email: profileEmail.value }
    localStorage.setItem('user', JSON.stringify(updatedUser))
    user.value = updatedUser
    
    profileSuccess.value = 'Profil mis à jour avec succès !'
    setTimeout(() => {
      showProfileModal.value = false
    }, 1500)
  } catch (err) {
    console.error('Error updating profile:', err)
    profileError.value = err.response?.data?.detail || 'Erreur de mise à jour.'
  } finally {
    updatingProfile.value = false
  }
}

onMounted(() => {
  // Ensure the document does not have the dark class
  document.documentElement.classList.remove('dark')
  localStorage.removeItem('theme')

  // Load user profile
  const savedUser = localStorage.getItem('user')
  if (savedUser) {
    user.value = JSON.parse(savedUser)
  }
  role.value = localStorage.getItem('role') || ''

  // Establish SSE connection for alerts
  eventSource = new EventSource(`/api/v1/alerts/stream`);
  
  eventSource.onmessage = (event) => {
    const newAlert = JSON.parse(event.data);
    alerts.value.unshift(newAlert); // Add new alert to the beginning
    // Optionally, limit the number of displayed alerts
    if (alerts.value.length > 5) {
      alerts.value.pop();
    }
  };

  eventSource.onerror = (error) => {
    console.error("EventSource failed:", error);
    eventSource.close();
  };
})

onUnmounted(() => {
  if (eventSource) {
    eventSource.close();
  }
})

const resolveAlert = (id, action) => {
  console.log(`Alert ${id} resolved with action: ${action}`);
  alerts.value = alerts.value.filter(alert => alert.id !== id);
  // In a real app, you would send this to the backend
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  localStorage.removeItem('role')
  window.location.href = '/login'
}
</script>

<template>
  <Toast />
  <router-view v-if="route.name === 'Login'" />
  <div v-else class="h-screen overflow-hidden bg-slate-50 text-slate-800 flex relative w-full">
    <!-- Glowing background blobs for a beautiful, organic glassmorphic gradient glow -->
    <div class="fixed -top-40 -left-40 w-[600px] h-[600px] rounded-full bg-indigo-400/10 blur-[130px] pointer-events-none"></div>
    <div class="fixed -bottom-40 -right-40 w-[600px] h-[600px] rounded-full bg-purple-400/10 blur-[130px] pointer-events-none"></div>
    <div class="fixed top-1/3 right-1/4 w-[400px] h-[400px] rounded-full bg-indigo-500/5 blur-[120px] pointer-events-none"></div>

    <!-- Sidebar Navigation -->
    <aside :class="[isCollapsed ? 'w-20 px-3 py-5' : 'w-68 p-5', 'border-r border-slate-200/60 bg-white/80 backdrop-blur-2xl flex flex-col space-y-6 shrink-0 shadow-[4px_0_24px_rgba(99,102,241,0.02)] z-10 transition-all duration-300 ease-in-out h-full overflow-hidden']">
      <!-- Logo Header -->
      <div class="flex justify-between" :class="isCollapsed ? 'flex-col items-center space-y-4 px-0' : 'flex-row items-center px-1 py-1'">
        <div class="flex items-center min-w-0" :class="isCollapsed ? 'justify-center' : 'space-x-3'">
          <div class="h-10 w-10 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 shrink-0">
            <Cpu class="h-5.5 w-5.5 text-white" />
          </div>
          <div v-show="!isCollapsed" class="transition-all duration-300 overflow-hidden whitespace-nowrap">
            <span class="font-extrabold text-xl tracking-tight bg-gradient-to-r from-slate-900 to-indigo-950 bg-clip-text text-transparent">EvoKnow</span>
            <p class="text-[9px] text-indigo-500 font-mono font-bold uppercase tracking-wider">KM Core Pipeline</p>
          </div>
        </div>
        <button @click="toggleSidebar" class="p-1.5 rounded-xl hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition-colors cursor-pointer shrink-0" :class="isCollapsed ? 'mx-auto' : 'ml-1'" :title="isCollapsed ? 'Développer la barre' : 'Réduire la barre'">
          <ChevronRight v-if="isCollapsed" class="h-4 w-4" />
          <ChevronLeft v-else class="h-4 w-4" />
        </button>
      </div>
      
      <!-- Nav Links -->
      <nav class="flex-1 space-y-1.5 overflow-y-auto pr-1">
        <template v-if="role !== 'Reader'">
          <div v-show="!isCollapsed" class="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-3 mb-2 font-mono">Vue d'ensemble</div>
          
          <router-link to="/" class="flex items-center rounded-xl text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition-all duration-200 group" :class="isCollapsed ? 'justify-center p-2.5 space-x-0' : 'px-3 py-2.5 space-x-3'" title="Tableau de bord">
            <LayoutDashboard class="h-4.5 w-4.5 group-hover:text-indigo-600 transition-colors" />
            <span v-show="!isCollapsed" class="text-sm font-semibold">Tableau de bord</span>
          </router-link>

          <div v-show="!isCollapsed" class="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-3 my-3 font-mono">Pipelines de Connaissances</div>
          
          <router-link to="/prediction" class="flex items-center rounded-xl text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition-all duration-200 group" :class="isCollapsed ? 'justify-center p-2.5 space-x-0' : 'px-3 py-2.5 space-x-3'" title="T1 : Prédiction">
            <TrendingUp class="h-4.5 w-4.5 group-hover:text-indigo-600 transition-colors" />
            <span v-show="!isCollapsed" class="text-sm font-semibold">T1 : Prédiction</span>
          </router-link>
          <router-link to="/reports" class="flex items-center rounded-xl text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition-all duration-200 group" :class="isCollapsed ? 'justify-center p-2.5 space-x-0' : 'px-3 py-2.5 space-x-3'" title="T2 : Rapports">
            <FileText class="h-4.5 w-4.5 group-hover:text-indigo-600 transition-colors" />
            <span v-show="!isCollapsed" class="text-sm font-semibold">T2 : Rapports</span>
          </router-link>
          <router-link to="/fusion" class="flex items-center rounded-xl text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition-all duration-200 group" :class="isCollapsed ? 'justify-center p-2.5 space-x-0' : 'px-3 py-2.5 space-x-3'" title="T3 : Fusion">
            <GitMerge class="h-4.5 w-4.5 group-hover:text-indigo-600 transition-colors" />
            <span v-show="!isCollapsed" class="text-sm font-semibold">T3 : Fusion</span>
          </router-link>
          <router-link to="/consistency" class="flex items-center rounded-xl text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition-all duration-200 group" :class="isCollapsed ? 'justify-center p-2.5 space-x-0' : 'px-3 py-2.5 space-x-3'" title="T4 : Cohérence">
            <ShieldAlert class="h-4.5 w-4.5 group-hover:text-indigo-600 transition-colors" />
            <span v-show="!isCollapsed" class="text-sm font-semibold">T4 : Cohérence</span>
          </router-link>
          <router-link to="/discovery" class="flex items-center rounded-xl text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition-all duration-200 group" :class="isCollapsed ? 'justify-center p-2.5 space-x-0' : 'px-3 py-2.5 space-x-3'" title="T5 : Découverte">
            <Cpu class="h-4.5 w-4.5 group-hover:text-indigo-600 transition-colors" />
            <span v-show="!isCollapsed" class="text-sm font-semibold">T5 : Découverte</span>
          </router-link>
        </template>
        
        <div v-show="!isCollapsed" class="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-3 my-3 font-mono">Base de connaissances</div>
        <router-link to="/knowledge-base" class="flex items-center rounded-xl text-slate-600 hover:bg-slate-100/80 hover:text-slate-900 transition-all duration-200 group" :class="isCollapsed ? 'justify-center p-2.5 space-x-0' : 'px-3 py-2.5 space-x-3'" title="Base de connaissances">
          <Database class="h-4.5 w-4.5 group-hover:text-indigo-600 transition-colors" />
          <span v-show="!isCollapsed" class="text-sm font-semibold">Base de connaissances</span>
        </router-link>
      </nav>

      <!-- Bottom Profile / Meta Actions -->
      <div class="border-t border-slate-200/60 pt-4 space-y-1">
        <template v-if="role !== 'Reader'">
          <router-link to="/audit" class="flex items-center rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-50 transition-all text-xs font-semibold" :class="isCollapsed ? 'justify-center p-2 space-x-0' : 'px-3 py-2 space-x-3'" title="Registre d'audit (XAI)">
            <History class="h-4 w-4 text-slate-400" />
            <span v-show="!isCollapsed">Registre d'audit (XAI)</span>
          </router-link>
          <router-link to="/settings" class="flex items-center rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-50 transition-all text-xs font-semibold" :class="isCollapsed ? 'justify-center p-2 space-x-0' : 'px-3 py-2 space-x-3'" title="Configuration">
            <Sliders class="h-4 w-4 text-slate-400" />
            <span v-show="!isCollapsed">Configuration</span>
          </router-link>
        </template>
        <template v-if="role === 'Admin'">
          <router-link to="/users" class="flex items-center rounded-xl text-slate-500 hover:text-slate-800 hover:bg-slate-50 transition-all text-xs font-semibold" :class="isCollapsed ? 'justify-center p-2 space-x-0' : 'px-3 py-2 space-x-3'" title="Gestion des Comptes">
            <Users class="h-4 w-4 text-slate-400" />
            <span v-show="!isCollapsed">Gestion des Comptes</span>
          </router-link>
        </template>
        <div @click="openProfileModal" class="flex items-center justify-between mt-4 bg-slate-50 border border-slate-200/50 rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.02)] transition-all duration-300 cursor-pointer hover:bg-slate-100/60" :class="isCollapsed ? 'p-2 flex-col space-y-3' : 'px-3 py-2.5'">
          <div class="flex items-center min-w-0" :class="isCollapsed ? 'flex-col space-y-1' : 'space-x-3'">
            <div class="h-8.5 w-8.5 rounded-xl bg-gradient-to-br from-indigo-100 to-violet-100 flex items-center justify-center border border-indigo-200/40 shrink-0">
              <User class="h-4.5 w-4.5 text-indigo-600" />
            </div>
            <div v-show="!isCollapsed" class="truncate w-24 transition-all duration-300">
              <p class="text-xs font-bold text-slate-800 truncate capitalize">{{ user ? user.username : 'admin' }}</p>
              <span class="inline-flex items-center px-1.5 py-0.5 rounded-md text-[8px] font-bold font-mono tracking-wider uppercase bg-indigo-50 text-indigo-700 border border-indigo-250/20">
                {{ role || 'Système' }}
              </span>
            </div>
          </div>
          <button @click.stop="handleLogout" class="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-all cursor-pointer" title="Se déconnecter">
            <LogOut class="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content Workspace -->
    <div class="flex-1 flex flex-col min-w-0 relative h-full overflow-hidden">
      <!-- Navbar / Top Header -->
      <header class="h-16 border-b border-slate-200/60 bg-white/70 backdrop-blur-xl flex items-center justify-between px-8 shrink-0 z-10">
        <div class="flex items-center space-x-3">
          <h2 class="font-bold text-base text-slate-800 tracking-tight">Centre de mise à jour KM Hub</h2>
          <div class="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-600">
            <span class="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span class="text-[9px] font-mono font-bold tracking-wider uppercase">Serveur de Production</span>
          </div>
        </div>
        <div class="flex items-center space-x-2">
          <!-- Notification bell -->
          <button class="relative p-2 text-slate-500 hover:text-slate-800 rounded-xl hover:bg-slate-100/80 transition-all duration-200 cursor-pointer">
            <Bell class="h-4.5 w-4.5" />
            <span v-if="alerts.length > 0" class="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-indigo-600 border border-white"></span>
          </button>
        </div>
      </header>

      <!-- Main Router view wrapper -->
      <main class="flex-1 overflow-y-auto p-8">
        <router-view />
      </main>

      <!-- Alerts Display Area -->
      <transition-group name="list" tag="div" class="fixed bottom-6 right-6 z-50 space-y-3 w-80 max-h-screen overflow-y-auto">
        <AlertCard 
          v-for="alert in alerts" 
          :key="alert.id" 
          :alert="alert" 
          @resolve="resolveAlert" 
          class="transition-all duration-300 ease-out"
        />
      </transition-group>
    </div>

    <!-- Profile Edit Modal -->
    <div v-if="showProfileModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4 transition-all duration-300">
      <div class="bg-white/90 border border-slate-200/80 backdrop-blur-2xl p-6 rounded-3xl w-full max-w-md shadow-2xl relative">
        <div class="flex items-center space-x-3 mb-6 pb-3 border-b border-slate-100">
          <div class="h-10 w-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center">
            <User class="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h3 class="font-extrabold text-slate-800 text-sm">Modifier le profil</h3>
            <p class="text-[10px] text-slate-400 font-medium">Mettez à jour vos informations personnelles.</p>
          </div>
        </div>

        <div v-if="profileError" class="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-750 text-xs font-semibold">
          {{ profileError }}
        </div>
        <div v-if="profileSuccess" class="mb-4 p-3 rounded-xl bg-emerald-50 border border-emerald-250/20 text-emerald-800 text-xs font-semibold">
          {{ profileSuccess }}
        </div>

        <form @submit.prevent="handleUpdateProfile" class="space-y-4">
          <div>
            <label class="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1 font-mono">Nom d'utilisateur</label>
            <input type="text" :value="user?.username" disabled class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-450 font-bold outline-none cursor-not-allowed" />
          </div>
          <div>
            <label class="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1 font-mono">Rôle</label>
            <input type="text" :value="role" disabled class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-450 font-bold outline-none cursor-not-allowed uppercase font-mono" />
          </div>
          <div>
            <label class="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1 font-mono">Adresse Email</label>
            <input type="email" v-model="profileEmail" required class="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 font-semibold focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none transition-all" />
          </div>
          <div>
            <label class="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-1 font-mono">Nouveau mot de passe (laisser vide pour inchangé)</label>
            <input type="password" v-model="profilePassword" placeholder="••••••••" class="w-full px-3.5 py-2.5 bg-white border border-slate-200 rounded-xl text-xs text-slate-800 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 outline-none transition-all" />
          </div>

          <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
            <button type="button" @click="showProfileModal = false" class="px-4 py-2 text-xs font-bold text-slate-500 hover:bg-slate-100 rounded-xl transition cursor-pointer">
              Annuler
            </button>
            <button type="submit" :disabled="updatingProfile" class="px-4 py-2 text-xs font-bold bg-indigo-600 hover:bg-indigo-550 text-white rounded-xl shadow-md shadow-indigo-600/10 transition cursor-pointer">
              {{ updatingProfile ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style>
@reference "tailwindcss";

/* Custom Router active classes styling */
.router-link-active {
  @apply bg-gradient-to-r from-indigo-500/10 to-indigo-500/[0.02] text-indigo-600 border-l-4 border-indigo-500 rounded-r-xl pl-3.5! font-bold;
}

/* Transition styles for alerts */
.list-enter-active, .list-leave-active {
  transition: all 0.5s ease;
}
.list-enter-from, .list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
