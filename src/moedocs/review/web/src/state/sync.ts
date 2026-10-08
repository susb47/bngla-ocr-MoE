/**
 * Helpers that keep the editor and the PDF pane in sync.
 *
 * Anchors in the Markdown look like:  <!-- b:12 -->
 * When the user clicks a block on the PDF we scroll the editor to that anchor.
 * When the user places the cursor near an anchor we highlight the corresponding
 * bbox on the PDF.
 */

/** Extract all block anchors from markdown text */
export function extractAnchors(markdown: string): Map<string, number> {
  const map = new Map<string, number>()
  const re = /<!--\s*b:(\w+)\s*-->/g
  let match: RegExpExecArray | null
  while ((match = re.exec(markdown)) !== null) {
    map.set(match[1], match.index)
  }
  return map
}

/** Find the nearest block id to a given character offset in the markdown */
export function blockIdAtOffset(
  markdown: string,
  offset: number
): string | null {
  const anchors = extractAnchors(markdown)
  let bestId: string | null = null
  let bestDist = Infinity

  for (const [id, pos] of anchors) {
    const dist = Math.abs(pos - offset)
    if (dist < bestDist) {
      bestDist = dist
      bestId = id
    }
  }
  // only consider it "near" if within 200 chars
  return bestDist < 200 ? bestId : null
}

/** Scroll a CodeMirror-like editor (or plain textarea) to an anchor */
export function scrollToAnchor(
  container: HTMLElement | null,
  markdown: string,
  blockId: string
) {
  if (!container) return
  const anchors = extractAnchors(markdown)
  const pos = anchors.get(blockId)
  if (pos === undefined) return

  // Approximate line from character offset
  const linesBefore = markdown.slice(0, pos).split('\n').length - 1
  const lineHeight = 22 // approximate
  container.scrollTop = Math.max(0, linesBefore * lineHeight - 80)
}
