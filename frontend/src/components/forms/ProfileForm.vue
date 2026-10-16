<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { Profile } from '@/types/club'
import { useClub } from '@/composables/useClub'
const { data, activeProfile, profileForm, changeProfile, deleteProfile, busy } = useClub()
const profilePage = ref(0)
const pageCount = computed(() => Math.ceil(data.profiles.length / 3))
const visibleProfiles = computed(() => data.profiles.slice(profilePage.value * 3, profilePage.value * 3 + 3))
watch(() => profileForm.targetId, id => { const index = data.profiles.findIndex(p => p.id === id); if (index >= 0) profilePage.value = Math.floor(index / 3) }, { immediate: true })
function selectProfile(event: Event) { const profile = data.profiles.find(p => p.id === Number((event.target as HTMLSelectElement).value)); if (profile) configure('edit', profile) }
const fileInput = ref<HTMLInputElement | null>(null)
const deleting = ref<Profile | null>(null)
const imageError = ref(''), dragging = ref(false)
const colors = ['#FF6600', '#102372', '#2563EB', '#7C3AED', '#DB2777', '#14866D', '#475569']
const previewProfile = computed(() => profileForm.mode === 'edit' ? data.profiles.find(p => p.id === profileForm.targetId) : undefined)
const initials = computed(() => profileForm.name.trim().slice(0, 2).toUpperCase() || 'TU')
function configure(mode: string, target?: Profile) {
  imageError.value = ''; deleting.value = null
  const profile = mode === 'edit' ? (target || activeProfile.value) : undefined
  Object.assign(profileForm, { mode, targetId: profile?.id || 0, name: profile?.name || '', color: profile?.color || '#FF6600', avatar: profile?.avatar || '', description: profile?.description || '' })
}
async function upload(file?: File) {
  if (!file || busy.value || profileForm.processing) return
  imageError.value = ''
  if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type) || file.size > 2 * 1024 * 1024) {
    imageError.value = 'Elige una imagen JPG, PNG o WebP de hasta 2 MB.'; return
  }
  profileForm.processing = true
  const url = URL.createObjectURL(file)
  try {
    const image = new Image()
    image.src = url
    await image.decode()
    if (image.naturalWidth * image.naturalHeight > 16_000_000) throw new Error()
    const canvas = document.createElement('canvas')
    canvas.width = canvas.height = 256
    const context = canvas.getContext('2d')
    if (!context) throw new Error()
    const size = Math.min(image.naturalWidth, image.naturalHeight)
    context.fillStyle = '#ffffff'; context.fillRect(0, 0, 256, 256)
    context.drawImage(image, (image.naturalWidth-size)/2, (image.naturalHeight-size)/2, size, size, 0, 0, 256, 256)
    profileForm.avatar = canvas.toDataURL('image/jpeg', 0.9)
  } catch { imageError.value = 'No pudimos leer esa imagen. Prueba otra de menor resolución.' }
  finally { URL.revokeObjectURL(url); profileForm.processing = false }
}
function choose(event: Event) {
  const input = event.target as HTMLInputElement
  void upload(input.files?.[0]); input.value = ''
}
function drop(event: DragEvent) { dragging.value = false; void upload(event.dataTransfer?.files[0]) }
</script>
<template>
  <p class="profile-intro">Administra tus perfiles. Cada perfil tiene su propia colección, puntuaciones, favoritos y notas.</p>
  <div class="profile-workspace">
    <aside class="profile-switcher" aria-label="Tus perfiles">
      <button type="button" class="profile-new-button" :disabled="busy || profileForm.processing" @click="configure('create')">＋ Crear nuevo perfil</button>
      <div class="profile-mobile-selector"><label for="profile-select-mobile">Seleccionar perfil</label><select id="profile-select-mobile" :value="profileForm.targetId" :disabled="busy || profileForm.processing" @change="selectProfile"><option disabled value="0">Nuevo perfil</option><option v-for="profile in data.profiles" :key="profile.id" :value="profile.id">{{ profile.name }}{{ profile.id===activeProfile?.id?' · Activo':'' }}</option></select><button v-if="previewProfile && previewProfile.id!==activeProfile?.id" type="button" :disabled="busy || profileForm.processing" @click="changeProfile(previewProfile.id)">Usar este perfil</button></div>
      <div class="profile-switcher-list">
        <article v-for="profile in visibleProfiles" :key="profile.id" class="profile-switch-card" :class="{selected:profileForm.mode==='edit' && profileForm.targetId===profile.id}">
          <button type="button" class="profile-select" :disabled="busy || profileForm.processing" :aria-pressed="profileForm.mode==='edit' && profileForm.targetId===profile.id" @click="configure('edit',profile)">
            <span class="profile-switch-avatar" :style="{background:profile.color}"><img v-if="profile.avatar" :src="profile.avatar" alt="" /><template v-else>{{ profile.name.slice(0,2).toUpperCase() }}</template></span>
            <span><strong>{{ profile.name }}</strong><small :class="{'profile-active-label':profile.id===activeProfile?.id}">{{ profile.id===activeProfile?.id?'● Perfil activo':'Editar perfil' }}</small></span>
          </button>
          <div class="profile-switch-stats"><span><strong>{{ profile.series_count || 0 }}</strong>Series</span><span><strong>{{ profile.favorites_count || 0 }}</strong>Favoritas</span><span><strong>{{ profile.rated_count || 0 }}</strong>Puntuados</span></div>
          <button v-if="profile.id!==activeProfile?.id" type="button" class="profile-switch-use" :disabled="busy || profileForm.processing" @click="changeProfile(profile.id)">Cambiar a este perfil →</button>
        </article>
      </div>
      <div v-if="pageCount>1" class="profile-pagination"><button type="button" :disabled="profilePage===0" aria-label="Perfiles anteriores" @click="profilePage--">‹</button><span>{{ profilePage+1 }} / {{ pageCount }}</span><button type="button" :disabled="profilePage>=pageCount-1" aria-label="Perfiles siguientes" @click="profilePage++">›</button></div>
    </aside>
    <div class="profile-workspace-main">
      <div class="profile-edit-heading"><div><h3>{{ profileForm.mode==='create'?'Crear nuevo perfil':'Editar perfil' }}</h3><p>{{ profileForm.mode==='create'?'Un nuevo espacio para tus series.':'Personaliza este perfil.' }}</p></div><button v-if="previewProfile" type="button" class="profile-delete-action" :disabled="busy || profileForm.processing || data.profiles.length===1" :title="data.profiles.length===1?'Debes conservar al menos un perfil':''" @click="deleting=previewProfile">Eliminar perfil</button></div>
  <div v-if="deleting" class="profile-delete-confirm" role="alert">
    <strong>¿Eliminar el perfil de {{ deleting.name }}?</strong>
    <p>Se eliminarán su colección personal, puntuaciones, favoritas, notas y foto. Los demás perfiles conservarán sus datos. Esta acción no se puede deshacer.</p>
    <button type="button" :disabled="busy" @click="deleting=null">Cancelar</button>
    <button type="button" class="profile-delete-button" :disabled="busy" @click="deleteProfile(deleting.id)">{{ busy?'Eliminando…':'Sí, eliminar perfil' }}</button>
  </div>
  <fieldset v-if="!deleting" class="profile-fields" :disabled="busy || profileForm.processing">

    <div class="profile-editor">
      <aside class="profile-preview" :style="{'--profile-color':profileForm.color}">
        <span class="profile-preview-label">VISTA PREVIA</span>
        <div class="profile-avatar-wrap"><div class="profile-preview-avatar"><img v-if="profileForm.avatar" :src="profileForm.avatar" alt="Vista previa de tu foto" /><span v-else>{{ initials }}</span></div><button type="button" class="profile-camera" aria-label="Cambiar foto de perfil" @click="fileInput?.click()"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5 10 3h4l2 2h4v15H4V5h4Z"/><circle cx="12" cy="12" r="4"/></svg></button></div>
        <strong>{{ profileForm.name.trim() || 'Tu nombre' }}</strong><span v-if="previewProfile?.id===activeProfile?.id" class="profile-active-label">● Perfil activo</span><small>Tu próxima historia empieza aquí</small>
        <div class="profile-preview-stats">
          <div><span>▣</span><p><strong>{{ previewProfile?.series_count || 0 }}</strong><small>Series en la colección</small></p></div>
          <div><span>☆</span><p><strong>{{ previewProfile?.favorites_count || 0 }}</strong><small>Favoritas</small></p></div>
          <div><span>◷</span><p><strong>{{ previewProfile?.rated_count || 0 }}</strong><small>Capítulos puntuados</small></p></div>
          <div><span>☷</span><p><strong>{{ previewProfile?.pending_count || 0 }}</strong><small>En espera</small></p></div>
        </div>
      </aside>
      <div class="profile-details">
        <h3>Información del perfil</h3>
        <label for="profile-name">Nombre del perfil <span class="required">*</span></label>
        <input id="profile-name" v-model="profileForm.name" required maxlength="40" placeholder="Tu nombre o apodo" autocomplete="nickname" />
        <small class="profile-help">Así te saludaremos al entrar. {{ profileForm.name.length }}/40</small>
        <label for="profile-description">Descripción <small>(opcional)</small></label>
        <div class="profile-description"><textarea id="profile-description" v-model="profileForm.description" maxlength="120" placeholder="Tu rincón personal para llevar el control de tus series." /><small>{{ profileForm.description.length }}/120</small></div>
        <label>Imagen de perfil <small>(opcional)</small></label>
        <div class="profile-upload" :class="{dragging}" @dragover.prevent="dragging=true" @dragleave.prevent="dragging=false" @drop.prevent="drop">
          <input ref="fileInput" class="profile-file-input" type="file" accept="image/jpeg,image/png,image/webp" aria-label="Seleccionar foto de perfil" @change="choose" />
          <button type="button" class="profile-upload-button" @click="fileInput?.click()">{{ profileForm.processing?'Preparando foto…':profileForm.avatar?'Cambiar foto':'＋ Subir una foto' }}</button>
          <img v-if="profileForm.avatar" class="profile-upload-thumbnail" :src="profileForm.avatar" alt="Foto seleccionada" />
          <small>O arrástrala aquí · JPG, PNG o WebP · Máx. 2 MB</small>

          <button v-if="profileForm.avatar" class="profile-remove" type="button" @click="profileForm.avatar=''">Quitar foto</button>
        </div>
        <p v-if="imageError" class="error" role="alert">{{ imageError }}</p>
        <label>Color del perfil</label>
        <div class="profile-colors"><button v-for="color in colors" :key="color" type="button" :style="{background:color}" :aria-label="`Color ${color}`" :aria-pressed="profileForm.color.toUpperCase()===color" @click="profileForm.color=color">{{ profileForm.color.toUpperCase()===color?'✓':'' }}</button><input v-model="profileForm.color" type="color" aria-label="Elegir un color personalizado" /></div>
      </div>
    </div>
  </fieldset>
    </div>
  </div>
</template>
