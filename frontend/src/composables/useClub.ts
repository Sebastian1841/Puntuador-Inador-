import { ApiError } from '../services/http'
import { useNavigation } from './useNavigation'
import { computed, reactive, ref, inject, type InjectionKey } from 'vue'
import { useRanking } from './useRanking'
import type { Profile, Series, Review, DashboardData } from '../types/club'
import { clubApi, type MutationEndpoint, type ClubState } from '../services/clubApi'

const newSeries = () => ({ catalog_source: 'tvmaze' as 'tvmaze' | 'jikan', favorite: false, catalog_id: null as number | null, image_url: '', source_url: '', original_title: '', title: '', genre: 'Drama', year: new Date().getFullYear(), status: 'Pendiente', description: '', color: '#102372' })

export function createClub() {
  const data = reactive({ dashboard: { activity: [], upcoming: [] } as DashboardData, active_profile_id: 0, notes: '', profiles: [] as Profile[], series: [] as Series[], reviews: [] as Review[], settings: { name: 'Mi biblioteca', accent: '#FF6600', compact: false } })
  const page = ref('Biblioteca'), search = ref(''), filter = ref('Todas'), modal = ref('')
  const profileScreen = ref<'select' | 'manage' | 'editor'>('select')
  const selected = ref<Series | null>(null), error = ref(''), busy = ref(false), loading = ref(true)
  const { navigate } = useNavigation(data, page, selected)
  const form = reactive(newSeries())
  const profileForm = reactive({ name: '', color: '#FF6600', avatar: '', description: '', targetId: 0, processing: false, mode: 'create' })
  const activeProfile = computed(() => data.profiles.find(p => p.id === data.active_profile_id))
  function applyState(state: ClubState) { Object.assign(data, state); localStorage.setItem('episodiario-profile', String(state.active_profile_id)) }
  async function changeProfile(id: number) {
    if (busy.value) return
    busy.value = true; error.value = ''
    try { applyState(await clubApi.getState(id)); filter.value = 'Todas'; search.value = ''; navigate('Biblioteca'); modal.value = '' }
    catch (e) { error.value = (e as Error).message }
    finally { busy.value = false }
  }
  const prefs = reactive({ ...data.settings })
  const ranking = useRanking(data, page, filter, search)

  async function load() {
    loading.value = true; error.value = ''
    try {
      const remembered = localStorage.getItem('episodiario-profile')
      let showPicker = !remembered
      let state: ClubState
      try { state = await clubApi.getState() }
      catch (e) {
        // A profile removed in another tab/device should not block startup.
        if (!remembered || !(e instanceof ApiError) || ![400, 404].includes(e.status)) throw e
        localStorage.removeItem('episodiario-profile')
        state = await clubApi.getState()
        showPicker = true
      }
      applyState(state)
      if (showPicker) open('profiles')
    }
    catch (e) { error.value = (e as Error).message }
    finally { loading.value = false }
  }
  async function save(endpoint: MutationEndpoint, body: unknown) {
    busy.value = true; error.value = ''
    try { applyState(await clubApi.mutate(endpoint, body)); return true }
    catch (e) { error.value = (e as Error).message; return false }
    finally { busy.value = false }
  }
  function open(kind: string, series?: Series) {
    error.value = ''
    if (kind === 'settings') { modal.value = ''; navigate('Configuracion'); return }
    if (kind === 'detail' && series) { modal.value = ''; navigate('Serie', series.id); return }
    modal.value = kind
    if (series) selected.value = series
    if (kind === 'settings') Object.assign(prefs, data.settings)
    if (kind === 'series') Object.assign(form, newSeries())
    if (kind === 'profiles') {
      profileScreen.value = 'select'
      const profile = activeProfile.value
      Object.assign(profileForm, { name: profile?.name || '', color: profile?.color || '#FF6600', avatar: profile?.avatar || '', description: profile?.description || '', targetId: profile?.id || 0, processing: false, mode: profile ? 'edit' : 'create' })
    }
  }
  async function submit() {
    if (busy.value || profileForm.processing || (modal.value === 'profiles' && profileScreen.value !== 'editor')) return
    let ok = false
    if (modal.value === 'series') ok = await save('series', form)
    if (modal.value === 'settings') ok = await save('settings', prefs)
    if (modal.value === 'profiles') ok = await save(profileForm.mode === 'create' ? 'profiles' : `profiles/${profileForm.targetId}`, { name: profileForm.name, color: profileForm.color, avatar: profileForm.avatar, description: profileForm.description })
    if (ok) {
      if (modal.value === 'profiles' && profileForm.mode === 'edit') profileScreen.value = 'manage'
      else { if (modal.value === 'profiles') { filter.value = 'Todas'; search.value = ''; navigate('Biblioteca') }; modal.value = '' }
    }
  }
  async function deleteProfile(id: number) {
    if (busy.value || profileForm.processing) return false
    busy.value = true; error.value = ''
    try {
      applyState(await clubApi.deleteProfile(id)); navigate('Biblioteca'); profileScreen.value = 'manage'
      return true
    } catch (e) { error.value = (e as Error).message; return false }
    finally { busy.value = false }
  }
  function exportData() {
    const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' }))
    const a = document.createElement('a'); a.href = url; a.download = 'mi-biblioteca.json'; a.click(); URL.revokeObjectURL(url)
  }
  return { profileScreen, deleteProfile, activeProfile, profileForm, changeProfile, navigate, data, page, search, filter, modal, selected, error, busy, loading, form, prefs, ...ranking, load, save, open, submit, exportData }
}
export const clubKey: InjectionKey<ReturnType<typeof createClub>> = Symbol('club')
export function useClub() {
  const club = inject(clubKey)
  if (!club) throw new Error('Falta el proveedor de la biblioteca')
  return club
}
