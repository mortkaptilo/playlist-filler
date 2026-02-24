import { atom } from 'jotai'
import type { Track } from '../types'

export const seedTracksAtom = atom<Track[]>([])
export const searchQueryAtom = atom('')
export const searchResultsAtom = atom<Track[]>([])
export const isSearchingAtom = atom(false)
export const recommendationsAtom = atom<Track[]>([])
export const isLoadingRecsAtom = atom(false)
export const recErrorAtom = atom<string | null>(null)
