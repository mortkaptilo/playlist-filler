import { useAtomValue } from 'jotai'
import { recommendationsAtom, isLoadingRecsAtom, recErrorAtom } from '../store/atoms'
import { TrackItem } from './TrackItem'

export function Recommendations() {
  const recommendations = useAtomValue(recommendationsAtom)
  const isLoading = useAtomValue(isLoadingRecsAtom)
  const error = useAtomValue(recErrorAtom)

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3 text-zinc-500">
        <svg className="w-7 h-7 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
        <p className="text-sm">Running models…</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-3 text-center px-4">
        <svg className="w-8 h-8 text-red-400/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
        </svg>
        <p className="text-sm text-red-400">{error}</p>
      </div>
    )
  }

  if (recommendations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-2 text-center px-4">
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
            d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010 7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.507-1.938-1.354A9.01 9.01 0 012.25 12c0-.83.112-1.633.322-2.396C2.806 8.756 3.63 8.25 4.51 8.25H6.75z"
          />
        </svg>
        <p className="text-sm font-medium text-zinc-400">No recommendations yet</p>
        <p className="text-xs text-zinc-600 max-w-48">
          Add tracks to your playlist and hit &ldquo;Fill Playlist&rdquo;
        </p>
      </div>
    )
  }

  return (
    <ul className="flex flex-col gap-1 max-h-[calc(100vh-260px)] overflow-y-auto pr-1">
      {recommendations.map((track, i) => (
        <li
          key={track.track_id}
          className="flex items-center bg-zinc-800/40 rounded-lg hover:bg-zinc-800 transition-colors"
        >
          <TrackItem track={track} index={i + 1} />
        </li>
      ))}
    </ul>
  )
}
