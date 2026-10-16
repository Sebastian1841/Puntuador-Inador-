<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useClub } from '@/composables/useClub'
import { useCatalogSearch } from '@/composables/useCatalogSearch'
import type { CatalogSeries } from '@/services/catalogApi'
const { data, form, busy } = useClub()
const { source, query, results, loading, error, searched, search } = useCatalogSearch()
const manual = ref(false), resultPage = ref(0)
const chosen = ref<CatalogSeries | null>(null)
const shown = computed(() => results.value.slice(resultPage.value * 2, resultPage.value * 2 + 2))
const pages = computed(() => Math.ceil(results.value.length / 2))
const alreadyAdded = (id: number) => data.series.some(series => series.catalog_id === id && (series.catalog_source || 'tvmaze') === source.value)
function select(series: CatalogSeries) {
  chosen.value = series
  Object.assign(form, { ...series, year: series.year ?? new Date().getFullYear(), color: '#102372' })
}
function reset() {
  chosen.value = null
  Object.assign(form, { catalog_source: source.value, title: '', genre: 'Drama', year: new Date().getFullYear(), description: '', catalog_id: null, image_url: '', source_url: '', original_title: '' })
}
function mode(value: boolean) { manual.value = value; reset() }
watch([query, source], () => { reset(); resultPage.value = 0 })
</script>
<template>
  <p class="series-dialog-intro">Busca una serie en el catálogo o agrégala manualmente a tu colección.</p>
  <fieldset class="series-form-fields" :disabled="busy">
    <div class="series-source-tabs" role="group" aria-label="Forma de agregar una serie">
      <button type="button" :aria-pressed="!manual" @click="mode(false)">⌕ Buscar en catálogo</button>
      <button type="button" :aria-pressed="manual" @click="mode(true)">✎ Agregar manualmente</button>
    </div>
    <div v-if="!manual" class="series-search-box">
      <div class="catalog-provider" role="group" aria-label="Catálogo"><button type="button" :aria-pressed="source==='tvmaze'" @click="source='tvmaze'">Series · TVmaze</button><button type="button" :aria-pressed="source==='jikan'" @click="source='jikan'">Anime · MyAnimeList</button></div>
      <label for="series-query">¿Qué serie quieres agregar?</label>
      <div class="series-search-row"><input id="series-query" v-model="query" type="search" maxlength="100" placeholder="Ej. La casa búho, Breaking Bad…" @keydown.enter.prevent="search" /><button type="button" :disabled="loading || query.trim().length<2" @click="search">{{ loading?'Buscando…':'⌕ Buscar' }}</button></div>
      <small>Busca por título o título original. Escribe al menos 2 caracteres.</small>
    </div>
    <div class="series-add-layout">
      <section class="series-results-panel">
        <template v-if="!manual">
          <div class="series-results-heading"><h3>Resultados</h3><span>{{ results.length }} {{ results.length===1?'resultado':'resultados' }}</span></div>
          <p v-if="loading" class="series-search-empty" role="status">Buscando tu próxima serie…</p>
          <div v-else-if="error" class="error" role="alert">{{ error }} <button type="button" @click="search">Reintentar</button></div>
          <p v-else-if="!results.length" class="series-search-empty">{{ searched?'No encontramos series. Prueba el título original o agrégala manualmente.':'Busca una serie y selecciónala para agregarla a tu perfil.' }}</p>
          <div v-else class="series-search-results">
            <button v-for="series in shown" :key="series.catalog_id" type="button" class="series-search-card" :class="{selected:chosen?.catalog_id===series.catalog_id}" :aria-pressed="chosen?.catalog_id===series.catalog_id" :disabled="alreadyAdded(series.catalog_id)" @click="select(series)">
              <img v-if="series.image_url" :src="series.image_url" alt="" loading="lazy" /><span v-else class="series-poster-fallback">▤</span>
              <span class="series-search-info"><strong>{{ series.title }}</strong><small>{{ series.original_title }}</small><span class="series-search-tags"><span>{{ series.year || 'Año sin confirmar' }}</span><span>{{ series.genre }}</span></span><span class="series-search-description">{{ series.description || 'Sin sinopsis disponible.' }}</span><span class="series-choice-label">{{ alreadyAdded(series.catalog_id)?'Ya está en tu colección':chosen?.catalog_id===series.catalog_id?'✓ Seleccionada':'Seleccionar serie' }}</span></span>
            </button>
          </div>
          <div v-if="pages>1" class="profile-pagination"><button type="button" :disabled="resultPage===0" @click="resultPage--">‹</button><span>{{ resultPage+1 }} / {{ pages }}</span><button type="button" :disabled="resultPage>=pages-1" @click="resultPage++">›</button></div>
        </template>
        <template v-else>
          <h3>Información de la serie</h3>
          <label>Nombre<input v-model="form.title" required maxlength="100" placeholder="Nombre de la serie" /></label>
          <div class="form-row"><label>Género<input v-model="form.genre" required maxlength="40" /></label><label>Año<input v-model.number="form.year" type="number" min="1900" max="2100" required /></label></div>
          <label>Sinopsis<textarea v-model="form.description" maxlength="2000" placeholder="¿De qué trata?" /></label>
          <label class="color-field">Color de portada<input v-model="form.color" type="color" /></label>
        </template>
      </section>
      <aside class="series-add-options">
        <h3>Agregar a mi colección</h3>
        <p v-if="chosen" class="series-chosen-name">{{ chosen.title }}</p>
        <label>Estado inicial</label>
        <div class="series-status-options"><button v-for="status in ['Viendo','Pendiente','Terminada']" :key="status" type="button" :aria-pressed="form.status===status" @click="form.status=status">{{ status }}</button></div>
        <p class="series-status-help">{{ form.status==='Viendo'?'La encontrarás entre las series que estás siguiendo.':form.status==='Pendiente'?'Quedará en tu lista para ver después.':'Aparecerá en tus series terminadas.' }}</p>
        <label class="series-favorite-toggle"><span><strong>♡ Agregar a favoritos</strong><small>Aparecerá en tus series favoritas.</small></span><input v-model="form.favorite" type="checkbox" role="switch" /></label>
        <p class="series-personal-hint">Se agregará únicamente a tu perfil. Podrás puntuar sus capítulos desde la colección.</p>
      </aside>
    </div>
  </fieldset>
  <p v-if="source==='jikan' && !manual" class="catalog-attribution">Datos de <a href="https://myanimelist.net" target="_blank" rel="noopener noreferrer">MyAnimeList</a> mediante <a href="https://jikan.moe" target="_blank" rel="noopener noreferrer">Jikan</a>. Las temporadas pueden aparecer como fichas separadas.</p>
  <p v-else class="catalog-attribution">Datos proporcionados por <a href="https://www.tvmaze.com" target="_blank" rel="noopener noreferrer">TVmaze</a> · <a href="https://creativecommons.org/licenses/by-sa/4.0/" target="_blank" rel="noopener noreferrer">CC BY-SA</a></p>
</template>
