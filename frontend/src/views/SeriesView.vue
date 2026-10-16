<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { useClub } from '@/composables/useClub'
import { useEpisodes } from '@/composables/useEpisodes'
import EpisodeRatingEditor from '@/components/episodes/EpisodeRatingEditor.vue'
const { selected, stars, navigate, data, save, busy } = useClub()
const { episodes, loading, saving, error, notice, season, current, score, comment, seasons, visible, rated, seasonAverage, load, choose, rate, add } = useEpisodes()
const manual = ref(false), number = ref(1), title = ref(''), query = ref('')
const tab = ref('Capítulos')
const filtered = computed(() => visible.value.filter(e => `${e.number} ${e.title}`.toLowerCase().includes(query.value.toLowerCase())))
const seasonRated = computed(() => visible.value.filter(e => e.score !== null).length)
const progress = computed(() => episodes.value.length ? Math.round(rated.value / episodes.value.length * 100) : 0)
const seasonProgress = computed(() => visible.value.length ? Math.round(seasonRated.value / visible.value.length * 100) : 0)
const average = computed(() => rated.value ? (episodes.value.reduce((sum,e) => sum + (e.score ?? 0), 0) / rated.value).toFixed(1) : '—')
const comments = computed(() => episodes.value.filter(e => e.comment?.trim()))
const nextEpisode = computed(() => episodes.value.find(e => e.score === null))
async function continueRating() {
  const episode = nextEpisode.value
  if (!episode) return
  tab.value = 'Capítulos'; season.value = episode.season; query.value = ''; choose(episode)
  await nextTick()
  document.getElementById(`episode-editor-${episode.id}`)?.scrollIntoView({ block: 'center', behavior: 'instant' })
}
async function addManual() {
  if (await add(number.value, title.value)) { manual.value = false; title.value = ''; number.value++ }
}
</script>

