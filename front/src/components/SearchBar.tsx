import { useEffect, useRef, useState } from 'react'
import { useAtom } from 'jotai'
import {
  searchQueryAtom,
  searchResultsAtom,
  isSearchingAtom,
  seedTracksAtom,
} from '../store/atoms'
import { searchTracks } from '../api'
import { TrackItem } from './TrackItem'
import type { Track } from '../types'

export function SearchBar() {
  const [query, setQuery] = useAtom(searchQueryAtom)
  const [results, setResults] = useAtom(searchResultsAtom)
  const [isSearching, setIsSearching] = useAtom(isSearchingAtom)
  const [seedTracks, setSeedTracks] = useAtom(seedTracksAtom)
  const [open, setOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      setOpen(false)
      return
    }
    const timer = setTimeout(async () => {
      setIsSearching(true)
      try {
        const data = await searchTracks(query)
        setResults(data)
        setOpen(true)
      } catch {
        setResults([])
      } finally {
        setIsSearching(false)
      }
    }, 350)
    return () => clearTimeout(timer)
  }, [query, setResults, setIsSearching])

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [])

  function addTrack(track: Track) {
    if (!seedTracks.find(t => t.track_id === track.track_id)) {
      setSeedTracks(prev => [...prev, track])
    }
    setQuery('')
    setResults([])
    setOpen(false)
  }

  const seedIds = new Set(seedTracks.map(t => t.track_id))

  return (
    <div ref={containerRef} className="relative">
      <div className="relative flex items-center">
        <svg
          className="absolute left-3 w-4 h-4 text-zinc-500 pointer-events-none"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        {isSearching && (
          <svg
            className="absolute right-3 w-4 h-4 text-zinc-500 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
        )}
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          onKeyDown={e => e.key === 'Escape' && setOpen(false)}
          placeholder="Search tracks or artists…"
          className="w-full bg-zinc-900 border border-zinc-700 text-white placeholder-zinc-500 text-sm rounded-xl pl-10 pr-10 py-3 outline-none focus:border-emerald-500/60 focus:ring-2 focus:ring-emerald-500/20 transition-all"
        />
      </div>

      {open && results.length > 0 && (
        <ul className="absolute z-50 top-full mt-1.5 w-full bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl overflow-hidden max-h-72 overflow-y-auto">
          {results.map(track => {
            const added = seedIds.has(track.track_id)
            return (
              <li
                key={track.track_id}
                onClick={() => !added && addTrack(track)}
                className={`flex items-center border-b border-zinc-800 last:border-0 transition-colors ${
                  added
                    ? 'opacity-40 cursor-default'
                    : 'cursor-pointer hover:bg-zinc-800'
                }`}
              >
                <TrackItem
                  track={track}
                  action={
                    <span
                      className={`shrink-0 mr-2 text-xs font-semibold w-10 text-right ${
                        added ? 'text-zinc-500' : 'text-emerald-400'
                      }`}
                    >
                      {added ? 'Added' : '+ Add'}
                    </span>
                  }
                />
              </li>
            )
          })}
        </ul>
      )}

      {open && query.trim() && !isSearching && results.length === 0 && (
        <div className="absolute z-50 top-full mt-1.5 w-full bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl p-5 text-center text-sm text-zinc-500">
          No tracks found for &ldquo;{query}&rdquo;
        </div>
      )}
    </div>
  )
}
