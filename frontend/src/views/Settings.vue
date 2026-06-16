<script setup>
import { ref } from 'vue';
import { Sliders, Database, Save, ShieldAlert } from 'lucide-vue-next';
import Button from 'primevue/button';

const neo4jThreshold = ref(0.7);
const aprioriSupport = ref(0.3);
const aprioriConfidence = ref(0.5);
const enableAutoResolve = ref(false);

const saving = ref(false);
const saveSuccess = ref(false);

const saveSettings = () => {
  saving.value = true;
  saveSuccess.value = false;
  setTimeout(() => {
    saving.value = false;
    saveSuccess.value = true;
  }, 1000);
};
</script>

<template>
  <div class="space-y-6">
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Configuration Système</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Configurez les hyperparamètres des modèles, les clés LLM et les connecteurs d'entreprise.</p>
      </div>
      <Button @click="saveSettings" :loading="saving" class="bg-indigo-600! hover:bg-indigo-550! text-white! px-5! py-2.5! rounded-xl! transition! flex! items-center! text-xs! font-bold! shadow-md! shadow-indigo-600/10! cursor-pointer! border-none!">
        <Save class="h-4 w-4 mr-2" />
        <span>{{ saving ? 'Enregistrement...' : 'Enregistrer' }}</span>
      </Button>
    </div>

    <!-- Alert Success -->
    <div v-if="saveSuccess" class="p-4 bg-emerald-50 border border-emerald-250/20 text-emerald-800 text-xs rounded-2xl font-semibold flex items-center space-x-2">
      <span class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
      <span>Configuration sauvegardée avec succès dans l'API Gateway.</span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Vector Database Params -->
      <div class="bg-white border border-slate-200/50 rounded-3xl p-6 shadow-sm space-y-5">
        <div class="flex items-center space-x-2.5 pb-2.5 border-b border-slate-100">
          <Database class="h-5 w-5 text-indigo-600" />
          <h3 class="font-bold text-slate-800 text-sm">Base Vectorielle & Graphe</h3>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-2 font-mono">Adresse Neo4j BOLT</label>
            <input type="text" value="bolt://localhost:7687" disabled class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-550 font-bold font-mono outline-none cursor-not-allowed" />
          </div>
          <div>
            <div class="flex justify-between items-center mb-2">
              <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">Seuil de similitude Cosinus</label>
              <span class="text-xs font-bold text-indigo-600 font-mono">{{ neo4jThreshold }}</span>
            </div>
            <input type="range" min="0.4" max="0.95" step="0.05" v-model="neo4jThreshold" class="w-full accent-indigo-600 cursor-pointer" />
          </div>
        </div>
      </div>

      <!-- Discovery & Apriori -->
      <div class="bg-white border border-slate-200/50 rounded-3xl p-6 shadow-sm space-y-5">
        <div class="flex items-center space-x-2.5 pb-2.5 border-b border-slate-100">
          <Sliders class="h-5 w-5 text-indigo-600" />
          <h3 class="font-bold text-slate-800 text-sm">Paramètres d'Extraction Apriori</h3>
        </div>

        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="flex justify-between items-center mb-2">
                <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">Support Min</label>
                <span class="text-xs font-bold text-indigo-600 font-mono">{{ aprioriSupport }}</span>
              </div>
              <input type="range" min="0.1" max="0.8" step="0.05" v-model="aprioriSupport" class="w-full accent-indigo-600 cursor-pointer" />
            </div>
            <div>
              <div class="flex justify-between items-center mb-2">
                <label class="block text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">Confiance Min</label>
                <span class="text-xs font-bold text-indigo-600 font-mono">{{ aprioriConfidence }}</span>
              </div>
              <input type="range" min="0.2" max="0.9" step="0.05" v-model="aprioriConfidence" class="w-full accent-indigo-600 cursor-pointer" />
            </div>
          </div>

          <div class="flex items-center justify-between pt-2">
            <div>
              <p class="text-xs font-bold text-slate-800">Arbitrage de Cohérence Automatique</p>
              <p class="text-[10px] text-slate-400 mt-1 font-semibold">Résout les contradictions mineures automatiquement via LLM</p>
            </div>
            <input type="checkbox" v-model="enableAutoResolve" class="w-4 h-4 accent-indigo-600 rounded cursor-pointer" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
