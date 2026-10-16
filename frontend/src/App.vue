<script setup lang="ts">
import { computed, onMounted, provide } from 'vue';
import { accentPalette } from './composables/accentPalette';
import { createClub, clubKey } from './composables/useClub';
import AppSidebar from './components/layout/AppSidebar.vue';
import ClubDialog from './components/dialogs/ClubDialog.vue';
import RecommendationsView from './views/RecommendationsView.vue';
import SettingsView from './views/SettingsView.vue';
import CollectionView from './views/CollectionView.vue';
import LibraryView from './views/LibraryView.vue';
import RankingView from './views/RankingView.vue';
import SeriesView from './views/SeriesView.vue';
const club = createClub();
provide(clubKey, club);
const { data, activeProfile, page, selected, loading, error, modal, load, open, navigate } = club;
const accentStyle = computed(() => accentPalette(page.value === 'Configuracion' ? club.prefs.accent : data.settings.accent));
onMounted(load);
</script>
<template>
<div class="app" :style="accentStyle">
  <div class="site-artwork" aria-hidden="true"><img src="/rooftop-trio-v4.png" alt="" fetchpriority="high" /><div class="site-artwork-shade"></div></div>
  <AppSidebar />
  <main>
    <div v-if="error&&!modal" class="error" role="alert">{{error}} <button @click="load">Reintentar</button>
</div>
    <section class="content" :class="{ 'series-content': page === 'Serie' }">
      <div v-if="page === 'Ranking'" class="page-heading">
<div>
<div class="eyebrow">EL RITUAL DESPUÉS DE LOS CRÉDITOS</div>
<h1>Tus mejores capítulos.</h1>
<p>Puntúa cada episodio de media en media estrella.</p>
</div>
<button class="primary" @click="open('series')">＋ Agregar serie</button>
</div>
      <LibraryView v-if="page==='Biblioteca'" />
      <CollectionView v-else-if="page==='Coleccion'" />
      <RecommendationsView v-else-if="page==='Recomendaciones'" />
      <SettingsView v-else-if="page==='Configuracion'" />
      <RankingView v-else-if="page==='Ranking'" />
      <SeriesView v-else-if="selected" :key="`${selected.id}:${activeProfile?.id}`" />
      <p v-else-if="loading" role="status">Cargando serie…</p>
      <div v-else class="empty"><h2>No encontramos esa serie</h2><button class="outline" @click="navigate('Biblioteca')">Volver a la colección</button></div>

    </section>
  </main>
  <ClubDialog />
</div>
</template>
