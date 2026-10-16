import { apiRequest } from './http';
import type { Profile, Series, Review, DashboardData } from '../types/club';
export type MutationEndpoint = `profiles/${number}` | 'profiles' | 'series' | 'reviews' | 'episode-reviews' | 'profile' | 'favorites' | 'notes' | 'status' | 'settings';
export interface ClubState {
    dashboard: DashboardData;
    active_profile_id: number;
    notes: string;
    profiles: Profile[];
    series: Series[];
    reviews: Review[];
    settings: {
        name: string;
        accent: string;
        compact: boolean;
    };
}
async function request(path: string, body?: unknown): Promise<ClubState> {
    return apiRequest<ClubState>(path, body === undefined ? undefined : {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
}
export const clubApi = {
    deleteProfile: (id: number) => apiRequest<ClubState>(`profiles/${id}`, { method: 'DELETE' }),
    getState: (profile?: number) => apiRequest<ClubState>('state', profile ? { headers: { 'X-Profile-Id': String(profile) } } : undefined),
    mutate: (endpoint: MutationEndpoint, body: unknown) => request(endpoint, body),
};
