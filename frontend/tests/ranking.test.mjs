import { test } from 'node:test'
import assert from 'node:assert/strict'
import { reactive, ref } from 'vue'
import { useRanking } from '../src/composables/useRanking.ts'

test('ranking conserva medias, desempates y actualizaciones reactivas', () => {
  const data = reactive({
    series: [1, 2, 3].map(id => ({ id, title: `Serie ${id}`, genre: 'Drama', year: 2026, status: id === 2 ? 'Viendo' : 'Terminada', description: '', color: '#102372' })),
    reviews: [{ series_id: 1, profile_id: 1, score: 3.5, comment: '' }, { series_id: 2, profile_id: 1, score: 3, comment: '' }, { series_id: 2, profile_id: 2, score: 4, comment: '' }],
  })
  const page = ref('Ranking'), filter = ref('Todas'), search = ref('')
  const ranking = useRanking(data, page, filter, search)
  assert.equal(ranking.average(2), 3.5)
  assert.deepEqual(ranking.ranked.value.map(s => s.id), [2, 1])
  data.reviews[0].score = 5
  assert.equal(ranking.top.value.id, 1)
  filter.value = 'Viendo'
  assert.deepEqual(ranking.visible.value.map(s => s.id), [2])
  filter.value = 'Todas'
  search.value = 'serie 3'
  assert.equal(ranking.visible.value.length, 0)
  page.value = 'Biblioteca'
  assert.deepEqual(ranking.visible.value.map(s => s.id), [3])
})

test('los renders repetidos reutilizan el agregado de opiniones', () => {
  let reads = 0
  const reviews = Array.from({ length: 10000 }, (_, i) => ({
    series_id: i % 1000, profile_id: Math.floor(i / 1000), comment: '',
    get score() { reads++; return (i % 10 + 1) / 2 },
  }))
  const data = { series: Array.from({ length: 1000 }, (_, id) => ({ id, title: `Serie ${id}`, genre: 'Drama', status: 'Viendo' })), reviews }
  const ranking = useRanking(data, ref('Ranking'), ref('Todas'), ref(''))
  const start = performance.now()
  assert.equal(ranking.ranked.value.length, 1000)
  for (let render = 0; render < 10; render++) {
    for (const series of data.series) { ranking.average(series.id); ranking.votes(series.id) }
  }
  assert.equal(reads, reviews.length)
  console.log(`Ranking de 1000 series / 10000 opiniones y 10 lecturas por tarjeta: ${(performance.now() - start).toFixed(1)} ms; ${reads} lecturas de puntuación`)
})
