import { useReviewStore } from '@/state/store'
import type { DocStatus } from '@/types'

const STATUS_COLORS: Record<DocStatus, string> = {
  pending: 'bg-amber-100 text-amber-800',
  reviewed: 'bg-blue-100 text-blue-800',
  approved: 'bg-emerald-100 text-emerald-800',
  rejected: 'bg-red-100 text-red-800',
}

export default function QueueSidebar() {
  const {
    documents,
    loadingList,
    currentDocId,
    selectDocument,
    loadDocuments,
  } = useReviewStore()

  return (
    <aside className="flex w-64 flex-col border-r border-slate-200 bg-white">
      <div className="flex items-center justify-between border-b border-slate-100 px-3 py-2">
        <h2 className="text-sm font-medium text-slate-700">Queue</h2>
        <button
          onClick={() => loadDocuments()}
          className="text-xs text-brand-600 hover:underline"
        >
          refresh
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loadingList && (
          <p className="p-3 text-xs text-slate-400">Loading…</p>
        )}
        {!loadingList && documents.length === 0 && (
          <p className="p-3 text-xs text-slate-400">No documents</p>
        )}
        {documents.map((doc) => (
          <button
            key={doc.doc_id}
            onClick={() => selectDocument(doc.doc_id)}
            className={`w-full border-b border-slate-50 px-3 py-2.5 text-left transition-colors hover:bg-slate-50 ${
              currentDocId === doc.doc_id ? 'bg-brand-50' : ''
            }`}
          >
            <div className="flex items-center justify-between gap-1">
              <span className="truncate text-sm font-medium text-slate-800">
                {doc.title || doc.doc_id}
              </span>
              <span
                className={`shrink-0 rounded px-1.5 py-0.5 text-[10px] font-medium ${STATUS_COLORS[doc.status]}`}
              >
                {doc.status}
              </span>
            </div>
            <div className="mt-0.5 flex items-center justify-between text-[11px] text-slate-500">
              <span>{doc.agency}</span>
              <span>
                {doc.page_count}p · {(doc.confidence * 100).toFixed(0)}%
              </span>
            </div>
          </button>
        ))}
      </div>
    </aside>
  )
}
