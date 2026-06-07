<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  alert: Object
});
const emit = defineEmits(['resolve']);

const takeAction = async (action) => {
  emit('resolve', props.alert.id, action);
};
</script>

<template>
  <div class="p-4 border-l-4 rounded-r-lg flex items-start space-x-4 glass-panel"
       :class="alert.severity === 'critical' ? 'border-rose-500 bg-rose-500/5' : 'border-amber-500 bg-amber-500/5'">
    <div class="flex-1">
      <div class="flex items-center space-x-2">
        <span class="font-semibold text-sm">{{ alert.title }}</span>
        <span class="text-xs px-2 py-0.5 rounded" 
              :class="alert.severity === 'critical' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'">
          {{ alert.severity }}
        </span>
      </div>
      <p class="text-xs text-slate-400 mt-1">{{ alert.message }}</p>
      <div class="mt-3 flex space-x-2">
        <button @click="takeAction('review')" class="bg-indigo-600 hover:bg-indigo-500 text-white text-xs px-3 py-1.5 rounded font-medium">Review</button>
        <button @click="takeAction('archive')" class="bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs px-3 py-1.5 rounded font-medium">Archive</button>
      </div>
    </div>
  </div>
</template>
