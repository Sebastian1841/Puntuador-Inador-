export class ApiError extends Error {
  constructor(message: string, public status: number) { super(message); this.name = 'ApiError' }
}

export async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response
  try {
    const headers = new Headers(options?.headers)
    headers.set('X-Requested-With','Puntuador')
    const profile = localStorage.getItem('episodiario-profile')
    if (profile && !headers.has('X-Profile-Id')) headers.set('X-Profile-Id', profile)
    response = await fetch(`/api/${path}`, { ...options, headers })
  } catch (error) {
    if ((error as Error).name === 'AbortError') throw error
    throw new Error('No se pudo conectar con el servidor. Comprueba tu conexión y vuelve a intentarlo.')
  }
  const text = await response.text()
  let result
  try { result = JSON.parse(text) }
  catch { throw new Error('La API no está disponible. Reinicia npm run dev y comprueba que Python inició en el puerto 8000.') }
  if(response.status===401 && !path.startsWith('auth/'))window.dispatchEvent(new Event('session-expired'))
  if (!response.ok) throw new ApiError(result.error || 'No se pudo completar la solicitud', response.status)
  return result as T
}
