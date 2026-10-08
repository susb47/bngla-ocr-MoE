import { useReviewStore } from '@/state/store'
import SourcePane from './SourcePane'
import MarkdownEditor from './MarkdownEditor'
import MarkdownPreview from './MarkdownPreview'

export default function SplitLayout() {
  const { document, loadingDoc, showDiff } = useReviewStore()

  if (loadingDoc) {
    return (
      <div className="flex flex-1 items-center justify-center text-slate-400">
        Loading document…
      </div>
    )
  }

  if (!document) {
    return (
      <div className="flex flex-1 items-center justify-center text-slate-400">
        Select a document from the queue
      </div>
    )
  }

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* Left: Source (PDF / page images) */}
      <div className="w-1/2 border-r border-slate-200 bg-slate-50">
        <SourcePane />
      </div>

      {/* Right: Markdown editor + optional preview / diff */}
      <div className="flex w-1/2 flex-col">
        {showDiff && document.original_markdown ? (
          <div className="flex flex-1 overflow-hidden">
            <div className="w-1/2 border-r border-slate-100">
              <div className="bg-slate-100 px-2 py-1 text-xs font-medium text-slate-500">
                Original OCR
              </div>
              <MarkdownPreview markdown={document.original_markdown} />
            </div>
            <div className="w-1/2">
              <div className="bg-slate-100 px-2 py-1 text-xs font-medium text-slate-500">
                Current
              </div>
              <MarkdownEditor />
            </div>
          </div>
        ) : (
          <MarkdownEditor />
        )}
      </div>
    </div>
  )
}
