import { create } from 'zustand'
import type {
  DocumentSummary,
  DocumentDetail,
  Block,
  DocStatus,
} from '@/types'
import * as api from '@/api/client'

interface ReviewState {
  // Queue
  documents: DocumentSummary[]
  loadingList: boolean

  // Current document
  currentDocId: string | null
  document: DocumentDetail | null
  loadingDoc: boolean

  // UI state
  currentPage: number
  selectedBlockId: string | null
  showDiff: boolean
  showConfidence: boolean
  confidenceThreshold: number // highlight blocks below this
  editBuffer: string // current markdown being edited
  dirty: boolean
  error: string | null

  // Actions
  loadDocuments: (status?: DocStatus) => Promise<void>
  selectDocument: (docId: string) => Promise<void>
  setPage: (page: number) => void
  selectBlock: (blockId: string | null) => void
  setShowDiff: (v: boolean) => void
  setShowConfidence: (v: boolean) => void
  setConfidenceThreshold: (v: number) => void
  updateEditBuffer: (md: string) => void
  saveMarkdown: () => Promise<void>
  updateBlockText: (blockId: string, text: string) => Promise<void>
  setStatus: (status: DocStatus) => Promise<void>
  clearError: () => void
}

export const useReviewStore = create<ReviewState>((set, get) => ({
  documents: [],
  loadingList: false,
  currentDocId: null,
  document: null,
  loadingDoc: false,
  currentPage: 1,
  selectedBlockId: null,
  showDiff: false,
  showConfidence: true,
  confidenceThreshold: 0.75,
  editBuffer: '',
  dirty: false,
  error: null,

  loadDocuments: async (status) => {
    set({ loadingList: true, error: null })
    try {
      const docs = await api.listDocuments({ status })
      set({ documents: docs, loadingList: false })
    } catch (e) {
      set({
        loadingList: false,
        error: e instanceof Error ? e.message : 'Failed to load documents',
      })
    }
  },

  selectDocument: async (docId) => {
    set({
      loadingDoc: true,
      currentDocId: docId,
      selectedBlockId: null,
      currentPage: 1,
      dirty: false,
      error: null,
    })
    try {
      const doc = await api.getDocument(docId)
      set({
        document: doc,
        editBuffer: doc.markdown,
        loadingDoc: false,
      })
    } catch (e) {
      set({
        loadingDoc: false,
        error: e instanceof Error ? e.message : 'Failed to load document',
      })
    }
  },

  setPage: (page) => set({ currentPage: page, selectedBlockId: null }),

  selectBlock: (blockId) => set({ selectedBlockId: blockId }),

  setShowDiff: (v) => set({ showDiff: v }),

  setShowConfidence: (v) => set({ showConfidence: v }),

  setConfidenceThreshold: (v) => set({ confidenceThreshold: v }),

  updateEditBuffer: (md) => set({ editBuffer: md, dirty: true }),

  saveMarkdown: async () => {
    const { currentDocId, editBuffer } = get()
    if (!currentDocId) return
    try {
      await api.updateMarkdown(currentDocId, editBuffer)
      set((s) => ({
        dirty: false,
        document: s.document
          ? { ...s.document, markdown: editBuffer }
          : null,
      }))
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : 'Save failed',
      })
    }
  },

  updateBlockText: async (blockId, text) => {
    const { currentDocId, document } = get()
    if (!currentDocId || !document) return
    try {
      const updated = await api.updateBlock(currentDocId, blockId, { text })
      // also patch local state
      const newBlocks = document.blocks.map((b) =>
        b.id === blockId ? updated : b
      )
      set({
        document: { ...document, blocks: newBlocks },
      })
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : 'Block update failed',
      })
    }
  },

  setStatus: async (status) => {
    const { currentDocId } = get()
    if (!currentDocId) return
    try {
      await api.setStatus(currentDocId, status)
      set((s) => ({
        document: s.document
          ? {
              ...s.document,
              meta: { ...s.document.meta, status },
            }
          : null,
        documents: s.documents.map((d) =>
          d.doc_id === currentDocId ? { ...d, status } : d
        ),
      }))
    } catch (e) {
      set({
        error: e instanceof Error ? e.message : 'Status change failed',
      })
    }
  },

  clearError: () => set({ error: null }),
}))
