<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { 
  Users, 
  ShieldCheck, 
  ShieldAlert, 
  Trash2, 
  Check, 
  X, 
  Search, 
  Clock, 
  UserCheck 
} from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

// Configure axios base URL

const usersList = ref([])
const loading = ref(true)
const actionLoading = ref({})
const searchQuery = ref('')
const selectedTab = ref('Tous') // 'Tous', 'Pending', 'Approved'
const message = ref({ text: '', type: '' }) // type: 'success' or 'error'

const confirmModal = ref({
  show: false,
  message: '',
  onConfirm: null
})

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/auth/users', {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    usersList.value = res.data
  } catch (err) {
    console.error("Error fetching users:", err)
    showMsg("Erreur lors du chargement des utilisateurs.", "error")
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUsers()
})

const showMsg = (text, type = 'success') => {
  message.value = { text, type }
  setTimeout(() => {
    message.value = { text: '', type: '' }
  }, 4000)
}

const handleApprove = async (username) => {
  actionLoading.value[username] = 'approve'
  try {
    const res = await axios.post(`/api/v1/auth/users/${username}/approve`, {}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    showMsg(res.data.message)
    await fetchUsers()
  } catch (err) {
    console.error("Approve error:", err)
    showMsg(err.response?.data?.detail || "Erreur d'approbation.", "error")
  } finally {
    delete actionLoading.value[username]
  }
}

const handleReject = async (username) => {
  actionLoading.value[username] = 'reject'
  try {
    const res = await axios.post(`/api/v1/auth/users/${username}/reject`, {}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    showMsg(res.data.message)
    await fetchUsers()
  } catch (err) {
    console.error("Reject error:", err)
    showMsg(err.response?.data?.detail || "Erreur de rejet.", "error")
  } finally {
    delete actionLoading.value[username]
  }
}

const handleDelete = (username) => {
  confirmModal.value = {
    show: true,
    message: `Voulez-vous vraiment supprimer le compte de ${username} ? Cette action est définitive.`,
    onConfirm: async () => {
      confirmModal.value.show = false
      actionLoading.value[username] = 'delete'
      try {
        const res = await axios.delete(`/api/v1/auth/users/${username}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        })
        showMsg(res.data.message)
        await fetchUsers()
      } catch (err) {
        console.error("Delete error:", err)
        showMsg(err.response?.data?.detail || "Erreur de suppression.", "error")
      } finally {
        delete actionLoading.value[username]
      }
    }
  }
}

// Compute stats
const stats = computed(() => {
  const total = usersList.value.length
  const pending = usersList.value.filter(u => u.status === 'pending').length
  const experts = usersList.value.filter(u => u.role === 'Expert' && u.status === 'approved').length
  const readers = usersList.value.filter(u => u.role === 'Reader').length
  return { total, pending, experts, readers }
})

// Filtered Users
const filteredUsers = computed(() => {
  return usersList.value.filter(user => {
    const matchesSearch = user.username.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          (user.email && user.email.toLowerCase().includes(searchQuery.value.toLowerCase()))
    
    let matchesTab = true
    if (selectedTab.value === 'Pending') {
      matchesTab = user.status === 'pending'
    } else if (selectedTab.value === 'Approved') {
      matchesTab = user.status === 'approved'
    }
    
    return matchesSearch && matchesTab
  })
})
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Gestion des Comptes Utilisateurs</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Gérez les comptes, approuvez les demandes d'accès des experts et supprimez les comptes obsolètes.</p>
      </div>
      <Button @click="fetchUsers" :loading="loading" class="bg-indigo-600! hover:bg-indigo-550! text-white! px-4! py-2! rounded-xl! transition! border-none! cursor-pointer! text-xs! font-bold! flex! items-center!">
        <span>Actualiser</span>
      </Button>
    </div>

    <!-- Alert Messages -->
    <div v-if="message.text" :class="message.type === 'error' ? 'bg-rose-50 border-rose-250 text-rose-800' : 'bg-emerald-50 border-emerald-250/20 text-emerald-800'" class="p-4 border text-xs rounded-2xl font-semibold flex items-center space-x-2 transition-all">
      <span :class="message.type === 'error' ? 'bg-rose-500' : 'bg-emerald-500'" class="h-2 w-2 rounded-full animate-pulse"></span>
      <span>{{ message.text }}</span>
    </div>

    <!-- Stats Panel -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
      <div class="bg-white border border-slate-200/50 rounded-3xl p-5 shadow-sm flex items-center space-x-4">
        <div class="h-10 w-10 rounded-2xl bg-indigo-50 flex items-center justify-center text-indigo-600 shrink-0">
          <Users class="h-5 w-5" />
        </div>
        <div>
          <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest font-mono">Utilisateurs</p>
          <h4 class="text-xl font-extrabold text-slate-800 mt-0.5">{{ stats.total }}</h4>
        </div>
      </div>

      <div class="bg-white border border-slate-200/50 rounded-3xl p-5 shadow-sm flex items-center space-x-4">
        <div class="h-10 w-10 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600 shrink-0">
          <Clock class="h-5 w-5" />
        </div>
        <div>
          <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest font-mono">En attente</p>
          <h4 class="text-xl font-extrabold text-slate-800 mt-0.5">{{ stats.pending }}</h4>
        </div>
      </div>

      <div class="bg-white border border-slate-200/50 rounded-3xl p-5 shadow-sm flex items-center space-x-4">
        <div class="h-10 w-10 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600 shrink-0">
          <ShieldCheck class="h-5 w-5" />
        </div>
        <div>
          <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest font-mono">Experts Actifs</p>
          <h4 class="text-xl font-extrabold text-slate-800 mt-0.5">{{ stats.experts }}</h4>
        </div>
      </div>

      <div class="bg-white border border-slate-200/50 rounded-3xl p-5 shadow-sm flex items-center space-x-4">
        <div class="h-10 w-10 rounded-2xl bg-violet-50 flex items-center justify-center text-violet-600 shrink-0">
          <UserCheck class="h-5 w-5" />
        </div>
        <div>
          <p class="text-[9px] font-bold text-slate-400 uppercase tracking-widest font-mono">Lecteurs</p>
          <h4 class="text-xl font-extrabold text-slate-800 mt-0.5">{{ stats.readers }}</h4>
        </div>
      </div>
    </div>

    <!-- Main Table Section -->
    <div class="bg-white border border-slate-200/50 rounded-3xl p-6 shadow-sm space-y-6">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <!-- Tabs -->
        <div class="flex space-x-1.5 bg-slate-50 p-1 rounded-2xl border border-slate-200/60 self-start">
          <button 
            v-for="tab in ['Tous', 'Pending', 'Approved']" 
            :key="tab"
            @click="selectedTab = tab"
            :class="selectedTab === tab ? 'bg-white text-indigo-600 shadow-sm font-bold' : 'text-slate-500 hover:text-slate-800 font-semibold'"
            class="px-4 py-2 text-xs rounded-xl transition cursor-pointer"
          >
            {{ tab === 'Tous' ? 'Tous' : tab === 'Pending' ? 'En attente' : 'Approuvés' }}
          </button>
        </div>

        <!-- Search Bar -->
        <div class="relative w-full md:max-w-xs">
          <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 pointer-events-none">
            <Search class="h-4.5 w-4.5" />
          </span>
          <InputText 
            v-model="searchQuery" 
            placeholder="Rechercher par nom..." 
            class="w-full pl-10! pr-4! py-2! bg-slate-50! border-slate-200! rounded-2xl! focus:border-indigo-500! focus:bg-white! outline-none! text-xs! text-slate-800! transition-all!"
          />
        </div>
      </div>

      <!-- Users List Table -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="border-b border-slate-100 text-[10px] font-bold text-slate-400 uppercase tracking-wider font-mono">
              <th class="py-3.5 px-4">Utilisateur</th>
              <th class="py-3.5 px-4">Email</th>
              <th class="py-3.5 px-4">Rôle</th>
              <th class="py-3.5 px-4">Date de Création</th>
              <th class="py-3.5 px-4">Statut</th>
              <th class="py-3.5 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in filteredUsers" :key="u.username" class="border-b border-slate-100/50 hover:bg-slate-50/40 transition-colors">
              <td class="py-4 px-4">
                <span class="text-sm font-bold text-slate-800 capitalize">{{ u.username }}</span>
              </td>
              <td class="py-4 px-4 text-xs font-semibold text-slate-600">{{ u.email || 'Non renseigné' }}</td>
              <td class="py-4 px-4">
                <span :class="u.role === 'Admin' ? 'bg-indigo-50 text-indigo-700 border border-indigo-200/50' : u.role === 'Expert' ? 'bg-emerald-50 text-emerald-700 border border-emerald-250/20' : 'bg-slate-50 text-slate-600 border border-slate-200'" class="px-2 py-0.5 rounded text-[9px] font-bold font-mono tracking-wider uppercase">
                  {{ u.role }}
                </span>
              </td>
              <td class="py-4 px-4 text-xs font-medium text-slate-500 font-mono">{{ u.created_at || 'Date inconnue' }}</td>
              <td class="py-4 px-4">
                <span :class="u.status === 'approved' ? 'bg-emerald-50 text-emerald-700' : u.status === 'pending' ? 'bg-amber-50 text-amber-700' : 'bg-rose-50 text-rose-700'" class="px-2 py-0.5 rounded-full text-[9px] font-bold capitalize">
                  {{ u.status === 'approved' ? 'Approuvé' : u.status === 'pending' ? 'En attente' : 'Rejeté' }}
                </span>
              </td>
              <td class="py-4 px-4 text-right space-x-1.5">
                <!-- If pending approval -->
                <template v-if="u.status === 'pending'">
                  <button 
                    @click="handleApprove(u.username)"
                    :disabled="actionLoading[u.username]"
                    title="Approuver"
                    class="p-1.5 text-emerald-600 hover:bg-emerald-50 border border-emerald-100 hover:border-emerald-200 rounded-xl transition cursor-pointer"
                  >
                    <Check class="h-4 w-4" />
                  </button>
                  <button 
                    @click="handleReject(u.username)"
                    :disabled="actionLoading[u.username]"
                    title="Rejeter"
                    class="p-1.5 text-rose-600 hover:bg-rose-50 border border-rose-100 hover:border-rose-200 rounded-xl transition cursor-pointer"
                  >
                    <X class="h-4 w-4" />
                  </button>
                </template>

                <!-- If already approved or rejected (Not admin itself) -->
                <template v-if="u.role !== 'Admin'">
                  <button 
                    @click="handleDelete(u.username)"
                    :disabled="actionLoading[u.username]"
                    title="Supprimer le compte"
                    class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 border border-slate-100 hover:border-rose-100 rounded-xl transition cursor-pointer"
                  >
                    <Trash2 class="h-4 w-4" />
                  </button>
                </template>
              </td>
            </tr>
            <tr v-if="filteredUsers.length === 0">
              <td colspan="6" class="text-center py-12 text-slate-450 font-medium">Aucun utilisateur ne correspond à vos filtres.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- Custom Confirmation Modal -->
  <div v-if="confirmModal.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="bg-white border border-slate-200/80 p-6 rounded-3xl w-full max-w-md shadow-2xl relative">
      <!-- Title & Warning Icon -->
      <div class="flex items-center space-x-3.5 mb-4 pb-3 border-b border-slate-100">
        <div class="h-10 w-10 rounded-xl bg-rose-50 border border-rose-100 flex items-center justify-center shrink-0">
          <ShieldAlert class="h-5 w-5 text-rose-600" />
        </div>
        <div>
          <h3 class="font-extrabold text-slate-800 text-sm">Confirmation de suppression</h3>
          <p class="text-[9px] text-slate-400 font-medium font-mono uppercase">Action irréversible</p>
        </div>
      </div>

      <!-- Description -->
      <p class="text-xs text-slate-650 leading-relaxed font-semibold mb-6">
        {{ confirmModal.message }}
      </p>

      <!-- Action Buttons -->
      <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100">
        <button 
          @click="confirmModal.show = false" 
          class="px-4 py-2 text-xs font-bold text-slate-500 hover:bg-slate-100 rounded-xl transition cursor-pointer border-none bg-transparent"
        >
          Annuler
        </button>
        <button 
          @click="confirmModal.onConfirm" 
          class="px-4 py-2 text-xs font-bold bg-rose-600 hover:bg-rose-550 text-white rounded-xl shadow-md shadow-rose-600/10 transition cursor-pointer border-none"
        >
          Confirmer
        </button>
      </div>
    </div>
  </div>
</template>
