<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Cpu, ShieldCheck, Key, User, ArrowRight } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    errorMessage.value = 'Veuillez saisir votre nom d\'utilisateur et votre mot de passe.'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const response = await axios.post('/api/v1/auth/login', {
      username: username.value,
      password: password.value
    })

    // Store token and user data in localStorage
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('user', JSON.stringify(response.data.user))
    localStorage.setItem('role', response.data.role)

    // Redirect to dashboard
    router.push('/')
  } catch (error) {
    console.error('Login error:', error)
    if (error.response && error.response.status === 401) {
      errorMessage.value = 'Nom d\'utilisateur ou mot de passe incorrect.'
    } else {
      errorMessage.value = 'Une erreur est survenue lors de la connexion au serveur.'
    }
  } finally {
    loading.value = false
  }
}

// Quick credentials fill helper for demonstration purposes
const fillCredentials = (userType) => {
  if (userType === 'admin') {
    username.value = 'admin'
    password.value = 'admin_pass_2026'
  } else if (userType === 'expert') {
    username.value = 'expert'
    password.value = 'expert_pass_2026'
  } else if (userType === 'reader') {
    username.value = 'reader'
    password.value = 'reader_pass_2026'
  }
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 flex items-center justify-center p-4 relative overflow-hidden">
    <!-- Background animations / glows -->
    <div class="absolute -top-40 -left-40 w-[600px] h-[600px] rounded-full bg-indigo-550/10 blur-[130px] pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-[600px] h-[600px] rounded-full bg-purple-450/10 blur-[130px] pointer-events-none"></div>
    <div class="absolute top-1/3 left-1/3 w-[300px] h-[300px] rounded-full bg-pink-400/5 blur-[100px] pointer-events-none"></div>

    <div class="w-full max-w-md bg-white/70 border border-slate-200/60 backdrop-blur-2xl p-8 rounded-3xl shadow-xl shadow-slate-100/50 relative z-10">
      <!-- Header / Logo -->
      <div class="flex flex-col items-center mb-8">
        <div class="h-14 w-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 mb-4 animate-float">
          <Cpu class="h-8 w-8 text-white" />
        </div>
        <h1 class="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 to-indigo-950 bg-clip-text text-transparent">
          EvoKnow
        </h1>
        <p class="text-[10px] text-indigo-500 font-mono font-bold uppercase tracking-widest mt-2">Authentification de la Plateforme</p>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mb-5 p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start space-x-2">
        <ShieldCheck class="h-4 w-4 shrink-0 mt-0.5" />
        <span class="font-medium">{{ errorMessage }}</span>
      </div>

      <!-- Login Form -->
      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 font-mono">Nom d'utilisateur</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-4 flex items-center text-slate-400 z-10">
              <User class="h-4.5 w-4.5" />
            </span>
            <InputText 
              v-model="username" 
              placeholder="ex. admin" 
              class="w-full pl-11! py-3! bg-slate-50/50! border-slate-200/80! rounded-2xl! focus:border-indigo-500! focus:ring-4! focus:ring-indigo-500/10! outline-none! text-sm! text-slate-800! transition-all! placeholder:text-slate-400! font-medium!"
              required
            />
          </div>
        </div>

        <div>
          <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 font-mono">Mot de passe</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-4 flex items-center text-slate-400 z-10">
              <Key class="h-4.5 w-4.5" />
            </span>
            <InputText 
              v-model="password" 
              type="password" 
              placeholder="••••••••" 
              class="w-full pl-11! py-3! bg-slate-50/50! border-slate-200/80! rounded-2xl! focus:border-indigo-500! focus:ring-4! focus:ring-indigo-500/10! outline-none! text-sm! text-slate-800! transition-all! placeholder:text-slate-400!"
              required
            />
          </div>
        </div>

        <Button 
          type="submit" 
          :loading="loading"
          class="w-full py-3.5! bg-indigo-600! hover:bg-indigo-550! text-white! font-bold! rounded-2xl! shadow-lg! shadow-indigo-600/10! hover:shadow-indigo-600/20! transition-all! duration-200! flex! items-center! justify-center! cursor-pointer! border-none!"
        >
          <div class="flex items-center justify-center w-full">
            <span v-if="loading">Vérification...</span>
            <span v-else class="flex items-center justify-center">
              <span>Se connecter</span>
              <ArrowRight class="h-4 w-4 ml-2 inline-block" />
            </span>
          </div>
        </Button>
      </form>

      <!-- Credentials Helper Panel for quick presentation demo -->
      <div class="mt-8 border-t border-slate-200/60 pt-6">
        <p class="text-center text-[9px] text-slate-400 uppercase tracking-widest font-bold font-mono mb-4">Comptes de démonstration</p>
        <div class="grid grid-cols-3 gap-2.5">
          <button 
            @click="fillCredentials('admin')" 
            type="button"
            class="px-2 py-2.5 text-xs bg-slate-50 border border-slate-200/70 hover:border-indigo-500/50 hover:bg-indigo-50/30 rounded-2xl transition-all text-slate-700 flex flex-col items-center cursor-pointer hover:shadow-xs"
          >
            <span class="font-bold text-[10px] text-indigo-600">Admin</span>
            <span class="text-[9px] text-slate-400 font-mono mt-0.5">Full access</span>
          </button>
          <button 
            @click="fillCredentials('expert')" 
            type="button"
            class="px-2 py-2.5 text-xs bg-slate-50 border border-slate-200/70 hover:border-emerald-500/50 hover:bg-emerald-50/30 rounded-2xl transition-all text-slate-700 flex flex-col items-center cursor-pointer hover:shadow-xs"
          >
            <span class="font-bold text-[10px] text-emerald-600">Expert</span>
            <span class="text-[9px] text-slate-400 font-mono mt-0.5">Operations</span>
          </button>
          <button 
            @click="fillCredentials('reader')" 
            type="button"
            class="px-2 py-2.5 text-xs bg-slate-50 border border-slate-200/70 hover:border-amber-500/50 hover:bg-amber-50/30 rounded-2xl transition-all text-slate-700 flex flex-col items-center cursor-pointer hover:shadow-xs"
          >
            <span class="font-bold text-[10px] text-amber-600">Reader</span>
            <span class="text-[9px] text-slate-400 font-mono mt-0.5">Read-Only</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
