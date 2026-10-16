import { computed, type Ref } from 'vue'
import type { Series, Review } from '../types/club'

export function useRanking(
  data: { series: Series[]; reviews: Review[] },
  page: Ref<string>,
  filter: Ref<string>,
  search: Ref<string>,
) {
  // Aggregate once when reviews change, rather than scanning them per card/comparison.
  const totals = computed(() => {
    const result = new Map<number, { sum: number; count: number }>()
    for (const review of data.reviews) {
      const current = result.get(review.series_id) ?? { sum: 0, count: 0 }
      current.sum += review.score
      current.count++
      result.set(review.series_id, current)
    }
    return result
  })
  const average = (id: number) => {
    const total = totals.value.get(id)
    return total ? total.sum / total.count : 0
  }
  const votes = (id: number) => totals.value.get(id)?.count ?? 0
  const ranked = computed(() => data.series
    .filter(series => votes(series.id) > 0)
    .sort((a, b) => average(b.id) - average(a.id) || votes(b.id) - votes(a.id)))
  const visible = computed(() => {
    const query = search.value.trim().toLowerCase()
    const source = page.value === 'Ranking' ? ranked.value : data.series
    return source.filter(series =>
      (filter.value === 'Todas' || (filter.value === 'Favoritas' ? series.favorite : series.status === filter.value)) &&
      `${series.title} ${series.genre}`.toLowerCase().includes(query))
  })
  const top = computed(() => ranked.value[0])
  const stars = (score: number) => ({ width: `${score / 5 * 100}%` })
  return { average, votes, ranked, visible, top, stars }
}
