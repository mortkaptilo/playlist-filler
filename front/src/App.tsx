import { useAtomValue } from 'jotai'
import { recommendationsAtom } from './store/atoms'
import { SearchBar } from './components/SearchBar'
import { SeedPlaylist } from './components/SeedPlaylist'
import { Recommendations } from './components/Recommendations'

function App() {
  const recommendations = useAtomValue(recommendationsAtom)

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex flex-col">
      <header className="border-b border-zinc-800/80 px-6 py-4 shrink-0">
        <div className="max-w-5xl mx-auto flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center shrink-0">
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
            </svg>
          </div>
          <div>
            <h1 className="text-sm font-bold text-white leading-none tracking-tight">Playlist Filler</h1>
            <p className="text-xs text-zinc-500 mt-0.5">ML-powered track recommendations</p>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-5xl w-full mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 items-start">

          {/* Left: Search + Seed Playlist */}
          <div className="flex flex-col gap-3">
            <SearchBar />
            <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4">
              <SeedPlaylist />
            </div>
          </div>

          {/* Right: Recommendations */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl p-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xs font-semibold text-zinc-400 uppercase tracking-widest">
                Recommendations
              </h2>
              {recommendations.length > 0 && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-zinc-500 bg-zinc-800 px-2 py-0.5 rounded-full">
                    {recommendations.length} tracks
                  </span>
                </div>
              )}
            </div>
            <Recommendations />
          </div>

        </div>
      </main>
    </div>
  )
}

export default App
