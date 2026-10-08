import { useEffect } from 'react'
import { useReviewStore } from '@/state/store'
import QueueSidebar from '@/components/QueueSidebar'
import SplitLayout from '@/components/SplitLayout'
import StatusBar from '@/components/StatusBar'
import ConfidenceLegend from '@/components/ConfidenceLegend'
import DiffToggle from '@/components/DiffToggle'

export default function App() {
  const { loadDocuments, error, clearError, document } = useReviewStore()

  useEffect(() => {
    loadDocuments() // load all pending + reviewed by default
  }, [loadDocuments])

  return (
    <div className="flex h-full flex-col">
      {/* Top bar */}
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-2 shadow-sm">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold text-slate-800">
            moe-docs Review
          </h1>
          {document && (
            <span className="rounded bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
              {document.meta.doc_id}
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <DiffToggle />
          <ConfidenceLegend />
        </div>
      </header>

      {/* Error banner */}
      {error && (
        <div className="flex items-center justify-between bg-red-50 px-4 py-2 text-sm text-red-700">
          <span>{error}</span>
          <button
            onClick={clearError}
            className="ml-4 text-red-500 hover:underline"
          >
            dismiss
          </button>
        </div>
      )}

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        <QueueSidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <SplitLayout />
          <StatusBar />
        </div>
      </div>
    </div>
  )
}
