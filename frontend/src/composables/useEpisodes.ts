import { computed, onMounted, ref } from 'vue'
import { apiRequest } from '@/services/http'
import { useClub } from './useClub'

export interface Episode {
  id: number; series_id: number; season: number; number: number; title: string
  catalog_id?: number | null; image_url?: string; runtime?: number | null; airdate?: string; metadata_loaded?: number
  description: string; score: number | null; comment: string | null
}
export function useEpisodes() {
  const { selected, save } = useClub()
  const episodes = ref<Episode[]>([])
  const loading = ref(false), saving = ref(false), error = ref(''), notice = ref('')
  const season = ref(1), current = ref<Episode | null>(null), score = ref(3.5), comment = ref('')
  const seasons = computed(() => [...new Set(episodes.value.map(e => e.season))].sort((a,b) => a-b))
  const visible = computed(() => episodes.value.filter(e => e.season === season.value))
  const rated = computed(() => episodes.value.filter(e => e.score !== null).length)
  const seasonAverage = computed(() => {
    const reviews = visible.value.filter(e => e.score !== null)
    return reviews.length ? (reviews.reduce((sum,e) => sum + e.score!, 0) / reviews.length).toFixed(1) : '—'
  })
  async function load(refresh = false) {
    if (!selected.value) return
    loading.value = true; error.value = ''
    const requestedSeries = selected.value
    const path = `series/${requestedSeries.id}/episodes`
    try {
      if (refresh) episodes.value = await apiRequest<Episode[]>(path + '/sync', { method: 'POST' })
      else {
        episodes.value = await apiRequest<Episode[]>(path)
        if (requestedSeries.catalog_id && (!episodes.value.length || episodes.value.some(e => e.catalog_id && !e.metadata_loaded))) episodes.value = await apiRequest<Episode[]>(path + '/sync', { method: 'POST' })
      }
      requestedSeries.episode_count = episodes.value.length
      if (!seasons.value.includes(season.value)) season.value = seasons.value[0] ?? 1
    } catch (e) { error.value = (e as Error).message }
    finally { loading.value = false }
  }
  function choose(episode: Episode) {
    if (current.value || saving.value) return
    current.value = episode; score.value = episode.score ?? 3.5; comment.value = episode.comment ?? ''; notice.value = ''
  }
  async function rate() {
    if (!current.value || saving.value) return
    saving.value = true; notice.value = ''
    const episode = current.value
    const value = score.value, text = comment.value
    try {
      if (await save('episode-reviews', { episode_id: episode.id, score: value, comment: text })) {
        episode.score = value; episode.comment = text
        notice.value = `Capítulo ${episode.number} guardado con ${value.toFixed(1)} estrellas.`
        current.value = null
      }
    } finally { saving.value = false }
  }
  async function add(number: number, title: string) {
    if (!selected.value || saving.value) return
    saving.value = true; error.value = ''
    try {
      episodes.value = await apiRequest<Episode[]>(`series/${selected.value.id}/episodes`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ season: season.value, number, title }),
      })
      selected.value.episode_count = episodes.value.length
      notice.value = 'Capítulo agregado.'
      return true
    } catch (e) { error.value = (e as Error).message; return false }
    finally { saving.value = false }
  }
  onMounted(() => load())
  return { episodes, loading, saving, error, notice, season, current, score, comment, seasons, visible, rated, seasonAverage, load, choose, rate, add }
}
