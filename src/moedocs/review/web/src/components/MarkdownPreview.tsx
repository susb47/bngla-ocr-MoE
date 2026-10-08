import { useMemo } from 'react'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true,
})

interface Props {
  markdown: string
}

export default function MarkdownPreview({ markdown }: Props) {
  const html = useMemo(() => md.render(markdown), [markdown])

  return (
    <div
      className="prose prose-sm max-w-none overflow-auto p-4 text-slate-800"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
