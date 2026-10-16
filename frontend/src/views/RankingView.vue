<script setup lang="ts">
import { computed } from 'vue'
import { useClub } from '@/composables/useClub'
const { data, search, open } = useClub()
const ranked = computed(() => [...data.reviews].filter(r => {
  const series = data.series.find(s => s.id === r.series_id)
  return `${series?.title} ${r.episode_title}`.toLowerCase().includes(search.value.toLowerCase())
}).sort((a,b) => b.score-a.score || a.series_id-b.series_id || (a.season??0)-(b.season??0) || (a.number??0)-(b.number??0)))
function showSeries(id: number) { const series = data.series.find(s => s.id === id); if (series) open('detail', series) }
</script>
<template>
  <label class="search"><input v-model="search" placeholder="Buscar serie o capítulo…" aria-label="Buscar en el ranking" /></label>
  <p class="muted">Tus mejores capítulos, ordenados por puntuación.</p>
  <p v-if="!ranked.length" class="empty">Todavía no hay capítulos puntuados que coincidan. Abre una serie de tu biblioteca y valora sus episodios.</p>
  <div class="episode-list"><button v-for="(review,index) in ranked" :key="review.episode_id" class="episode-ranking" @click="showSeries(review.series_id)"><span>#{{ index+1 }}</span><span><strong>{{ review.episode_title }}</strong><small>{{ data.series.find(s=>s.id===review.series_id)?.title }} · T{{ review.season }} E{{ review.number }}</small></span><strong>★ {{ review.score.toFixed(1) }}</strong></button></div>
</template>
