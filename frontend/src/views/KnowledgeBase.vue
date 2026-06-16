<script setup>
import { ref, computed, onMounted } from 'vue';
import RAGChatbot from '../components/widgets/RAGChatbot.vue';
import { 
  Search, 
  FolderOpen, 
  FileText, 
  Calendar, 
  Tag, 
  Eye, 
  Trash2, 
  Plus, 
  X, 
  Upload,
  ShieldAlert
} from 'lucide-vue-next';
import axios from 'axios';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';

// Configure axios base URL from environment variable
axios.defaults.baseURL = import.meta.env.VITE_API_URL;

const searchQuery = ref('');
const selectedDept = ref('Tous');

const departments = ['Tous', 'Support IT', 'Infrastructure', 'Sécurité', 'R&D', 'Telecom RNO'];
const uploadDepartments = ['Support IT', 'Infrastructure', 'Sécurité', 'R&D', 'Telecom RNO'];

const docsList = ref([]);
const loading = ref(true);

// Role states
const role = ref(localStorage.getItem('role') || '');
const user = ref(JSON.parse(localStorage.getItem('user') || '{}'));

// Document Viewer Modal State
const showViewModal = ref(false);
const selectedDocContent = ref('');
const selectedDocTitle = ref('');
const loadingContent = ref(false);

// Document Upload Modal State
const showUploadModal = ref(false);
const showCatalogModal = ref(false);
const uploadFile = ref(null);
const uploadDept = ref('Telecom RNO');
const uploading = ref(false);
const uploadError = ref('');

const confirmModal = ref({
  show: false,
  message: '',
  onConfirm: null
});

const alertModal = ref({
  show: false,
  message: ''
});

const fetchDocs = async () => {
  loading.value = true;
  try {
    const res = await axios.get('/api/v1/query/documents');
    docsList.value = res.data.map(d => ({
      id: d.id,
      title: d.title,
      type: d.source_type,
      dept: d.department,
      date: d.uploaded_at || 'Non spécifié',
      author: d.uploaded_by || 'seeding_script',
      status: d.status
    }));
  } catch (err) {
    console.error("Error fetching documents:", err);
  } finally {
    loading.value = false;
  }
};

const openViewDoc = async (docId, title) => {
  showViewModal.value = true;
  selectedDocTitle.value = title;
  selectedDocContent.value = '';
  loadingContent.value = true;
  try {
    const res = await axios.get(`/api/v1/query/documents/${docId}/content`);
    selectedDocContent.value = res.data.content;
  } catch (err) {
    console.error("Error fetching doc content:", err);
    selectedDocContent.value = "Erreur lors de la lecture du document.";
  } finally {
    loadingContent.value = false;
  }
};

const openUploadModal = () => {
  uploadFile.value = null;
  uploadError.value = '';
  showUploadModal.value = true;
};

const onFileChange = (e) => {
  if (e.target.files.length > 0) {
    uploadFile.value = e.target.files[0];
  }
};

