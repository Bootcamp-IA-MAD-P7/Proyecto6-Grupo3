// ============================================================
//  Logo.jsx — Logotipo de PrivacyLens ("La L que es lente")
// ------------------------------------------------------------
//  QUÉ HACE: dibuja el logo aprobado por el equipo como SVG
//  inline, para que sea nítido a cualquier tamaño y herede
//  los colores de los tokens.
//
//  PROPS:
//   · size      (number)  alto/ancho en px. Por defecto 32.
//   · variant   ('color' | 'light')
//               'color' → azul petróleo + turquesa (fondos claros)
//               'light' → blanco + turquesa (fondos oscuros)
//   · wordmark  (bool)    si true, añade el texto "PrivacyLens"
//                         a la derecha del símbolo.
//
//  EJEMPLO:
//   <Logo size={40} wordmark />          → cabecera
//   <Logo size={128} />                  → página "about"
//   <Logo variant="light" wordmark />    → footer oscuro
// ============================================================

export default function Logo({ size = 32, variant = 'color', wordmark = false }) {
  // En modo 'light' la "L" pasa de azul petróleo a blanco.
  const colorL = variant === 'light' ? '#FFFFFF' : '#1D3557'
  const colorLens = '#2A9D8F' // turquesa = "la voz de la IA" (siempre)

  return (
    <span className="logo" style={{ display: 'inline-flex', alignItems: 'center', gap: 10 }}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        role="img"
        aria-label="Logotipo de PrivacyLens"
      >
        {/* La "L" de Lens… */}
        <path
          d="M22 12 v34 h13"
          stroke={colorL}
          strokeWidth="7"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        {/* …que termina convertida en una lupa */}
        <circle cx="45" cy="41" r="9" fill="none" stroke={colorLens} strokeWidth="4" />
        <line x1="51.5" y1="47.5" x2="58" y2="54" stroke={colorLens} strokeWidth="4" strokeLinecap="round" />
      </svg>

      {wordmark && (
        <span
          style={{
            fontFamily: 'var(--font-display)',
            fontWeight: 800,
            fontSize: size * 0.62,
            color: colorL,
            letterSpacing: '-0.5px',
          }}
        >
          Privacy<em style={{ fontStyle: 'normal', color: colorLens }}>Lens</em>
        </span>
      )}
    </span>
  )
}
