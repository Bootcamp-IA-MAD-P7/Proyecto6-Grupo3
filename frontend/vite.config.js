// ============================================================
//  vite.config.js — Configuración del bundler Vite
// ------------------------------------------------------------
//  QUÉ HACE: arranca el servidor de desarrollo y el build de
//  producción. El proxy '/api' redirige las llamadas del
//  frontend al backend de análisis (FastAPI/Flask) SIN tener
//  que cambiar código cuando el backend esté listo: basta con
//  ajustar el 'target' al puerto real del servidor de modelo.
// ============================================================
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Todas las llamadas a /api/* se reenvían al backend local.
      // TODO(backend): cambiar el target cuando el equipo de
      // datos despliegue el servicio de inferencia.
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
