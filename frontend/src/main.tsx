import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import App from './App'
import './index.css'

const ROOT_ELEMENT_ID = 'root'
const rootElement = document.getElementById(ROOT_ELEMENT_ID)

if (!rootElement) {
  throw new Error(`未找到应用挂载元素：${ROOT_ELEMENT_ID}`)
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
