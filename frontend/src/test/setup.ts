import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Vitest 未启用全局 afterEach，需显式清理每个用例的 React 页面。
afterEach(cleanup)

// Ant Design 响应式观察依赖 matchMedia，jsdom 需提供最小桩。
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false,
  }),
})

// jsdom 缺少 getComputedStyle 的部分属性时，Ant Design 可能警告。
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
// @ts-expect-error jsdom 全局补齐
window.ResizeObserver = ResizeObserverStub
