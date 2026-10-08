import { useEffect, useRef } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { markdown } from '@codemirror/lang-markdown'
import { EditorView } from '@codemirror/view'
import { useReviewStore } from '@/state/store'
import { scrollToAnchor } from '@/state/sync'

export default function MarkdownEditor() {
  const {
    editBuffer,
    updateEditBuffer,
    selectedBlockId,
    document,
  } = useReviewStore()

  const containerRef = useRef<HTMLDivElement>(null)

  // When a block is selected on the PDF, scroll the editor to its anchor
  useEffect(() => {
    if (!selectedBlockId || !document) return
    const scroller = containerRef.current?.querySelector('.cm-scroller') as
      | HTMLElement
      | null
    scrollToAnchor(scroller, editBuffer, selectedBlockId)
  }, [selectedBlockId, document, editBuffer])

  return (
    <div ref={containerRef} className="h-full overflow-hidden">
      <CodeMirror
        value={editBuffer}
        height="100%"
        extensions={[
          markdown(),
          EditorView.lineWrapping,
          EditorView.theme({
            '&': { fontSize: '13.5px' },
            '.cm-content': { fontFamily: 'ui-monospace, monospace' },
          }),
        ]}
        onChange={(value) => updateEditBuffer(value)}
        basicSetup={{
          lineNumbers: true,
          foldGutter: true,
          highlightActiveLine: true,
        }}
      />
    </div>
  )
}
