<script setup lang="ts">
import UiIcon from '@/components/layout/UiIcon.vue'
import DashboardPanels from '@/components/layout/DashboardPanels.vue'
import HomeRecommendations from '@/components/series/HomeRecommendations.vue'
import SeriesCard from '@/components/series/SeriesCard.vue'
import { computed } from 'vue'
import { useClub } from '@/composables/useClub'
import type { Series } from '@/types/club'
const { data, activeProfile, votes, open, navigate } = useClub()
const featured=computed(()=>data.series.find(s=>s.status==='Viendo')??data.series[0])
const following=computed(()=>data.series.filter(s=>s.status==='Viendo').slice(0,4))
const counts=computed(()=>({active:data.series.filter(s=>s.status==='Viendo').length,pending:data.series.filter(s=>s.status==='Pendiente').length,favorite:data.series.filter(s=>s.favorite).length}))
const percent=(s:Series)=>s.episode_count?Math.round(votes(s.id)/s.episode_count*100):0
</script>
<template>
  <div class="dashboard-home home-screen">
    <div class="home-topbar"><button class="home-explore" @click="open('series')"><UiIcon name="search" /><span>Explorar series y anime</span><span aria-hidden="true">→</span></button><button class="home-user" @click="open('profiles')"><span class="home-user-avatar" :style="{background:activeProfile?.color}"><img v-if="activeProfile?.avatar" :src="activeProfile.avatar" alt="" /><span v-else>{{ activeProfile?.name.slice(0,2).toUpperCase() }}</span></span><strong>{{ activeProfile?.name }}</strong><span>⌄</span></button></div>
    <section class="dashboard-welcome"><div><h1>¡Hola, <span class="welcome-name">{{ activeProfile?.name || 'bienvenido' }}!</span></h1><p>Un capítulo más siempre es un buen plan.</p></div></section>
    <div class="home-overview">
    <section class="dashboard-feature" :class="{'feature-empty':!featured}">
      <img v-if="featured?.image_url" :src="featured.image_url" alt="" class="dashboard-feature-image" decoding="async" />
      <div class="dashboard-feature-shade" aria-hidden="true"></div>
      <div class="home-feature-heading"><strong>▷ {{ featured?.status==='Viendo'?'Continuar puntuando':'Tu próxima historia' }}</strong><button @click="navigate('Siguiendo')">Ver todas ›</button></div>
      <div class="home-feature-body"><img v-if="featured?.image_url" :src="featured.image_url" alt="" class="home-feature-poster" />
      <div class="dashboard-feature-copy"><div class="feature-eyebrow">{{ featured?.status==='Viendo'?'CONTINUAR PUNTUANDO':'TU PRÓXIMA HISTORIA' }}</div><h2>{{ featured?.title || 'Cada episodio merece su estrella.' }}</h2>
        <template v-if="featured"><div class="feature-meta"><span>{{ featured.status }}</span>{{ featured.original_title || featured.genre }}</div><p>{{ featured.description || 'Abre la serie y guarda lo que te pareció cada capítulo.' }}</p><div class="feature-progress"><progress :value="votes(featured.id)" :max="featured.episode_count || 1" aria-label="Capítulos puntuados" /><strong>{{ percent(featured) }}%</strong></div><small>{{ votes(featured.id) }} de {{ featured.episode_count || '—' }} capítulos puntuados</small><div class="feature-buttons"><button class="orange-button" @click="open('detail',featured)">▶ Continuar puntuando</button><button class="feature-secondary" @click="open('detail',featured)">☷ Ver detalles</button></div></template>
        <template v-else><p>Agrega tu primera serie y empieza tu registro personal, capítulo a capítulo.</p><button class="orange-button" @click="open('series')">＋ Agregar serie</button></template>
      </div></div>
    </section>
    <DashboardPanels />
    </div>
    <section class="dashboard-stats" aria-label="Resumen de mi perfil" :style="{'--stat-art':featured?.image_url ? `url(${featured.image_url})` : 'none'}">
      <button class="stat-blue" @click="navigate('Siguiendo')"><span class="stat-icon"><UiIcon name="play" /></span><span><small>Series en seguimiento</small><strong>{{ counts.active }}</strong><p>Que estás viendo ahora</p></span></button>
      <button class="stat-orange" @click="navigate('Pendientes')"><span class="stat-icon"><UiIcon name="clock" /></span><span><small>Pendientes</small><strong>{{ counts.pending }}</strong><p>En tu lista por ver</p></span></button>
      <div class="stat-purple"><span class="stat-icon"><UiIcon name="star" /></span><span><small>Capítulos puntuados</small><strong>{{ data.reviews.length }}</strong><p>Con tu calificación personal</p></span></div>
      <button class="stat-pink" @click="navigate('Favoritas')"><span class="stat-icon"><UiIcon name="heart" /></span><span><small>Favoritas</small><strong>{{ counts.favorite }}</strong><p>Tus series especiales</p></span></button>
    </section>
    <div class="home-shelves">
<section><header class="shelf-heading"><h2>Continuar viendo</h2><button @click="navigate('Siguiendo')">Ver todas →</button></header><div class="collection-grid"><SeriesCard v-for="s in following" :key="s.id" :s="s" /></div><p v-if="!following.length" class="empty">Las series que marques como «Viendo» aparecerán aquí.</p></section>
<HomeRecommendations />
</div>
  </div>
</template>