<template>
  <article v-if="selected" class="series-page">
    <section class="series-heading">
      <img v-if="selected.image_url" class="series-backdrop" :src="selected.image_url" alt="" decoding="async" />
      <div class="series-shade" aria-hidden="true"></div>
      <img v-if="selected.image_url" class="series-cover" :src="selected.image_url" :alt="'Portada de ' + selected.title" width="210" height="295" decoding="async" />
      <div v-else class="series-cover cover-placeholder" aria-hidden="true">◧</div>
      <div class="series-heading-copy">
        <div class="eyebrow">MI SEGUIMIENTO</div>
        <h1>{{ selected.title }}</h1>
        <strong v-if="selected.original_title && selected.original_title !== selected.title" class="series-original-title">{{ selected.original_title }}</strong>
        <p class="series-meta">{{ selected.genre }} · {{ selected.year }}</p>
        <p v-if="selected.description" class="series-synopsis">{{ selected.description }}</p>
        <div class="series-hero-actions">
          <button class="primary" :disabled="loading || saving || current !== null || !nextEpisode" @click="continueRating">▶ {{ nextEpisode ? 'Continuar puntuando' : 'Todo puntuado' }}</button>
          <button class="hero-outline" :disabled="busy" @click="save('status',{id:selected.id,status:'Terminada'})">✓ Marcar serie terminada</button>
          <button class="hero-outline hero-return" aria-label="Volver a la colección" title="Volver a la colección" @click="navigate('Biblioteca')">←</button>
        </div>
      </div>
      <div class="series-dashboard">
        <label class="series-status">Estado de la serie<select :value="data.series.find(s=>s.id===selected!.id)?.status" :disabled="busy" @change="save('status',{id:selected.id,status:($event.target as HTMLSelectElement).value})"><option>Pendiente</option><option>Viendo</option><option>Terminada</option></select></label>
        <div class="series-progress"><div><span><strong>{{ rated }} de {{ episodes.length }}</strong> capítulos puntuados</span><strong>{{ progress }}%</strong></div><progress :value="rated" :max="episodes.length || 1" aria-label="Progreso de capítulos puntuados" /></div>
        <div class="series-metrics"><div><strong>{{ seasons.length }}</strong><span>Temporadas</span></div><div><strong>{{ episodes.length }}</strong><span>Capítulos</span></div><div><strong>{{ average }}</strong><span>Promedio ★</span></div></div>
      </div>
    </section>
    <nav class="series-tabs" aria-label="Secciones de la serie">
      <button v-for="(icon,name) in {Capítulos:'▦',Información:'ⓘ',Comentarios:'☷'}" :key="name" :class="{active:tab===name}" :aria-current="tab===name?'page':undefined" @click="tab=name"><span aria-hidden="true">{{ icon }}</span>{{ name }}<small v-if="name==='Comentarios' && comments.length">{{ comments.length }}</small></button>
    </nav>
    <section v-if="tab==='Información'" class="series-info-panel"><h2>Información de la serie</h2><p>{{ selected.description || 'Todavía no hay una sinopsis para esta serie.' }}</p><dl><div><dt>Título original</dt><dd>{{ selected.original_title || selected.title }}</dd></div><div><dt>Género</dt><dd>{{ selected.genre }}</dd></div><div><dt>Año</dt><dd>{{ selected.year }}</dd></div></dl></section>
    <section v-if="tab==='Comentarios'" class="series-info-panel"><h2>Mis comentarios</h2><p v-if="!comments.length" class="muted">Los comentarios que guardes al puntuar cada capítulo aparecerán aquí.</p><article v-for="episode in comments" :key="episode.id" class="series-comment"><h3>T{{ episode.season }} · E{{ episode.number }} — {{ episode.title }} <span>★ {{ episode.score?.toFixed(1) }}</span></h3><p>{{ episode.comment }}</p></article></section>
    <section v-show="tab==='Capítulos'" class="episodes-panel" aria-labelledby="episodes-heading">
      <div class="episodes-panel-heading"><div><h2 id="episodes-heading">Capítulos</h2><p>Una valoración por episodio, de media en media estrella.</p></div><div class="episode-panel-actions"><button class="outline" :disabled="saving || loading || current !== null" @click="manual = !manual">＋ Agregar capítulo</button><button v-if="selected.catalog_id" class="refresh-episodes" :disabled="loading || saving || current !== null" @click="current = null; load(true)">⟳ Actualizar capítulos</button></div></div>
      <div class="episode-toolbar">
        <label>Temporada<select v-model.number="season" :disabled="loading || saving || current !== null" @change="current = null"><option v-for="s in seasons" :key="s" :value="s">Temporada {{ s }}</option><option v-if="!seasons.length" :value="1">Temporada 1</option></select></label>
        <div class="season-overview"><span>Promedio de temporada</span><div><strong>{{ seasonAverage }} ★</strong><small>{{ seasonRated }} de {{ visible.length }} puntuados</small><progress :value="seasonRated" :max="visible.length || 1" aria-label="Progreso de la temporada" /><small>{{ seasonProgress }}%</small></div></div>
        <label class="episode-search"><span class="sr-only">Buscar capítulo</span><input v-model="query" :disabled="current !== null" type="search" placeholder="Buscar capítulo…" /></label>
      </div>
      <p v-if="error" class="error" role="alert">{{ error }} <button @click="load()">Reintentar</button></p>
      <p v-if="notice" class="notice" role="status">{{ notice }}</p>
      <form v-if="manual" class="episode-editor manual-episode" @submit.prevent="addManual">
        <h3>Nuevo capítulo</h3><div class="manual-fields"><label>Temporada<input v-model.number="season" type="number" min="1" max="1000" required /></label><label>Número<input v-model.number="number" type="number" min="1" max="10000" required /></label><label>Título<input v-model="title" maxlength="200" required /></label></div><div class="episode-actions"><button type="button" class="outline" @click="manual = false">Cancelar</button><button class="primary" :disabled="saving || !title.trim()">Agregar capítulo</button></div>
      </form>
      <div class="episodes-table-scroll" tabindex="0" aria-label="Tabla de capítulos, desplazable horizontalmente">
        <table class="episodes-table" :aria-busy="loading">
          <caption class="sr-only">Capítulos de {{ selected.title }}, temporada {{ season }}</caption>
          <thead><tr><th scope="col" class="episode-chevron"><span class="sr-only">Estado de edición</span></th><th scope="col">Capítulo</th><th scope="col">Título</th><th scope="col">Puntuación</th><th scope="col">Comentario</th><th scope="col"><span class="sr-only">Acciones</span></th></tr></thead>
          <tbody>
            <tr v-if="loading"><td colspan="6" class="table-message" role="status">Cargando capítulos…</td></tr>
            <tr v-else-if="!filtered.length"><td colspan="6" class="table-message">No hay capítulos en esta temporada. Puedes agregar uno manualmente.</td></tr>
            <template v-else v-for="episode in filtered" :key="episode.id">
              <tr :class="{ 'is-editing': current?.id === episode.id }">
                <td class="episode-chevron" aria-hidden="true">{{ current?.id === episode.id ? '⌄' : '›' }}</td><td class="episode-index">T{{ season }} · E{{ String(episode.number).padStart(2,'0') }}</td>
                <th scope="row" class="episode-table-title">{{ episode.title }}</th>
                <td><div v-if="episode.score !== null" class="table-rating"><span class="stars" aria-hidden="true">★★★★★<span :style="stars(episode.score)">★★★★★</span></span><strong>{{ episode.score.toFixed(1) }}</strong></div><span v-else class="unrated">Sin puntuar</span></td>
                <td class="episode-comment"><span>{{ episode.comment || '—' }}</span></td>
                <td><button class="outline" :disabled="saving || current !== null" :aria-expanded="current?.id === episode.id" :aria-controls="`episode-editor-${episode.id}`" @click="choose(episode)">{{ current?.id === episode.id ? 'Puntuando…' : episode.score === null ? 'Puntuar' : 'Volver a puntuar' }}</button></td>
              </tr>
              <tr v-if="current?.id === episode.id"><td colspan="6" class="editor-cell"><EpisodeRatingEditor :episode="episode" :poster="selected.image_url" :saving="saving" v-model:score="score" v-model:comment="comment" @save="rate" @cancel="current = null" /></td></tr>
            </template>
          </tbody>
        </table>
      </div>
    </section>
    <p v-if="selected.source_url" class="catalog-attribution">Títulos en el idioma del catálogo. Datos de <a :href="selected.source_url" target="_blank" rel="noopener noreferrer">{{ selected.catalog_source==='jikan'?'MyAnimeList (vía Jikan)':'TVmaze' }}</a><span v-if="selected.catalog_source!=='jikan'"> · CC BY-SA.</span> La sinopsis del capítulo aparece al abrir su puntuación.</p>
  </article>
</template>
