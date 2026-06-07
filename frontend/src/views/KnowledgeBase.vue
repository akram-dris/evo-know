<script setup>
import RAGChatbot from '../components/widgets/RAGChatbot.vue';
import axios from 'axios';

// Configure axios base URL from environment variable
axios.defaults.baseURL = import.meta.env.VITE_API_URL;
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-100 p-6 rounded-2xl border border-slate-200 glass-panel shadow-xs">
      <h1 class="text-2xl font-bold text-slate-900">Catalogue de la base de connaissances</h1>
      <p class="text-slate-600 text-sm mt-1">Recherche plein texte, recherche sémantique et gestion des fiches de connaissances.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="p-6 bg-white border border-slate-200 rounded-2xl glass-panel text-slate-600 text-center py-20 shadow-xs">
        Le catalogue de la base de connaissances est chargé. Accédez aux cartes de détails, appliquez des filtres ou lancez l'édition de documents.
      </div>
      
      <div>
        <RAGChatbot />
      </div>
    </div>
  </div>
</template>
