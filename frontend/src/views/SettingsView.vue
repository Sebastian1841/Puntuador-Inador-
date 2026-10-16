<script setup lang="ts">
import AccountSettings from '@/components/forms/AccountSettings.vue'
import { onMounted } from 'vue'
import SettingsForm from '@/components/forms/SettingsForm.vue'
import { useClub } from '@/composables/useClub'
const { data, prefs, save, busy, open, profileScreen }=useClub()
onMounted(()=>{Object.assign(prefs,data.settings); if(new URLSearchParams(location.hash.split('?')[1]).get('seccion')==='perfiles')document.getElementById('perfiles')?.scrollIntoView({block:'start'})})
function profiles(){open('profiles');profileScreen.value='manage'}
</script>
<template><div class="settings-page"><h1>Configuración</h1><AccountSettings /><form @submit.prevent="save('settings',prefs)"><SettingsForm /><button class="primary" :disabled="busy">{{busy?'Guardando…':'Guardar configuración'}}</button></form><section id="perfiles"><h2>Perfiles</h2><p>Cada perfil tiene su colección, favoritos y puntuaciones.</p><div class="settings-profiles"><button v-for="p in data.profiles" :key="p.id" @click="profiles"><img v-if="p.avatar" :src="p.avatar" alt="" /><span v-else :style="{background:p.color}" class="settings-avatar">{{p.name.slice(0,2)}}</span><strong>{{p.name}}</strong><small v-if="p.id===data.active_profile_id">Activo</small></button></div><button class="outline" @click="profiles">Administrar perfiles</button></section></div></template>
