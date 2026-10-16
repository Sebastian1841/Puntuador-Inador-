import { onUnmounted, ref, watch } from 'vue'
import { searchCatalog, type CatalogSeries } from '@/services/catalogApi'

export function useCatalogSearch() {
  const source = ref<'tvmaze' | 'jikan'>('tvmaze')
  const query = ref('')
  const results = ref<CatalogSeries[]>([])
  const loading = ref(false)
  const error = ref('')
  const searched = ref(false)
  let timer: ReturnType<typeof setTimeout> | undefined
  let controller: AbortController | undefined
  let version = 0

  async function search() {
    clearTimeout(timer)
    controller?.abort()
    const current = ++version
    if (query.value.trim().length < 2) return
    controller = new AbortController()
    loading.value = true
    error.value = ''
    try {
      const matches = await searchCatalog(query.value.trim(), controller.signal, source.value)
      if (current === version) { results.value = matches; searched.value = true }
    } catch (e) {
      if (current === version && (e as Error).name !== 'AbortError') error.value = (e as Error).message
    } finally {
      if (current === version) loading.value = false
    }
  }

  watch([query, source], () => {
    clearTimeout(timer)
    controller?.abort()
    version++
    results.value = []
    searched.value = false
    loading.value = false
    error.value = ''
    if (query.value.trim().length >= 2) timer = setTimeout(search, 650)
  })
  onUnmounted(() => { clearTimeout(timer); controller?.abort(); version++ })
  return { source, query, results, loading, error, searched, search }
}
