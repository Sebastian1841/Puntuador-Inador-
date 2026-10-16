import { apiRequest } from './http';
export interface CatalogSeries {
  catalog_source?: 'tvmaze' | 'jikan'
  catalog_id: number
  title: string
  original_title: string
  year: number | null
  genre: string
  description: string
  image_url: string
  source_url: string
}

export async function searchCatalog(query: string, signal?: AbortSignal, source = 'tvmaze'): Promise<CatalogSeries[]> {
  return apiRequest<CatalogSeries[]>(`catalog/search?q=${encodeURIComponent(query)}&source=${source}`, { signal })
}
