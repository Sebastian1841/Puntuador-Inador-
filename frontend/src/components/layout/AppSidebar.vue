<script setup lang="ts">
import UiIcon from './UiIcon.vue'
import { useClub } from '@/composables/useClub'
const { page, navigate } = useClub()
function browse() { navigate('Biblioteca') }
</script>
<template>
  <aside class="sidebar dashboard-sidebar">
    <a class="brand brand-emblem" href="#/biblioteca" aria-label="Puntuador-inador · Inicio" @click.prevent="browse()"><img src="/puntuador-mascots-v3.png" alt="Puntuador-inador" width="500" height="500" /></a>
    <nav aria-label="Navegación principal">
      <button :class="{active:page==='Biblioteca'}" @click="browse()"><UiIcon name="home" />Inicio</button>
      <button :class="{active:page==='Coleccion'}" @click="navigate('Coleccion')"><UiIcon name="book" />Mi colección</button>
      <button :class="{active:page==='Ranking'}" @click="navigate('Ranking')"><UiIcon name="chart" />Ranking</button>
      <button :class="{active:page==='Configuracion'}" @click="navigate('Configuracion')"><UiIcon name="settings" />Configuración</button>
    </nav>
    </aside>
</template>
