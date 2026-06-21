<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import axios from 'axios';
import { 
  ShieldAlert, 
  CheckCircle, 
  AlertTriangle, 
  RefreshCw, 
  Search, 
  Trash2,
  Upload,
  X,
  Plus
} from 'lucide-vue-next';
import Button from 'primevue/button';

const predictions = ref([]);
const loading = ref(true);
const searchQuery = ref('');
const userRole = ref(localStorage.getItem('role') || 'Reader');
const username = localStorage.getItem('username') || 'admin';
const totalPredictions = ref(0);

// Watch for search query and debounce / delay loading to avoid excessive API requests
let searchDebounce = null;
watch(searchQuery, (newVal) => {
  if (searchDebounce) clearTimeout(searchDebounce);
  searchDebounce = setTimeout(() => {
    fetchPredictions(false);
  }, 300);
});

// Upload modal state
const showUploadModal = ref(false);
const uploadFiles = ref([]);
const uploadDept = ref('Telecom RNO');
const uploading = ref(false);
const uploadError = ref('');
const uploadDepartments = ['Support IT', 'Infrastructure', 'Sécurité', 'R&D', 'Telecom RNO'];
const currentUploadingIndex = ref(0);

const confirmModal = ref({
  show: false,
  message: '',
  onConfirm: null
});

const alertModal = ref({
  show: false,
  message: ''
});

const canDelete = computed(() => ['Admin', 'Expert'].includes(userRole.value));
const canUpload = computed(() => ['Admin', 'Expert'].includes(userRole.value));

const openUploadModal = () => {
  uploadFiles.value = [];
  uploadError.value = '';
  showUploadModal.value = true;
};

const onFileChange = (e) => {
  if (e.target.files.length > 0) {
    uploadFiles.value = Array.from(e.target.files);
  } else {
    uploadFiles.value = [];
  }
};

