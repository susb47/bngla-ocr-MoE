import type { Block } from '@/types'

interface Props {
  blocks: Block[]
  selectedBlockId: string | null
  onSelect: (id: string | null) => void
  showConfidence: boolean
  confidenceThreshold: number
  imgWidth: number
  imgHeight: number
}

/**
 * Renders absolute-positioned rectangles over the page image.
 * bbox is expected as [x0, y0, x1, y1] in the same coordinate space
 * as the rendered image (pixels). If the backend stores normalized
 * coords (0-1) we scale them here.
 */
export default function BlockOverlay({
  blocks,
  selectedBlockId,
  onSelect,
  showConfidence,
  confidenceThreshold,
  imgWidth,
  imgHeight,
}: Props) {
  return (
    <div className="pointer-events-none absolute inset-0">
      {blocks.map((block) => {
        let [x0, y0, x1, y1] = block.bbox

        // Support both normalized (0-1) and absolute pixel bboxes
        if (x1 <= 1.01 && y1 <= 1.01) {
          x0 *= imgWidth
          y0 *= imgHeight
          x1 *= imgWidth
          y1 *= imgHeight
        }

        const isSelected = block.id === selectedBlockId
        const isLowConf =
          showConfidence && block.conf < confidenceThreshold

        const className = [
          'block-overlay pointer-events-auto absolute cursor-pointer border-2',
          isSelected ? 'selected' : '',
          isLowConf ? 'low-conf' : 'border-transparent',
        ]
          .filter(Boolean)
          .join(' ')

        return (
          <div
            key={block.id}
            className={className}
            style={{
              left: x0,
              top: y0,
              width: x1 - x0,
              height: y1 - y0,
            }}
            title={`${block.type} · conf ${(block.conf * 100).toFixed(0)}% · ${block.engine}`}
            onClick={(e) => {
              e.stopPropagation()
              onSelect(isSelected ? null : block.id)
            }}
          />
        )
      })}
    </div>
  )
}
