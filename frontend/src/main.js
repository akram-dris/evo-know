import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'
import router from './router'
import App from './App.vue'

// Import styles
import './style.css'
// PrimeVue Tailwind theme/presets will style components natively with Tailwind classes.
// We can use PrimeVue config standard.

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, { ripple: true })

app.mount('#app')
