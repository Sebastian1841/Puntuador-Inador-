<script setup lang="ts">
import { useClub } from '@/composables/useClub';
import { watch, onUnmounted } from 'vue';
import SeriesForm from '@/components/forms/SeriesForm.vue';
import ProfilePicker from '@/components/forms/ProfilePicker.vue';
import ProfileForm from '@/components/forms/ProfileForm.vue';
const { modal, error, busy, form, profileForm, profileScreen, submit } = useClub();
function close() { if (!busy.value && !profileForm.processing) modal.value = '' }
let previousOverflow: string | undefined;
function restoreScroll() {
  if (previousOverflow !== undefined) {
    document.body.style.overflow = previousOverflow;
    previousOverflow = undefined;
  }
}
watch(modal, value => {
  if (value && previousOverflow === undefined) {
    previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
  } else if (!value) restoreScroll();
}, { flush: 'sync' });
onUnmounted(restoreScroll);
</script>

<template>
<div v-if="modal" class="modal-backdrop" @click.self="close" @keydown.esc="close">
    <section class="modal" :class="{'series-add-modal':modal==='series', 'profile-modal':modal==='profiles', 'profile-picker-modal':modal==='profiles' && profileScreen!=='editor', 'profile-single-editor':modal==='profiles' && profileScreen==='editor'}" role="dialog" aria-modal="true" aria-labelledby="modal-title">
<button class="close" aria-label="Cerrar" :disabled="busy || profileForm.processing" @click="close">×</button>
<div v-if="modal!=='series'" class="eyebrow">{{ modal==='profiles'?'PERFILES':'TU CLUB, TUS REGLAS' }}</div>
<h2 id="modal-title">{{modal==='series'?'Agregar serie':modal==='profiles'?(profileScreen==='select'?'¿Quién está viendo?':profileScreen==='manage'?'Administrar perfiles':profileForm.mode==='create'?'Crear nuevo perfil':'Editar perfil'):'Hazlo tuyo'}}</h2>
      <form @submit.prevent="submit">
        <SeriesForm v-if="modal==='series'" />
        <ProfilePicker v-if="modal==='profiles' && profileScreen!=='editor'" />
        <ProfileForm v-if="modal==='profiles' && profileScreen==='editor'" />
        <p v-if="error" class="error" role="alert">{{error}}</p>
<div v-if="modal!=='profiles' || profileScreen==='editor'" :class="{'profile-dialog-footer':modal==='profiles', 'series-dialog-footer':modal==='series'}"><button v-if="modal==='profiles'" type="button" class="outline profile-cancel" :disabled="busy || profileForm.processing" @click="profileScreen='select'; error=''">Volver a perfiles</button>
<button v-if="modal==='series'" type="button" class="outline" :disabled="busy" @click="close">Cancelar</button>
<button class="primary save" :disabled="busy || (modal === 'profiles' && (profileForm.processing || !profileForm.name.trim())) || (modal === 'series' && !form.title.trim())">{{busy?'Guardando…':modal==='profiles'?(profileForm.mode==='create'?'Crear perfil':'Guardar cambios'):modal==='series'?'＋ Agregar serie':'Guardar'}}</button></div>
      </form>
    </section>
  </div>
</template>
