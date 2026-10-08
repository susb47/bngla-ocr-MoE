import { useReviewStore } from '@/state/store'

export default function ConfidenceLegend() {
  const {
    showConfidence,
    setShowConfidence,
    confidenceThreshold,
    setConfidenceThreshold,
  } = useReviewStore()

  return (
    <div className="flex items-center gap-2 text-xs text-slate-600">
      <label className="flex items-center gap-1.5 cursor-pointer">
        <input
          type="checkbox"
          checked={showConfidence}
          onChange={(e) => setShowConfidence(e.target.checked)}
          className="rounded border-slate-300"
        />
        Confidence
      </label>
      {showConfidence && (
        <div className="flex items-center gap-1">
          <span className="text-slate-400">&lt;</span>
          <input
            type="range"
            min={0.4}
            max={0.95}
            step={0.05}
            value={confidenceThreshold}
            onChange={(e) =>
              setConfidenceThreshold(parseFloat(e.target.value))
            }
            className="w-20"
          />
          <span className="w-8 tabular-nums">
            {(confidenceThreshold * 100).toFixed(0)}%
          </span>
        </div>
      )}
    </div>
  )
}
