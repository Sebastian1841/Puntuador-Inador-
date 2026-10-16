export type Profile = {
    description?: string;
    series_count?: number;
    favorites_count?: number;
    rated_count?: number;
    pending_count?: number;
    avatar?: string;
    id: number;
    name: string;
    color: string;
};
export type Series = {
    catalog_source?: 'tvmaze' | 'jikan';
    favorite?: boolean;
    episode_count?: number;
    catalog_id?: number | null;
    image_url?: string;
    source_url?: string;
    original_title?: string;
    id: number;
    title: string;
    genre: string;
    year: number;
    status: string;
    description: string;
    color: string;
};
export type Review = {
    episode_id?: number;
    episode_title?: string;
    season?: number;
    number?: number;
    series_id: number;
    profile_id: number;
    score: number;
    comment: string;
};

export type DashboardData = {
    activity: { id: number; series_id: number; title: string; image_url: string; kind: string; detail: string; created_at: string }[];
    upcoming: { id: number; series_id: number; series_title: string; image_url: string; title: string; season: number; number: number; airdate: string }[];
};
