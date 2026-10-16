<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import App from './App.vue'
import { apiRequest } from './services/http'
import { account, authEnabled } from './composables/useAccount'
const ready=ref(false),error=ref(''),busy=ref(false),username=ref(''),password=ref('')
const invitation=ref(new URLSearchParams(location.hash.split('?')[1]||'').get('invitacion')||'')
async function check(){error.value='';try{const state=await apiRequest<{enabled:boolean;account:typeof account.value}>('auth/me');authEnabled.value=state.enabled;account.value=state.account;ready.value=true}catch(e){error.value=(e as Error).message}}
async function submit(){busy.value=true;error.value='';try{await apiRequest(invitation.value?'auth/register':'auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:username.value,password:password.value,...(invitation.value?{invitation:invitation.value}:{})})});password.value='';invitation.value='';localStorage.removeItem('episodiario-profile');location.hash='#/inicio';await check()}catch(e){error.value=(e as Error).message}finally{busy.value=false}}
function expired(){if(authEnabled.value){account.value=null;localStorage.removeItem('episodiario-profile')}}
onMounted(()=>{check();window.addEventListener('session-expired',expired)})
onUnmounted(()=>window.removeEventListener('session-expired',expired))
</script>
<template><App v-if="ready && (!authEnabled || account)" :key="account?.id||0" /><main v-else class="account-gate"><form class="account-panel" @submit.prevent="submit"><img src="/puntuador-mascots-v3.png" alt="Puntuador-inador" /><h1>{{invitation?'Crea tu cuenta':'Bienvenido'}}</h1><p>{{invitation?'Tu invitación te da acceso a tu colección personal.':'Entra para continuar con tus series.'}}</p><template v-if="ready"><label>Usuario<input v-model="username" autocomplete="username" required minlength="3" maxlength="60" pattern="[a-zA-Z0-9_.-]+" /></label><label>Contraseña<input v-model="password" type="password" :autocomplete="invitation?'new-password':'current-password'" required minlength="12" maxlength="128" /></label><small>Mínimo 12 caracteres.</small><button :disabled="busy">{{busy?'Espera…':invitation?'Crear cuenta':'Entrar'}}</button></template><p v-else>Cargando acceso…</p><p v-if="error" role="alert">{{error}}</p><button v-if="!ready && error" type="button" @click="check">Reintentar conexión</button></form></main></template>
