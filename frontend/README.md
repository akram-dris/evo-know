# 🖥️ EvoKnow Frontend Web Application

This is the user interface of the **Cloud-Native Knowledge Management (KM) Update System**, implemented as a Single Page Application (SPA) using **Vue.js 3** and styled with **Tailwind CSS v4**.

---

## 🏗️ Technology Stack
* **Framework**: Vue 3 (Composition API, `<script setup>`)
* **Styling**: Tailwind CSS v4 (using the `@tailwindcss/vite` compiler plugin)
* **Components**: PrimeVue
* **State Store**: Pinia (auth, knowledge base, tasks states)
* **Routing**: Vue Router
* **API Client**: Axios

---

## 🛠️ Local Development & Build Setup

Ensure Node.js v20+ is installed.

### 1. Install dependencies:
```bash
npm install
```

### 2. Start the development server:
Runs on port `5173`:
```bash
npm run dev
```

### 3. Compile for production:
Generates static assets in `/dist`:
```bash
npm run build
```

---

## 📂 File Architecture
```
frontend/
├── src/
│   ├── assets/         # Visual elements, logos, icons
│   ├── components/     # Layout shells and widgets (RAG Chat, active alerts)
│   ├── router/         # Vue Router configurations
│   ├── stores/         # Pinia global states (useAuthStore, useTaskStore)
│   ├── views/          # 9 core page templates (Dashboard, T1-T5 analytics views)
│   ├── App.vue         # Main layout shell
│   ├── main.js         # Vue bootstrap and config mounting
│   └── style.css       # Tailwind v4 import endpoint
├── index.html          # HTML5 mounting point
├── vite.config.js       # Vite build configurations (Tailwind v4 integration)
└── Dockerfile          # NginX web server build blueprint
```
