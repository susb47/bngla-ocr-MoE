/** Shared types that mirror the backend Pydantic models (schema.py) */

export type BlockType =
  | 'heading'
  | 'paragraph'
  | 'list'
  | 'table'
  | 'figure'
  | 'header'
  | 'footer'
  | 'stamp'
  | 'handwriting'

export type DocStatus = 'pending' | 'reviewed' | 'approved' | 'rejected'

export type Volatility = 'stable' | 'semi' | 'volatile'

export interface Block {
  id: string
  page: number
  bbox: [number, number, number, number] // x0, y0, x1, y1 (normalized 0-1 or absolute px)
  type: BlockType
  text: string
  conf: number // 0-1
  engine: string
  flags: string[] // e.g. "garbled", "low-conf", "force-review"
}

export interface Meta {
  doc_id: string
  url: string | null
  agency: string
  retrieved_at: string // ISO
  sha256: string
  as_of: string | null
  volatility: Volatility
  status: DocStatus
}

export interface DocumentSummary {
  doc_id: string
  agency: string
  status: DocStatus
  page_count: number
  confidence: number // document-level avg
  title?: string
  retrieved_at: string
}

export interface DocumentDetail {
  meta: Meta
  markdown: string
  blocks: Block[]
  page_count: number
  confidence: number
  original_markdown?: string // for diff view
}

export interface PageInfo {
  page: number
  image_url: string // /api/docs/{id}/pages/{page}/image
  width: number
  height: number
  blocks: Block[]
}
