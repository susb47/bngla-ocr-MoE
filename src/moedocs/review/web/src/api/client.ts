/**
 * Thin API client that talks to the FastAPI review backend.
 * All paths are relative so the Vite proxy (/api → localhost:8000) works in dev.
 */

import type {
  DocumentSummary,
  DocumentDetail,
  PageInfo,
  Block,
  DocStatus,
} from '@/types'

const BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!res.ok) {
    const body = await res.text()
    throw new Error(`API ${res.status}: ${body || res.statusText}`)
  }

  // 204 No Content
  if (res.status === 204) return undefined as T
  return res.json()
}

// ---------------------------------------------------------------------------
// Documents
// ---------------------------------------------------------------------------

export async function listDocuments(params?: {
  status?: DocStatus
  agency?: string
}): Promise<DocumentSummary[]> {
  const q = new URLSearchParams()
  if (params?.status) q.set('status', params.status)
  if (params?.agency) q.set('agency', params.agency)
  const query = q.toString() ? `?${q}` : ''
  return request(`/docs${query}`)
}

export async function getDocument(docId: string): Promise<DocumentDetail> {
  return request(`/docs/${docId}`)
}

export async function getPage(
  docId: string,
  page: number
): Promise<PageInfo> {
  return request(`/docs/${docId}/pages/${page}`)
}

/** Returns the URL for the page image (used by <img> or pdf.js) */
export function pageImageUrl(docId: string, page: number): string {
  return `${BASE}/docs/${docId}/pages/${page}/image`
}

// ---------------------------------------------------------------------------
// Editing
// ---------------------------------------------------------------------------

export async function updateBlock(
  docId: string,
  blockId: string,
  patch: Partial<Pick<Block, 'text' | 'type' | 'flags'>>
): Promise<Block> {
  return request(`/docs/${docId}/blocks/${blockId}`, {
    method: 'PATCH',
    body: JSON.stringify(patch),
  })
}

export async function updateMarkdown(
  docId: string,
  markdown: string
): Promise<{ markdown: string }> {
  return request(`/docs/${docId}/markdown`, {
    method: 'PUT',
    body: JSON.stringify({ markdown }),
  })
}

export async function setStatus(
  docId: string,
  status: DocStatus
): Promise<{ status: DocStatus }> {
  return request(`/docs/${docId}/status`, {
    method: 'POST',
    body: JSON.stringify({ status }),
  })
}

export async function getDiff(docId: string): Promise<{
  original: string
  current: string
}> {
  return request(`/docs/${docId}/diff`)
}
