import { useEffect, useRef, useState } from 'react'
import { useReviewStore } from '@/state/store'
import { pageImageUrl } from '@/api/client'
import BlockOverlay from './BlockOverlay'

/**
 * Shows one page at a time as an image (rendered by the backend).
 * Block bounding boxes are overlaid and clickable.
 *
 * Future: can be swapped for full pdf.js multi-page viewer.
 */
export default function SourcePane() {
  const {
    document,
    currentPage,
    setPage,
    selectedBlockId,
    selectBlock,
    showConfidence,
    confidenceThreshold,
  } = useReviewStore()

  const containerRef = useRef<HTMLDivElement>(null)
  const [imgSize, setImgSize] = useState({ w: 0, h: 0 })

  if (!document) return null

  const pageCount = document.page_count
  const pageBlocks = document.blocks.filter((b) => b.page === currentPage)
  const imgUrl = pageImageUrl(document.meta.doc_id, currentPage)

  return (
    <div className="flex h-full flex-col">
      {/* Page navigator */}
      <div className="flex items-center justify-between border-b border-slate-200 bg-white px-3 py-1.5">
        <button
          disabled={currentPage <= 1}
          onClick={() => setPage(currentPage - 1)}
          className="rounded px-2 py-0.5 text-sm text-slate-600 hover:bg-slate-100 disabled:opacity-30"
        >
          ← Prev
        </button>
        <span className="text-sm text-slate-600">
          Page {currentPage} / {pageCount}
        </span>
        <button
          disabled={currentPage >= pageCount}
          onClick={() => setPage(currentPage + 1)}
          className="rounded px-2 py-0.5 text-sm text-slate-600 hover:bg-slate-100 disabled:opacity-30"
        >
          Next →
        </button>
      </div>

      {/* Image + overlays */}
      <div
        ref={containerRef}
        className="relative flex-1 overflow-auto bg-slate-200/60"
      >
        <div className="relative inline-block min-w-full">
          <img
            src={imgUrl}
            alt={`Page ${currentPage}`}
            className="max-w-full"
            onLoad={(e) => {
              const img = e.currentTarget
              setImgSize({ w: img.naturalWidth, h: img.naturalHeight })
            }}
          />
          {imgSize.w > 0 && (
            <BlockOverlay
              blocks={pageBlocks}
              selectedBlockId={selectedBlockId}
              onSelect={selectBlock}
              showConfidence={showConfidence}
              confidenceThreshold={confidenceThreshold}
              imgWidth={imgSize.w}
              imgHeight={imgSize.h}
            />
          )}
        </div>
      </div>
    </div>
  )
}
