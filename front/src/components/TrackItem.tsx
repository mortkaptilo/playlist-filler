import type { ReactNode } from 'react'
import type { Track } from '../types'

interface Props {
  track: Track
  index?: number
  action?: ReactNode
}

export function TrackItem({ track, index, action }: Props) {
  return (
    <div className="flex items-center gap-2 px-3 py-2.5 w-full min-w-0">
      {index !== undefined && (
        <span className="text-xs text-zinc-600 w-5 text-right shrink-0">{index}</span>
      )}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white truncate leading-tight">{track.name}</p>
        <p className="text-xs text-zinc-400 truncate mt-0.5">
          {track.artist}
          {track.year ? <span className="text-zinc-600"> · {track.year}</span> : null}
        </p>
      </div>
      {track.genre && (
        <span className="hidden sm:block shrink-0 text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded-full max-w-28 truncate">
          {track.genre.split(',')[0].trim()}
        </span>
      )}
      {action}
    </div>
  )
}
