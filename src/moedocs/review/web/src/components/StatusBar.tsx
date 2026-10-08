import { useReviewStore } from '@/state/store'
import type { DocStatus } from '@/types'

export default function StatusBar() {
  const {
    document,
    dirty,
    saveMarkdown,
    setStatus,
  } = useReviewStore()

  if (!document) {
    return <div className="h-10 border-t border-slate-200 bg-white" />
  }

  const status = document.meta.status
  const conf = (document.confidence * 100).toFixed(1)

  const canApprove = status === 'pending' || status === 'reviewed'
  const canReject = status !== 'rejected'

  return (
    <div className="flex h-12 items-center justify-between border-t border-slate-200 bg-white px-4">
      <div className="flex items-center gap-4 text-sm text-slate-600">
        <span>
          Status:{' '}
          <strong className="capitalize text-slate-800">{status}</strong>
        </span>
        <span>
          Confidence: <strong className="text-slate-800">{conf}%</strong>
        </span>
        <span>
          Blocks: <strong className="text-slate-800">{document.blocks.length}</strong>
        </span>
        {dirty && (
          <span className="rounded bg-amber-100 px-2 py-0.5 text-xs text-amber-800">
            unsaved changes
          </span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => saveMarkdown()}
          disabled={!dirty}
          className="rounded bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-200 disabled:opacity-40"
        >
          Save
        </button>

        {canReject && (
          <button
            onClick={() => setStatus('rejected')}
            className="rounded border border-red-200 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50"
          >
            Reject
          </button>
        )}

        {status === 'pending' && (
          <button
            onClick={() => setStatus('reviewed')}
            className="rounded bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
          >
            Mark Reviewed
          </button>
        )}

        {canApprove && (
          <button
            onClick={() => setStatus('approved')}
            className="rounded bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-700"
          >
            Approve
          </button>
        )}
      </div>
    </div>
  )
}
