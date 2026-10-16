import { ref } from 'vue'
export type Theme = 'light' | 'dark'
const theme = ref<Theme>(document.documentElement.dataset.theme === 'light' ? 'light' : 'dark')
function setTheme(value: Theme) {
  theme.value = value
  document.documentElement.dataset.theme = value
  document.documentElement.style.colorScheme = value
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', value === 'dark' ? '#070e1c' : '#edf2fa')
  try { localStorage.setItem('puntuador-theme', value) } catch { /* Theme still works when storage is unavailable. */ }
}
export function useTheme() { return { theme, setTheme, toggleTheme: () => setTheme(theme.value === 'dark' ? 'light' : 'dark') } }
