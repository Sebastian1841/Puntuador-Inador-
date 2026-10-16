<script setup lang="ts">
import { computed, ref } from 'vue'
import { useClub } from '@/composables/useClub'
import type { Profile } from '@/types/club'
const { data, activeProfile, profileForm, profileScreen, changeProfile, busy, error } = useClub()
const page = ref(0)
const pages = computed(() => Math.max(1, Math.ceil(data.profiles.length / 5)))
const profiles = computed(() => data.profiles.slice(page.value * 5, page.value * 5 + 5))
function edit(profile?: Profile) {
  error.value = ''
  Object.assign(profileForm, { mode: profile ? 'edit' : 'create', targetId: profile?.id || 0, name: profile?.name || '', avatar: profile?.avatar || '', description: profile?.description || '', color: profile?.color || '#FF6600', processing: false })
  profileScreen.value = 'editor'
}
function select(profile: Profile) {
  if (busy.value) return
  if (profileScreen.value === 'manage') edit(profile)
  else void changeProfile(profile.id)
}
</script>
<template>
  <img class="profile-picker-logo" src="/puntuador-mascots-v3.png" alt="Puntuador-inador" width="580" height="419" />
  <p class="picker-subtitle">{{ profileScreen==='manage'?'Elige un perfil para editar su nombre, foto o eliminarlo.':'Elige tu perfil y continúa con tus series.' }}</p>
  <div class="streaming-profiles" :aria-busy="busy">
    <button v-for="profile in profiles" :key="profile.id" type="button" class="streaming-profile" :disabled="busy" :aria-label="`${profileScreen==='manage'?'Editar':'Entrar como'} ${profile.name}`" @click="select(profile)">
      <span class="streaming-avatar" :style="{background:profile.color}"><img v-if="profile.avatar" :src="profile.avatar" alt="" /><span v-else>{{ profile.name.slice(0,2).toUpperCase() }}</span><span v-if="profileScreen==='manage'" class="streaming-edit" aria-hidden="true">✎</span></span>
      <strong>{{ profile.name }}</strong><small>{{ profile.id===activeProfile?.id?'Perfil actual':'Tu espacio personal' }}</small>
    </button>
    <button type="button" class="streaming-profile streaming-add" :disabled="busy" @click="edit()"><span class="streaming-avatar">＋</span><strong>Agregar perfil</strong><small>Un nuevo espacio para ti</small></button>
  </div>
  <nav v-if="pages>1" class="profile-pagination" aria-label="Páginas de perfiles"><button type="button" :disabled="busy || page===0" @click="page--">‹</button><span>{{ page+1 }} / {{ pages }}</span><button type="button" :disabled="busy || page>=pages-1" @click="page++">›</button></nav>
  <p v-if="busy" class="picker-subtitle" role="status">Abriendo tu colección…</p>
  <button type="button" class="streaming-manage" :disabled="busy" @click="profileScreen=profileScreen==='manage'?'select':'manage'; error=''">{{ profileScreen==='manage'?'Listo':'Administrar perfiles' }}</button>
</template>
