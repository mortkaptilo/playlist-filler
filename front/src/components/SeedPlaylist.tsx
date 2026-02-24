import { useAtom, useSetAtom } from 'jotai'
import {
  seedTracksAtom,
  recommendationsAtom,
  isLoadingRecsAtom,
  recErrorAtom,
} from '../store/atoms'
import { getRecommendations } from '../api'
import { TrackItem } from './TrackItem'

export function SeedPlaylist() {
  const [seedTracks, setSeedTracks] = useAtom(seedTracksAtom)
  const setRecommendations = useSetAtom(recommendationsAtom)
  const [isLoading, setIsLoading] = useAtom(isLoadingRecsAtom)
  const setError = useSetAtom(recErrorAtom)

  function removeTrack(track_id: string) {
    setSeedTracks(prev => prev.filter(t => t.track_id !== track_id))
  }

  async function fillPlaylist() {
    setIsLoading(true)
    setError(null)
    try {
      const recs = await getRecommendations(seedTracks.map(t => t.track_id))
      setRecommendations(recs)
    } catch {
      setError('Could not reach the server. Make sure the backend is running.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-widest">
          Your Playlist
        </h2>
        {seedTracks.length > 0 && (
          <span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded-full">
            {seedTracks.length} track{seedTracks.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {seedTracks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-14 text-center gap-2">
          <svg
            className="w-10 h-10 text-zinc-700"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"
            />
          </svg>
          <p className="text-sm text-zinc-500">Search above to add seed tracks</p>
        </div>
      ) : (
        <ul className="flex flex-col gap-1 max-h-80 overflow-y-auto pr-1">
          {seedTracks.map((track, i) => (
            <li
              key={track.track_id}
              className="flex items-center bg-zinc-800/50 rounded-lg hover:bg-zinc-800 transition-colors group"
            >
              <TrackItem
                track={track}
                index={i + 1}
                action={
                  <button
                    onClick={() => removeTrack(track.track_id)}
                    className="opacity-0 group-hover:opacity-100 mr-2 shrink-0 transition-opacity text-zinc-500 hover:text-red-400 p-1 rounded-md hover:bg-red-400/10"
                    aria-label="Remove track"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                }
              />
            </li>
          ))}
        </ul>
      )}

      <button
        onClick={fillPlaylist}
        disabled={seedTracks.length === 0 || isLoading}
        className="mt-1 w-full py-3 rounded-xl font-semibold text-sm bg-emerald-500 text-white hover:bg-emerald-400 active:scale-[0.98] disabled:opacity-30 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20"
      >
        {isLoading ? (
          <>
            <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Finding tracks…
          </>
        ) : (
          <>
            Fill Playlist
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M9 5l7 7-7 7" />
            </svg>
          </>
        )}
      </button>
    </div>
  )
}
