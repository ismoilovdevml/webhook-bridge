import { describe, it, expect } from 'vitest'

// Simple date formatter test
describe('Date Formatting', () => {
  it('should format ISO date string', () => {
    const isoDate = '2025-11-07T16:30:00Z'
    const date = new Date(isoDate)

    expect(date).toBeInstanceOf(Date)
    expect(date.getFullYear()).toBe(2025)
    expect(date.getMonth()).toBe(10) // November (0-indexed)
    expect(date.getDate()).toBe(7)
  })

  it('should handle invalid date strings', () => {
    const invalidDate = new Date('invalid')

    expect(isNaN(invalidDate.getTime())).toBe(true)
  })

  it('should create current date', () => {
    const now = new Date()

    expect(now).toBeInstanceOf(Date)
    expect(now.getTime()).toBeGreaterThan(0)
  })
})
