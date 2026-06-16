<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Cpu, ShieldCheck, Key, User, ArrowRight } from 'lucide-vue-next'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

// Configure axios base URL from environment variable

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')

// Registration states
const isRegister = ref(false)
const regUsername = ref('')
const regEmail = ref('')
const regPassword = ref('')
const regRole = ref('Reader')
const regSuccessMessage = ref('')

const handleLogin = async () => {
  if (!username.value || !password.value) {
    errorMessage.value = 'Veuillez saisir votre nom d\'utilisateur et votre mot de passe.'
    return
  }

  loading.value = true
  errorMessage.value = ''
  regSuccessMessage.value = ''

  try {
    const response = await axios.post('/api/v1/auth/login', {
      username: username.value,
      password: password.value
    })

    // Store token and user data in localStorage
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('user', JSON.stringify(response.data.user))
    localStorage.setItem('role', response.data.role)

    // Redirect with page refresh to reload App.vue state
    if (response.data.role === 'Reader') {
      window.location.href = '/knowledge-base'
    } else {
      window.location.href = '/'
    }
  } catch (error) {
    console.error('Login error:', error)
    if (error.response && error.response.status === 401) {
      errorMessage.value = 'Nom d\'utilisateur ou mot de passe incorrect.'
    } else if (error.response && error.response.status === 403) {
      errorMessage.value = error.response.data.detail || 'Votre compte n\'est pas encore approuvé.'
    } else {
      errorMessage.value = 'Une erreur est survenue lors de la connexion au serveur.'
    }
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!regUsername.value || !regEmail.value || !regPassword.value) {
    errorMessage.value = 'Veuillez remplir tous les champs d\'inscription.'
    return
  }

  loading.value = true
  errorMessage.value = ''
  regSuccessMessage.value = ''

  try {
    const response = await axios.post('/api/v1/auth/register', {
      username: regUsername.value,
      email: regEmail.value,
      password: regPassword.value,
      role: regRole.value
    })

    regSuccessMessage.value = response.data.message
    
    const registeredName = regUsername.value
    
    // Reset fields
    regUsername.value = ''
    regEmail.value = ''
    regPassword.value = ''
    
    // If reader, auto fill login username and switch to login tab after 2 seconds
    if (response.data.user_status === 'approved') {
      setTimeout(() => {
        isRegister.value = false
        username.value = registeredName
        errorMessage.value = ''
        regSuccessMessage.value = ''
      }, 2500)
    }
  } catch (error) {
    console.error('Registration error:', error)
    errorMessage.value = error.response?.data?.detail || 'Une erreur est survenue lors de l\'inscription.'
  } finally {
    loading.value = false
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
      <div class="flex flex-col items-center mb-6">
        <div class="h-14 w-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 mb-4 shrink-0">
          <Cpu class="h-8 w-8 text-white" />
        </div>
        <h1 class="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-slate-900 to-indigo-950 bg-clip-text text-transparent">
          EvoKnow
        </h1>
        <p class="text-[10px] text-indigo-500 font-mono font-bold uppercase tracking-widest mt-2">Gestion des Connaissances</p>
      </div>

      <!-- Toggle Tabs -->
      <div class="flex border-b border-slate-100 mb-6 font-semibold text-xs">
        <button 
          @click="isRegister = false; errorMessage = ''; regSuccessMessage = ''" 
          :class="!isRegister ? 'border-b-2 border-indigo-600 text-indigo-600 font-bold' : 'text-slate-400 hover:text-slate-600'"
          class="flex-1 pb-3 text-center transition cursor-pointer"
        >
          Se connecter
        </button>
        <button 
          @click="isRegister = true; errorMessage = ''; regSuccessMessage = ''" 
          :class="isRegister ? 'border-b-2 border-indigo-600 text-indigo-600 font-bold' : 'text-slate-400 hover:text-slate-600'"
          class="flex-1 pb-3 text-center transition cursor-pointer"
        >
          Créer un compte
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="errorMessage" class="mb-5 p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-start space-x-2">
        <ShieldCheck class="h-4 w-4 shrink-0 mt-0.5" />
        <span class="font-medium">{{ errorMessage }}</span>
      </div>

      <!-- Success Message -->
      <div v-if="regSuccessMessage" class="mb-5 p-4 rounded-2xl bg-emerald-50 border border-emerald-250/20 text-emerald-800 text-xs flex items-start space-x-2">
        <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse mt-1.5 shrink-0"></span>
        <span class="font-medium">{{ regSuccessMessage }}</span>
      </div>

      <!-- Login Form -->
      <form v-if="!isRegister" @submit.prevent="handleLogin" class="space-y-5">
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

      <!-- Registration Form -->
      <form v-else @submit.prevent="handleRegister" class="space-y-5">
        <div>
          <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 font-mono">Nom d'utilisateur</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-4 flex items-center text-slate-400 z-10">
              <User class="h-4.5 w-4.5" />
            </span>
            <InputText 
              v-model="regUsername" 
              placeholder="ex. nom_utilisateur" 
              class="w-full pl-11! py-3! bg-slate-50/50! border-slate-200/80! rounded-2xl! focus:border-indigo-500! focus:ring-4! focus:ring-indigo-500/10! outline-none! text-sm! text-slate-800! transition-all! placeholder:text-slate-400!"
              required
            />
          </div>
        </div>

        <div>
          <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 font-mono">Adresse Email</label>
          <div class="relative">
            <span class="absolute inset-y-0 left-0 pl-4 flex items-center text-slate-400 z-10">
              <User class="h-4.5 w-4.5" />
            </span>
            <InputText 
              v-model="regEmail" 
              type="email"
              placeholder="votre@email.com" 
              class="w-full pl-11! py-3! bg-slate-50/50! border-slate-200/80! rounded-2xl! focus:border-indigo-500! focus:ring-4! focus:ring-indigo-500/10! outline-none! text-sm! text-slate-800! transition-all! placeholder:text-slate-400!"
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
              v-model="regPassword" 
              type="password" 
              placeholder="••••••••" 
              class="w-full pl-11! py-3! bg-slate-50/50! border-slate-200/80! rounded-2xl! focus:border-indigo-500! focus:ring-4! focus:ring-indigo-500/10! outline-none! text-sm! text-slate-800! transition-all! placeholder:text-slate-400!"
              required
            />
          </div>
        </div>

        <div>
          <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 font-mono">Type d'accès requis</label>
          <div class="grid grid-cols-2 gap-3">
            <label class="flex items-center justify-between p-3 border border-slate-250/60 rounded-2xl cursor-pointer hover:bg-slate-50 transition-all" :class="regRole === 'Reader' ? 'border-indigo-500 bg-indigo-50/10' : ''">
              <span class="text-xs font-semibold text-slate-700">Lecteur</span>
              <input type="radio" value="Reader" v-model="regRole" class="accent-indigo-650" />
            </label>
            <label class="flex items-center justify-between p-3 border border-slate-250/60 rounded-2xl cursor-pointer hover:bg-slate-50 transition-all" :class="regRole === 'Expert' ? 'border-indigo-500 bg-indigo-50/10' : ''">
              <span class="text-xs font-semibold text-slate-700">Expert</span>
              <input type="radio" value="Expert" v-model="regRole" class="accent-indigo-650" />
            </label>
          </div>
          <p class="text-[9px] text-slate-400 mt-2 font-medium">Note : Les comptes Experts nécessitent une approbation par l'administrateur.</p>
        </div>

        <Button 
          type="submit" 
          :loading="loading"
          class="w-full py-3.5! bg-indigo-600! hover:bg-indigo-550! text-white! font-bold! rounded-2xl! shadow-lg! shadow-indigo-600/10! hover:shadow-indigo-600/20! transition-all! duration-200! flex! items-center! justify-center! cursor-pointer! border-none!"
        >
          <div class="flex items-center justify-center w-full">
            <span v-if="loading">Création...</span>
            <span v-else class="flex items-center justify-center">
              <span>S'enregistrer</span>
              <ArrowRight class="h-4 w-4 ml-2 inline-block" />
            </span>
          </div>
        </Button>
      </form>


    </div>
  </div>
</template>
