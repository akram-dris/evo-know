import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import router from './router'
import App from './App.vue'
import axios from 'axios'

// Set Axios base URL globally
axios.defaults.baseURL = import.meta.env.VITE_API_URL;

// Import styles
import './style.css'
// PrimeVue Tailwind theme/presets will style components natively with Tailwind classes.
// We can use PrimeVue config standard.

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, { ripple: true })

app.mount('#app')
