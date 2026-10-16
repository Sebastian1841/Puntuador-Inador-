<script setup lang="ts">
import { computed } from 'vue'
import type { Episode } from '@/composables/useEpisodes'
const props = defineProps<{ episode: Episode; poster?: string; saving: boolean }>()
const score = defineModel<number>('score', { required: true })
const comment = defineModel<string>('comment', { required: true })
defineEmits<{ save: []; cancel: [] }>()
const image = computed(() => props.episode.image_url || props.poster)
const date = computed(() => {
  if (!props.episode.airdate) return 'Sin fecha disponible'
  const value = new Date(props.episode.airdate + 'T12:00:00')
  return Number.isNaN(value.getTime()) ? 'Sin fecha disponible' : new Intl.DateTimeFormat('es-CL', { day: 'numeric', month: 'short', year: 'numeric' }).format(value)
})
</script>
<template>
  <form :id="`episode-editor-${episode.id}`" class="episode-rating-detail" :aria-label="'Puntuar ' + episode.title" :aria-busy="saving" @submit.prevent="$emit('save')">
    <div class="rating-episode-info">
      <img v-if="image" :src="image" :alt="episode.image_url ? 'Imagen del capítulo' : 'Portada de la serie'" decoding="async" />
      <div class="rating-episode-copy">
        <span class="rating-episode-code">T{{ episode.season }} · E{{ String(episode.number).padStart(2,'0') }}</span>
        <h3>{{ episode.title }}</h3>
        <p>{{ episode.description || 'Este capítulo todavía no tiene una sinopsis disponible.' }}</p>
        <dl><div><dt>Temporada</dt><dd>{{ episode.season }}</dd></div><div><dt>Capítulo</dt><dd>{{ episode.number }}</dd></div><div><dt>Duración</dt><dd>{{ episode.runtime ? episode.runtime + ' min' : 'No disponible' }}</dd></div><div><dt>Fecha de emisión</dt><dd>{{ date }}</dd></div></dl>
      </div>
    </div>
    <div class="rating-episode-controls">
      <label :for="`score-${episode.id}`">Mi puntuación</label>
      <div class="rating-detail-value"><span class="stars" aria-hidden="true">★★★★★<span :style="{ width: `${score / 5 * 100}%` }">★★★★★</span></span><output :for="`score-${episode.id}`">{{ score.toFixed(1) }} <small>/ 5</small></output></div>
      <input :id="`score-${episode.id}`" v-model.number="score" :disabled="saving" type="range" min="0.5" max="5" step="0.5" :aria-valuetext="`${score} de 5 estrellas`" />
      <label :for="`comment-${episode.id}`">Comentario</label>
      <textarea :id="`comment-${episode.id}`" v-model="comment" :disabled="saving" maxlength="2000" placeholder="¿Qué te pareció este capítulo?" />
      <span class="rating-comment-count">{{ comment.length }} / 2000</span>
      <div class="episode-actions"><button type="button" class="outline" :disabled="saving" @click="$emit('cancel')">Cancelar</button><button class="primary" :disabled="saving">{{ saving ? 'Guardando…' : 'Guardar puntuación' }}</button></div>
    </div>
  </form>
</template>
