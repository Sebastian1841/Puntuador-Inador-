<script setup lang="ts">
import UiIcon from '@/components/layout/UiIcon.vue'
import { ref } from 'vue'
import { useClub } from '@/composables/useClub'
const { data, open } = useClub()
const allUpcoming = ref(false), allActivity = ref(false)
function details(id: number) { const series = data.series.find(s => s.id===id); if(series) open('detail',series) }
function date(value: string) { return new Intl.DateTimeFormat('es-CL', {day:'numeric',month:'short'}).format(new Date(value.length===10?value+'T12:00:00':value)) }
</script>
<template>
  <section class="home-side-panel" aria-labelledby="upcoming-title"><div class="home-panel-heading"><h2 id="upcoming-title"><UiIcon name="calendar" /> Próximos capítulos</h2><button v-if="data.dashboard.upcoming.length>4" @click="allUpcoming=!allUpcoming">{{ allUpcoming?'Ver menos':'Ver todos' }} ›</button></div>
    <div v-if="!data.dashboard.upcoming.length" class="home-panel-empty"><UiIcon name="calendar" /><strong>Sin próximas fechas</strong><p>Aquí aparecerán las fechas anunciadas de los capítulos que hayas importado.</p></div>
    <div v-else class="home-panel-list"><button v-for="episode in data.dashboard.upcoming.slice(0,allUpcoming?20:4)" :key="episode.id" class="home-panel-item" @click="details(episode.series_id)"><img v-if="episode.image_url" :src="episode.image_url" alt="" loading="lazy" /><span class="home-panel-item-copy"><strong>{{ episode.series_title }}</strong><small>T{{ episode.season }} · Episodio {{ episode.number }}</small><small class="home-episode-name">{{ episode.title }}</small></span><time :datetime="episode.airdate">{{ date(episode.airdate) }}</time></button></div>
  </section>
  <section class="home-side-panel" aria-labelledby="activity-title"><div class="home-panel-heading"><h2 id="activity-title"><UiIcon name="activity" /> Actividad reciente</h2><button v-if="data.dashboard.activity.length>4" @click="allActivity=!allActivity">{{ allActivity?'Ver menos':'Ver toda' }} ›</button></div>
    <div v-if="!data.dashboard.activity.length" class="home-panel-empty"><UiIcon name="activity" /><strong>Tu historia empieza aquí</strong><p>Las series que agregues y los capítulos que puntúes aparecerán en este espacio.</p></div>
    <div v-else class="home-panel-list"><button v-for="item in data.dashboard.activity.slice(0,allActivity?20:4)" :key="item.id" class="home-panel-item activity-item" @click="details(item.series_id)"><img v-if="item.image_url" :src="item.image_url" alt="" loading="lazy" /><span class="home-panel-item-copy"><span>{{ item.kind==='rated'?'Puntuaste un capítulo de':item.kind==='added'?'Añadiste':item.detail==='Terminada'?'Terminaste':'Actualizaste' }} <strong>{{ item.title }}</strong></span><small v-if="item.kind==='rated'" class="home-activity-score">★ {{ item.detail }} / 5</small><small v-else-if="item.kind==='status'">{{ item.detail }}</small><time :datetime="item.created_at">{{ date(item.created_at) }}</time></span></button></div>
  </section>
</template>
