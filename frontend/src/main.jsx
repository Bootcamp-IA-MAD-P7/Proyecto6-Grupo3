// ============================================================
//  main.jsx — Punto de arranque de React
// ------------------------------------------------------------
//  QUÉ HACE: importa los estilos globales (¡el orden importa:
//  primero tokens, luego global!) y monta <App /> en el DOM.
// ============================================================
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'

import './styles/tokens.css' // 1º: variables de diseño
import './styles/global.css' // 2º: estilos base que las usan

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
