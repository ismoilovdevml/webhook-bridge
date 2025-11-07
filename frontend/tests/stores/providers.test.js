import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mock the API service before importing the store
vi.mock('../../src/services/api', () => ({
  default: {
    getProviders: vi.fn(),
    createProvider: vi.fn(),
    updateProvider: vi.fn(),
    deleteProvider: vi.fn(),
    testProvider: vi.fn(),
  }
}))

import { useProvidersStore } from '../../src/stores/providers'
import api from '../../src/services/api'

describe('Providers Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('should initialize with empty providers array', () => {
    const store = useProvidersStore()
    expect(store.providers).toEqual([])
    expect(store.loading).toBe(false)
  })

  it('should fetch providers successfully', async () => {
    const mockProviders = [
      { id: 1, name: 'Telegram', type: 'telegram', enabled: true },
      { id: 2, name: 'Slack', type: 'slack', enabled: false }
    ]

    api.getProviders.mockResolvedValueOnce(mockProviders)

    const store = useProvidersStore()
    await store.fetchProviders()

    expect(store.providers).toEqual(mockProviders)
    expect(store.loading).toBe(false)
  })

  it('should handle fetch providers error', async () => {
    api.getProviders.mockRejectedValueOnce(new Error('Network error'))

    const store = useProvidersStore()
    await store.fetchProviders()

    expect(store.providers).toEqual([])
    expect(store.loading).toBe(false)
    expect(store.error).toBe('Network error')
  })
})
