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
  <div class="p-4 border-l-4 rounded-2xl flex items-start space-x-4 bg-white border border-slate-200/80 shadow-lg shadow-slate-100/60 backdrop-blur-md"
       :class="alert.severity === 'critical' ? 'border-rose-500' : 'border-amber-500'">
    <div class="flex-1 space-y-1.5">
      <div class="flex items-center justify-between">
        <span class="font-bold text-slate-800 text-xs truncate max-w-[150px]">{{ alert.title }}</span>
        <span class="text-[9px] px-2 py-0.5 rounded-md font-bold font-mono tracking-wider uppercase" 
              :class="alert.severity === 'critical' ? 'bg-rose-50 text-rose-700 border border-rose-200/40' : 'bg-amber-50 text-amber-700 border border-amber-200/40'">
          {{ alert.severity }}
        </span>
      </div>
      <p class="text-[11px] text-slate-600 leading-relaxed font-medium">{{ alert.message }}</p>
      <div class="pt-1 flex space-x-2">
        <button @click="takeAction('review')" class="bg-indigo-600 hover:bg-indigo-550 text-white text-[10px] font-bold px-3.5 py-1.5 rounded-lg shadow-xs transition-all cursor-pointer">
          Analyser
        </button>
        <button @click="takeAction('archive')" class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-[10px] font-bold px-3.5 py-1.5 rounded-lg transition-all cursor-pointer">
          Archiver
        </button>
      </div>
    </div>
  </div>
</template>
