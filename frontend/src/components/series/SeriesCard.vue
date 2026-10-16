<script setup lang="ts">
import { useClub } from '@/composables/useClub'
import type { Series } from '@/types/club'
defineProps<{ s: Series }>()
const { average, votes, open, save, busy } = useClub()
const percent = (s: Series) => s.episode_count ? Math.round(votes(s.id) / s.episode_count * 100) : 0
async function favorite(s: Series) { await save('favorites', {id:s.id, favorite:!s.favorite}) }
</script>
<template>        <article class="collection-card">
          <div class="collection-cover" :style="{background:s.color}"><button class="cover-open" :aria-label="'Abrir '+s.title" @click="open('detail',s)"><img v-if="s.image_url" :src="s.image_url" alt="" loading="lazy" decoding="async" width="210" height="295" /><span v-else class="cover-fallback">{{ s.title }}</span></button><span class="collection-status" :class="{'status-done':s.status==='Terminada','status-pending':s.status==='Pendiente'}">{{ s.status }}</span><button class="favorite-toggle" :class="{favorited:s.favorite}" :disabled="busy" :aria-label="(s.favorite?'Quitar de favoritas: ':'Agregar a favoritas: ')+s.title" :aria-pressed="!!s.favorite" @click="favorite(s)">{{ s.favorite?'♥':'♡' }}</button></div>
          <div class="collection-card-body"><button class="collection-title" @click="open('detail',s)">{{ s.title }}</button><div class="collection-progress"><progress :value="votes(s.id)" :max="s.episode_count || 1" :class="{complete:percent(s)===100}" aria-label="Progreso de puntuaciones" /><span>{{ percent(s) }}%</span></div><small>{{ votes(s.id) }} / {{ s.episode_count || '—' }} capítulos puntuados</small><div class="collection-card-bottom"><span>★ <strong>{{ votes(s.id)?average(s.id).toFixed(1):'—' }}</strong><small> / 5</small></span><button :aria-label="'Ver capítulos de '+s.title" @click="open('detail',s)">Ver detalles ›</button></div></div>
        </article></template>