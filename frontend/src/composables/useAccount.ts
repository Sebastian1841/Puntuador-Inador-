import { ref } from 'vue'
import { apiRequest } from '@/services/http'
export const account=ref<{id:number;username:string;admin:number}|null>(null)
export const authEnabled=ref(false)
export async function logout(){await apiRequest('auth/logout',{method:'POST'});localStorage.removeItem('episodiario-profile');account.value=null;window.dispatchEvent(new Event('session-expired'))}