const handleUpload = async () => {
  if (!uploadFile.value) {
    uploadError.value = "Veuillez sélectionner un fichier.";
    return;
  }
  
  uploading.value = true;
  uploadError.value = '';
  
  const formData = new FormData();
  formData.append('file', uploadFile.value);
  formData.append('department', uploadDept.value);
  formData.append('uploaded_by', user.value.username || 'admin');
  
  try {
    await axios.post('/api/v1/ingest', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${localStorage.getItem('token')}`
      }
    });
    
    showUploadModal.value = false;
    await fetchDocs();
  } catch (err) {
    console.error("Upload error:", err);
    uploadError.value = err.response?.data?.detail || "Erreur de téléversement.";
  } finally {
    uploading.value = false;
  }
};

const handleDocDelete = (docId, title) => {
  confirmModal.value = {
    show: true,
    message: `Voulez-vous vraiment supprimer définitivement le document "${title}" ? Cette action est irréversible et reconstruira l'index de recherche.`,
    onConfirm: async () => {
      confirmModal.value.show = false;
      try {
        await axios.delete(`/api/v1/ingest/documents/${docId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        });
        await fetchDocs();
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

onMounted(() => {
  fetchDocs();
});

const filteredDocs = computed(() => {
  return docsList.value.filter(doc => {
    const matchesSearch = doc.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          doc.author.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchesDept = selectedDept.value === 'Tous' || doc.dept === selectedDept.value;
    return matchesSearch && matchesDept;
  });
});
</script>

<template>
  <div class="space-y-6">
    <!-- Header Block with Catalog Trigger (Visible for Admin & Expert) -->
    <div class="bg-gradient-to-r from-white to-slate-50 p-6 rounded-3xl border border-slate-200/50 shadow-[0_8px_30px_rgba(99,102,241,0.015)] backdrop-blur-xl flex justify-between items-center flex-wrap gap-4">
      <div>
        <h1 class="text-2xl font-extrabold text-slate-900 tracking-tight">Base de connaissances</h1>
        <p class="text-slate-500 text-sm mt-2 font-medium">Recherche sémantique, exploration du graphe de relations et requêtage RAG.</p>
      </div>
      
      <!-- Catalogue trigger button -->
      <button 
        v-if="role !== 'Reader'"
        @click="showCatalogModal = true"
        class="px-5 py-3 bg-indigo-600 hover:bg-indigo-550 text-white rounded-2xl text-sm font-bold shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/20 transition-all flex items-center space-x-2 cursor-pointer border-none shrink-0"
      >
        <FolderOpen class="h-4.5 w-4.5" />
        <span>Afficher le catalogue</span>
      </button>
    </div>

    <!-- Main Workspace: Chatbot ONLY (Centered ChatGPT-like layout) -->
    <div class="max-w-4xl mx-auto w-full">
      <RAGChatbot />
    </div>

    <!-- Document Catalog Modal (Admin/Expert only) -->
    <div v-if="showCatalogModal && role !== 'Reader'" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-40 p-4">
      <div class="bg-white border border-slate-200/80 p-6 rounded-3xl w-full max-w-4xl shadow-2xl relative flex flex-col max-h-[85vh]">
        <button @click="showCatalogModal = false" class="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition cursor-pointer">
          <X class="h-4 w-4" />
        </button>

        <div class="flex flex-col flex-1 overflow-hidden space-y-6">
          <div class="flex items-center justify-between border-b border-slate-105 pb-3 mt-2">
            <h3 class="font-extrabold text-slate-800 text-base flex items-center space-x-2">
              <FolderOpen class="h-5.5 w-5.5 text-indigo-600" />
              <span>Catalogue de Documents</span>
            </h3>
            <div class="flex items-center space-x-3">
              <span class="text-[10px] text-slate-400 font-bold font-mono uppercase">{{ filteredDocs.length }} documents</span>
              <!-- Upload Button for Admin & Expert only -->
              <button 
                v-if="role === 'Admin' || role === 'Expert'"
                @click="openUploadModal"
                class="px-3.5 py-2 bg-indigo-600 hover:bg-indigo-550 text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 cursor-pointer border-none shadow-sm"
              >
                <Plus class="h-3.5 w-3.5" />
                <span>Importer</span>
              </button>
            </div>
          </div>

          <!-- Search Bar -->
          <div class="relative shrink-0">
            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400 pointer-events-none z-10">
              <Search class="h-4.5 w-4.5" />
            </span>
            <InputText 
              v-model="searchQuery" 
              placeholder="Rechercher par titre ou auteur..." 
              class="w-full! pl-10! pr-4! py-2.5! bg-slate-50! border-slate-200! rounded-2xl! focus:border-indigo-500! focus:bg-white! outline-none! text-sm! text-slate-800! transition-all! font-medium! placeholder:text-slate-400!"
            />
          </div>

          <!-- Department Filters -->
          <div class="flex flex-wrap gap-2 shrink-0">
            <Button 
              v-for="dept in departments" 
              :key="dept" 
              @click="selectedDept = dept"
              :class="selectedDept === dept 
                      ? 'px-3.5! py-1.5! rounded-full! text-xs! font-bold! bg-indigo-600! text-white! shadow-sm! shadow-indigo-600/10! border-none! cursor-pointer!' 
                      : 'px-3.5! py-1.5! rounded-full! text-xs! font-bold! bg-slate-50! text-slate-500! hover:bg-slate-100! border-slate-200/50! border! cursor-pointer!'"
            >
              <span>{{ dept }}</span>
            </Button>
          </div>

          <!-- Document List -->
          <div class="flex-1 overflow-y-auto pr-1 space-y-3.5 min-h-[300px]">
            <div v-for="doc in filteredDocs" :key="doc.id" 
                 class="p-4 rounded-2xl border border-slate-200/60 bg-slate-50/20 hover:bg-slate-50/80 transition-all duration-200 flex justify-between items-center group">
              <div class="flex items-center space-x-3.5 min-w-0">
                <div class="h-10 w-10 rounded-xl bg-indigo-50 border border-indigo-100/30 flex items-center justify-center shrink-0">
                  <FileText class="h-5 w-5 text-indigo-600" />
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-bold text-slate-800 truncate">{{ doc.title }}</p>
                  <div class="flex items-center space-x-3 text-[10px] text-slate-450 font-semibold font-mono mt-1 flex-wrap gap-y-1">
                    <span class="flex items-center space-x-1">
                      <Tag class="h-3 w-3 text-slate-400" />
                      <span>{{ doc.dept }}</span>
                    </span>
                    <span class="flex items-center space-x-1">
                      <Calendar class="h-3 w-3 text-slate-400" />
                      <span>{{ doc.date }}</span>
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="flex items-center space-x-3.5 shrink-0">
                <span class="bg-indigo-50 text-indigo-700 text-[8px] font-bold font-mono tracking-wider uppercase px-2 py-0.5 rounded border border-indigo-250/20">
                  {{ doc.author }}
                </span>
                
                <!-- Quick Action Icons -->
                <div class="flex items-center space-x-1.5 pl-2">
                  <!-- Eye icon (Read) -->
                  <button 
                    @click="openViewDoc(doc.id, doc.title)"
                    title="Lire le document"
                    class="p-1.5 text-indigo-600 hover:bg-indigo-50 rounded-lg transition border border-slate-200/40 cursor-pointer"
                  >
                    <Eye class="h-3.5 w-3.5" />
                  </button>
                  
                  <!-- Trash icon (Delete) for Admin/Expert -->
                  <button 
                    v-if="role === 'Admin' || role === 'Expert'"
                    @click="handleDocDelete(doc.id, doc.title)"
                    title="Supprimer le document"
                    class="p-1.5 text-rose-600 hover:bg-rose-50 rounded-lg transition border border-slate-200/40 cursor-pointer"
                  >
                    <Trash2 class="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
            </div>
            <div v-if="filteredDocs.length === 0" class="text-slate-450 font-medium text-center py-12">Aucun document ne correspond à vos critères.</div>
          </div>
        </div>

        <div class="flex items-center justify-end pt-3 border-t border-slate-100 mt-4 shrink-0">
          <button @click="showCatalogModal = false" class="px-5 py-2.5 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition cursor-pointer">
            Fermer
          </button>
        </div>
      </div>
    </div>

    <!-- Document Viewer Modal (Higher z-index layer) -->
    <div v-if="showViewModal" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white border border-slate-200/80 p-6 rounded-3xl w-full max-w-2xl shadow-2xl relative flex flex-col max-h-[85vh]">
        <button @click="showViewModal = false" class="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-700 transition cursor-pointer">
          <X class="h-4 w-4" />
        </button>

        <div class="flex items-center space-x-3 mb-4 pb-3 border-b border-slate-100">
          <div class="h-10 w-10 rounded-xl bg-indigo-50 border border-indigo-100 flex items-center justify-center shrink-0">
            <FileText class="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h3 class="font-extrabold text-slate-800 text-sm truncate max-w-md">{{ selectedDocTitle }}</h3>
            <p class="text-[10px] text-slate-400 font-medium font-mono uppercase">Contenu extrait</p>
          </div>
        </div>

        <!-- Scrollable text content -->
        <div class="flex-1 overflow-y-auto pr-1 bg-slate-50 border border-slate-200/60 rounded-2xl p-4 text-xs text-slate-700 leading-relaxed whitespace-pre-wrap font-medium">
          <div v-if="loadingContent" class="flex flex-col items-center justify-center py-20 space-y-3">
            <span class="h-2 w-2 rounded-full bg-indigo-600 animate-ping"></span>
            <span class="text-slate-400 font-bold font-mono">Chargement du contenu...</span>
          </div>
          <template v-else>
            {{ selectedDocContent }}
          </template>
        </div>

        <div class="flex items-center justify-end pt-3 border-t border-slate-100 mt-4">
          <button @click="showViewModal = false" class="px-5 py-2.5 text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition cursor-pointer">
            Fermer
          </button>
        </div>
      </div>
    </div>

    <!-- Document Import Modal (Higher z-index layer) -->
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
            <label class="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-2 font-mono">Sélectionner le fichier</label>
            <input 
              type="file" 
              @change="onFileChange" 
              accept=".pdf,.docx,.txt"
              class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer" 
              required
            />
          </div>

          <div>
            <label class="block text-[9px] font-bold text-slate-500 uppercase tracking-wider mb-2 font-mono">Département concerné</label>
            <select v-model="uploadDept" class="w-full px-3.5 py-2.5 bg-slate-55/10 border border-slate-200 rounded-xl text-xs text-slate-700 font-semibold outline-none focus:border-indigo-500 transition-all">
              <option v-for="dept in uploadDepartments" :key="dept" :value="dept">{{ dept }}</option>
            </select>
          </div>

          <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-100 mt-6">
            <button type="button" @click="showUploadModal = false" class="px-4 py-2 text-xs font-bold text-slate-500 hover:bg-slate-100 rounded-xl transition cursor-pointer">
              Annuler
            </button>
            <button type="submit" :disabled="uploading" class="px-4 py-2 text-xs font-bold bg-indigo-600 hover:bg-indigo-550 text-white rounded-xl shadow-md shadow-indigo-600/10 transition cursor-pointer">
              {{ uploading ? 'Ingestion...' : 'Téléverser' }}
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
</div>
</template>
