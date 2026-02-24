import type { Track } from './types'

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function searchTracks(query: string): Promise<Track[]> {
  const res = await fetch(`${BASE}/search?q=${encodeURIComponent(query)}`)
  if (!res.ok) throw new Error('Search failed')
  return res.json()
}

export async function getRecommendations(trackIds: string[]): Promise<Track[]> {
  const res = await fetch(`${BASE}/recommendations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ track_ids: trackIds }),
  })
  if (!res.ok) throw new Error('Recommendations failed')
  const data = await res.json()
  return data.recommendations
}
