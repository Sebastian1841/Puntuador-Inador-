import { onMounted, onUnmounted, watch, type Ref } from 'vue'
import type { Series } from '@/types/club'

const routes: Record<string,string> = { Recomendaciones:'recomendaciones', Biblioteca:'inicio', Coleccion:'coleccion', Ranking:'ranking', Configuracion:'configuracion', Siguiendo:'coleccion?estado=siguiendo', Pendientes:'coleccion?estado=pendiente', Terminadas:'coleccion?estado=terminada', Favoritas:'coleccion?favoritas=true' }
const aliases: Record<string,string> = {biblioteca:'inicio',siguiendo:'coleccion?estado=siguiendo',pendientes:'coleccion?estado=pendiente',terminadas:'coleccion?estado=terminada',favoritas:'coleccion?favoritas=true',perfiles:'configuracion?seccion=perfiles',calendario:'inicio',explorar:'coleccion'}

// Hash routes support reloads, bookmarks and browser Back without server rewrites.
export function useNavigation(data: { series: Series[] }, page: Ref<string>, selected: Ref<Series | null>) {
  function resolveRoute() {
    const path=window.location.hash.slice(2).split('?')[0] || 'inicio'
    if(aliases[path]) { window.history.replaceState(null,'',`#/${aliases[path]}`) }
    const match = window.location.hash.match(/^#\/series\/(\d+)$/)
    if (match) {
      page.value = 'Serie'
      selected.value = data.series.find(series => series.id === Number(match[1])) ?? null
    } else {
      page.value = Object.keys(routes).find(key => window.location.hash.split('?')[0] === `#/${routes[key]}`) ?? 'Biblioteca'
      selected.value = null
    }
  }
  function navigate(destination: string, id?: number) {
    const hash = destination === 'Serie' ? `#/series/${id}` : `#/${routes[destination] ?? 'biblioteca'}`
    window.location.hash = hash
    resolveRoute()
    window.scrollTo({ top: 0, behavior: 'instant' })
  }
  watch(() => data.series, resolveRoute)
  onMounted(() => { resolveRoute(); window.addEventListener('hashchange', resolveRoute) })
  onUnmounted(() => window.removeEventListener('hashchange', resolveRoute))
  return { navigate }
}