const handleUpload = async () => {
  if (uploadFiles.value.length === 0) {
    uploadError.value = 'Veuillez sélectionner au moins un fichier.';
    return;
  }
  uploading.value = true;
  uploadError.value = '';
  currentUploadingIndex.value = 0;
  
  try {
    for (let i = 0; i < uploadFiles.value.length; i++) {
      currentUploadingIndex.value = i + 1;
      const file = uploadFiles.value[i];
      const formData = new FormData();
      formData.append('file', file);
      formData.append('department', uploadDept.value);
      formData.append('uploaded_by', username);
      
      await axios.post('/api/v1/ingest', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
    }
    
    showUploadModal.value = false;
    await fetchPredictions();
  } catch (err) {
    console.error('Upload error:', err);
    uploadError.value = err.response?.data?.detail || 'Erreur lors du téléversement de certains fichiers.';
    await fetchPredictions();
  } finally {
    uploading.value = false;
  }
};

const fetchPredictions = async (isLoadMore = false) => {
  if (isLoadMore && loading.value) return;
  loading.value = true;
  const limit = 10;
  const offset = isLoadMore ? predictions.value.length : 0;
  try {
    const res = await axios.get('/api/v1/tasks/predictions', {
      params: {
        limit: limit,
        offset: offset,
        search: searchQuery.value || undefined
      }
    });
    if (isLoadMore) {
      predictions.value = [...predictions.value, ...res.data.items];
    } else {
      predictions.value = res.data.items;
    }
    totalPredictions.value = res.data.total;
  } catch (err) {
    console.error("Error fetching predictions:", err);
  } finally {
    loading.value = false;
  }
};

const handleDeleteDoc = (docId, title) => {
  confirmModal.value = {
    show: true,
    message: `Voulez-vous vraiment supprimer définitivement le document "${title}" ainsi que toutes ses prédictions d'obsolescence associées ? Cette action est irréversible.`,
    onConfirm: async () => {
      confirmModal.value.show = false;
      try {
        await axios.delete(`/api/v1/ingest/documents/${docId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        await fetchPredictions(false);
      } catch (err) {
        console.error("Delete error:", err);
        alertModal.value = {
          show: true,
          message: err.response?.data?.detail || "Erreur lors de la suppression du document."
        };
      }
    }
  };
};

const filteredPredictions = computed(() => {
  return predictions.value;
});

const handleWindowScroll = async (event) => {
  const target = event.target || document.documentElement;
  const isDoc = target === document || target === document.documentElement || target === window || target === document.body;
  const scrollHeight = isDoc ? document.documentElement.scrollHeight : target.scrollHeight;
  const scrollTop = isDoc ? (document.documentElement.scrollTop || document.body.scrollTop) : target.scrollTop;
  const clientHeight = isDoc ? document.documentElement.clientHeight : target.clientHeight;
  
  if (scrollHeight - scrollTop - clientHeight < 100) {
    if (predictions.value.length < totalPredictions.value && !loading.value) {
      await fetchPredictions(true);
    }
  }
};

onMounted(() => {
  fetchPredictions(false);
  window.addEventListener('scroll', handleWindowScroll, true);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleWindowScroll, true);
});
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">T1 : Prédiction des besoins de mise à jour</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Surveillance en temps réel de l'obsolescence calculée par les modèles LSTM et Prophet.</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          v-if="canUpload"
          @click="openUploadModal"
          class="flex items-center gap-2 px-4 py-2.5 text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-md shadow-indigo-600/20 transition cursor-pointer border-none"
        >
          <Plus class="h-4 w-4" />
          <span>Importer</span>
        </button>
        <Button @click="fetchPredictions" class="bg-white! hover:bg-slate-50! text-slate-700! text-xs! px-4! py-2.5! rounded-xl! font-bold! border-slate-200/80! border! transition! flex! items-center! cursor-pointer!">
          <RefreshCw class="h-4 w-4 mr-2" :class="{'animate-spin': loading}" />
          <span>Actualiser</span>
        </Button>
      </div>
    </div>

    <!-- Action Bar (Search field) -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="relative w-full md:max-w-xs">
        <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 pointer-events-none">
          <Search class="h-4.5 w-4.5" />
        </span>
        <input 
          v-model="searchQuery" 
          type="text"
          placeholder="Rechercher par document..." 
          class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-2xl focus:border-indigo-500 focus:bg-white outline-none text-xs text-slate-800 transition-all placeholder:text-slate-400"
        />
      </div>
    </div>

    <div v-if="loading && predictions.length === 0" class="text-center py-24 text-slate-500 font-medium">Chargement des prédictions d'obsolescence...</div>
    
    <div v-else class="bg-white border border-slate-200/50 rounded-3xl overflow-hidden shadow-[0_12px_35px_rgba(0,0,0,0.025)]">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead class="bg-slate-50/70 text-slate-400 text-[10px] font-bold uppercase tracking-wider font-mono border-b border-slate-200/40">
            <tr>
              <th class="p-5">Nom du Document</th>
              <th class="p-5">Département</th>
              <th class="p-5">Modèle Utilisé</th>
              <th class="p-5">Score d'Obsolescence</th>
              <th class="p-5">Priorité</th>
              <th v-if="canDelete" class="p-5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-100/80">
            <tr v-for="item in filteredPredictions" :key="item.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="p-5 font-bold text-slate-800">{{ item.title }}</td>
              <td class="p-5 text-slate-500 font-semibold">{{ item.department }}</td>
              <td class="p-5">
                <span class="bg-slate-50 text-slate-600 text-[10px] px-2.5 py-1 rounded-lg border border-slate-200/40 font-bold font-mono">
                  {{ item.model_version }}
                </span>
              </td>
              <td class="p-5">
                <div class="flex items-center space-x-3">
                  <span class="font-bold text-xs font-mono w-10 text-right" :class="item.score > 0.7 ? 'text-rose-600' : (item.score > 0.4 ? 'text-amber-500' : 'text-emerald-600')">
                    {{ (item.score * 100).toFixed(0) }}%
                  </span>
                  <div class="w-32 bg-slate-100 rounded-full h-2 overflow-hidden shadow-inner">
                    <div class="h-full rounded-full transition-all duration-500" 
                          :class="item.score > 0.7 ? 'bg-gradient-to-r from-rose-500 to-rose-600' : (item.score > 0.4 ? 'bg-gradient-to-r from-amber-400 to-amber-500' : 'bg-gradient-to-r from-emerald-500 to-emerald-600')"
                          :style="{ width: (item.score * 100) + '%' }"></div>
                  </div>
                </div>
              </td>
              <td class="p-5">
                <span class="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold"
                      :class="item.priority === 'Critical' ? 'bg-rose-50 text-rose-700 border border-rose-250/30' : (item.priority === 'High' ? 'bg-amber-50 text-amber-700 border border-amber-250/30' : 'bg-emerald-50 text-emerald-700 border border-emerald-250/30')">
                  <ShieldAlert v-if="item.priority === 'Critical'" class="h-3.5 w-3.5" />
                  <AlertTriangle v-else-if="item.priority === 'High'" class="h-3.5 w-3.5" />
                  <CheckCircle v-else class="h-3.5 w-3.5" />
                  <span>{{ item.priority === 'Critical' ? 'Critique' : (item.priority === 'High' ? 'Haute' : 'Normale') }}</span>
                </span>
              </td>
              <td v-if="canDelete" class="p-5 text-right">
                <button 
                  @click="handleDeleteDoc(item.document_id, item.title)"
                  title="Supprimer le document"
                  class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 border border-slate-100 hover:border-rose-100 rounded-xl transition cursor-pointer"
                >
                  <Trash2 class="h-4 w-4" />
                </button>
              </td>
            </tr>
            <tr v-if="filteredPredictions.length === 0">
              <td :colspan="canDelete ? 6 : 5" class="text-center py-12 text-slate-450 font-medium">Aucun document ne correspond à vos filtres.</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Scroll pagination indicator -->
      <div v-if="predictions.length < totalPredictions" class="text-center py-6 text-xs text-slate-400 font-bold bg-slate-50/50 rounded-2xl border-t border-slate-200/50">
        Faites défiler vers le bas pour charger plus de prédictions ({{ predictions.length }} affichées sur {{ totalPredictions }})
      </div>
    </div>
  </div>

  <!-- Upload Document Modal -->
  <div v-if="showUploadModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="bg-white border border-slate-200/80 p-6 rounded-3xl w-full max-w-md shadow-2xl relative">
      <button @click="showUploadModal = false" class="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition cursor-pointer">
        <X class="h-4 w-4" />
      </button>

      <div class="flex items-center space-x-3 mb-6 pb-3 border-b border-slate-100">
        <div class="h-10 w-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center shrink-0">
          <Upload class="h-5 w-5 text-indigo-600" />
        </div>
        <div>
          <h3 class="font-extrabold text-slate-800 text-sm">Importer un Document</h3>
          <p class="text-[10px] text-slate-400 font-medium">Téléversez un nouveau manuel technique (.pdf, .docx, .txt).</p>
        </div>
      </div>

      <div v-if="uploadError" class="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold">
        {{ uploadError }}
      </div>

      <form @submit.prevent="handleUpload" class="space-y-4">
        <div>
          <label class="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-2 font-mono">Sélectionner les fichiers</label>
          <input
            type="file"
            @change="onFileChange"
            accept=".pdf,.docx,.txt"
            multiple
            class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
            required
          />
          
          <!-- List of selected files -->
          <div v-if="uploadFiles.length > 0" class="mt-3 space-y-1.5 max-h-32 overflow-y-auto border border-slate-100 rounded-xl p-3 bg-slate-50/50">
            <div v-for="file in uploadFiles" :key="file.name" class="text-[10px] font-bold text-slate-650 flex items-center justify-between">
              <span class="truncate max-w-[280px]">{{ file.name }}</span>
              <span class="text-[8px] text-indigo-650 bg-indigo-50/50 px-1.5 py-0.5 rounded font-mono font-bold">{{ (file.size / 1024).toFixed(1) }} KB</span>
            </div>
          </div>
        </div>

        <div>
          <label class="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-2 font-mono">Département concerné</label>
          <select v-model="uploadDept" class="w-full px-3.5 py-2.5 bg-slate-50/10 border border-slate-200 rounded-xl text-xs text-slate-700 font-semibold outline-none focus:border-indigo-500 transition-all">
            <option v-for="dept in uploadDepartments" :key="dept" :value="dept">{{ dept }}</option>
          </select>
        </div>

        <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100 mt-6">
          <button type="button" @click="showUploadModal = false" class="px-4 py-2 text-xs font-bold text-slate-500 hover:bg-slate-100 rounded-xl transition cursor-pointer border-none bg-transparent">
            Annuler
          </button>
          <button type="submit" :disabled="uploading" class="px-4 py-2 text-xs font-bold bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-md shadow-indigo-600/10 transition cursor-pointer border-none">
            {{ uploading ? `Ingestion (${currentUploadingIndex}/${uploadFiles.length})...` : 'Téléverser' }}
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Custom Confirmation Modal (z-index 50 layer) -->
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

  <!-- Custom Error Alert Modal (z-index 50 layer) -->
  <div v-if="alertModal.show" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="bg-white border border-slate-200/80 p-6 rounded-3xl w-full max-w-md shadow-2xl relative">
      <div class="flex items-center space-x-3.5 mb-4 pb-3 border-b border-slate-100">
        <div class="h-10 w-10 rounded-xl bg-rose-50 border border-rose-100 flex items-center justify-center shrink-0">
          <ShieldAlert class="h-5 w-5 text-rose-600" />
        </div>
        <div>
          <h3 class="font-extrabold text-slate-800 text-sm">Erreur</h3>
          <p class="text-[9px] text-slate-400 font-medium font-mono uppercase">Échec de l'action</p>
        </div>
      </div>
      <p class="text-xs text-slate-650 leading-relaxed font-semibold mb-6">
        {{ alertModal.message }}
      </p>
      <div class="flex items-center justify-end pt-3 border-t border-slate-100">
        <button @click="alertModal.show = false" class="px-5 py-2.5 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition cursor-pointer border-none">
          Fermer
        </button>
      </div>
    </div>
  </div>
</template>
