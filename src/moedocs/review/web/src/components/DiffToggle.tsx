import { useReviewStore } from '@/state/store'

export default function DiffToggle() {
  const { showDiff, setShowDiff, document } = useReviewStore()

  if (!document?.original_markdown) return null

  return (
    <label className="flex items-center gap-1.5 text-xs text-slate-600 cursor-pointer">
      <input
        type="checkbox"
        checked={showDiff}
        onChange={(e) => setShowDiff(e.target.checked)}
        className="rounded border-slate-300"
      />
      Show OCR Diff
    </label>
  )
}
