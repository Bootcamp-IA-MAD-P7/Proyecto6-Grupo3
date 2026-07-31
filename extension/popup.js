document.addEventListener('DOMContentLoaded', () => {
  // --- 1. Referencias a los elementos del DOM ---
  const luzRed = document.getElementById('luzRed');
  const luzYellow = document.getElementById('luzYellow');
  const luzGreen = document.getElementById('luzGreen');
  const statusBadge = document.getElementById('statusBadge');
  const statusText = document.getElementById('statusText');

  const siteAvatar = document.getElementById('siteAvatar');
  const siteTitle = document.getElementById('siteTitle');
  const siteUrl = document.getElementById('siteUrl');

  const iaSummaryBox = document.getElementById('iaSummaryBox');
  const exposureScoreEl = document.getElementById('exposureScore');
  const summaryContent = document.getElementById('summaryContent');
  const disclaimerTextEl = document.getElementById('disclaimerText');
  const categoriesContainer = document.getElementById('categoriesContainer');

  const evidenceQuote = document.getElementById('evidenceQuote');
  const evidenceSection = document.getElementById('evidenceSection');
  const evidenceLink = document.getElementById('evidenceLink');

  const retryBtn = document.getElementById('retryBtn');

  // Backend real desplegado en Render. Debe coincidir con host_permissions en manifest.json.
  const BACKEND_URL = 'https://privacylensproject.onrender.com';
  // Render free tier "duerme" el servicio tras un rato inactivo: la primera
  // petición que lo despierta puede tardar bastante más que una petición normal.
  const REQUEST_TIMEOUT_MS = 60000;

  // --- Mapeo de IDs de la API real a nombres e identificadores de CSS ---
  const categoryConfig = {
    'first_party_collection_use': { label: 'Data Collection/Usage', color: 'tag-darkblue' },
    'third_party_sharing_collection': { label: 'Third Party Sharing', color: 'tag-green' },
    'user_choice_control': { label: 'User Choice/Control', color: 'tag-yellow' },
    'user_access_edit_deletion': { label: 'User Access, Edit and Delete', color: 'tag-lightpurple' },
    'data_retention': { label: 'Data Retention', color: 'tag-lightpurple' },
    'data_security': { label: 'Data Security', color: 'tag-green' },
    'policy_change': { label: 'Policy Change', color: 'tag-yellow' },
    'do_not_track': { label: 'Do Not Track', color: 'tag-yellow' },
    'international_specific_audiences': { label: 'International & Specific Audiences', color: 'tag-darkblue' },
    'Other': { label: 'Otros', color: 'tag-darkblue' }
  };

  // Espejo de backend/app/exposure.py WEIGHTS: qué categoría domina el score,
  // para elegir el fragmento de evidencia más relevante (no simplemente el primero).
  const CATEGORY_WEIGHTS = {
    third_party_sharing_collection: 3.0,
    data_retention: 2.0,
    first_party_collection_use: 1.0,
    international_specific_audiences: 1.0,
    policy_change: 0.0,
    data_security: -1.0,
    user_choice_control: -1.0,
    user_access_edit_deletion: -1.0,
    do_not_track: 0.0,
    Other: 0.0
  };

  // --- 2. Dataset de demo (solo si el popup se abre fuera de Chrome, ej. previsualizando el HTML) ---
  const mockDataset = [
    {
      domain: 'Spotify',
      url: 'spotify.com/legal/privacy-policy',
      risk_level: 'medium',
      summary: 'El documento especifica recolección activa de datos de uso y compartición con socios publicitarios.',
      categories: [
        { label: 'Third Party Sharing', color: 'tag-green', confidence: 0.71 },
        { label: 'Data Collection/Usage', color: 'tag-darkblue', confidence: 0.65 }
      ],
      evidence: {
        quote: 'We share personal data with advertising partners to serve personalized content.',
        section: 'Third Party Sharing',
        link: 'https://spotify.com/legal/privacy-policy#section-3'
      }
    }
  ];

  // --- 3. Llamada al backend con timeout ---
  async function callBackend(payload) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    let response;
    try {
      response = await fetch(`${BACKEND_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal
      });
    } catch (error) {
      if (error.name === 'AbortError') {
        throw new Error('El backend tardó demasiado en responder (puede estar reactivándose en Render). Inténtalo de nuevo en unos segundos.');
      }
      throw new Error('No se pudo contactar con el backend. Comprueba tu conexión.');
    } finally {
      clearTimeout(timeoutId);
    }

    let data = null;
    try {
      data = await response.json();
    } catch (_) {
      // Respuesta sin cuerpo JSON (poco probable, pero no debe romper el flujo).
    }

    if (!response.ok) {
      return { ok: false, status: response.status, error: data?.error || `Error HTTP ${response.status}` };
    }
    return { ok: true, status: response.status, data };
  }

  // --- 4. Captura del texto ya renderizado de la pestaña activa (fallback para páginas JS-only) ---
  async function captureVisibleText(tabId) {
    const injectionResults = await chrome.scripting.executeScript({
      target: { tabId },
      func: () => document.body.innerText.replace(/\s+/g, ' ').trim()
    });
    return injectionResults[0]?.result || '';
  }

  // --- 5. Adaptador de la respuesta de FastAPI a la interfaz ---
  function buildSummary(exposureLevel, categories) {
    if (exposureLevel === 'unknown') {
      return 'No se encontraron suficientes fragmentos en esta página para estimar la exposición.';
    }
    const levelText = { high: 'alta', medium: 'media', low: 'baja' }[exposureLevel] || exposureLevel;
    const topCategories = categories.slice(0, 3).map((cat) => cat.label).join(', ');
    return topCategories
      ? `Exposición estimada: ${levelText}. Prácticas detectadas: ${topCategories}.`
      : `Exposición estimada: ${levelText}. No se detectaron prácticas de riesgo relevantes.`;
  }

  function adaptarRespuestaFastAPI(apiData, fallbackUrl) {
    const doc = apiData.document || {};
    const exposure = doc.exposure || {};
    const rawCategories = doc.categories || [];
    const fragments = apiData.fragments || [];

    const categoriesFiltered = rawCategories
      .filter((cat) => cat.present === true)
      .map((cat) => {
        const config = categoryConfig[cat.id] || { label: cat.id, color: 'tag-darkblue' };
        return { ...config, confidence: cat.confidence || 0 };
      });

    // Evidencia: el fragmento más fuerte de la categoría con más peso en el score de exposición,
    // no simplemente el primer párrafo del documento.
    const dominantCategory = rawCategories
      .filter((cat) => cat.present && CATEGORY_WEIGHTS[cat.id])
      .sort((a, b) => Math.abs(CATEGORY_WEIGHTS[b.id]) - Math.abs(CATEGORY_WEIGHTS[a.id]))[0];

    let topFragment = dominantCategory
      ? fragments
          .filter((f) => f.labels?.[0]?.id === dominantCategory.id)
          .sort((a, b) => (b.labels[0].score || 0) - (a.labels[0].score || 0))[0]
      : null;

    if (!topFragment) {
      topFragment = [...fragments].sort(
        (a, b) => (b.labels?.[0]?.score || 0) - (a.labels?.[0]?.score || 0)
      )[0] || {};
    }

    const topLabel = topFragment.labels?.[0]?.id || '';
    const sectionName = categoryConfig[topLabel]?.label || 'Cláusula relevante';
    const level = exposure.level || 'low';

    return {
      risk_level: level,
      score: typeof exposure.score === 'number' ? exposure.score : null,
      disclaimer: exposure.disclaimer || '',
      summary: buildSummary(level, categoriesFiltered),
      categories: categoriesFiltered,
      evidence: {
        quote: topFragment.text && topFragment.text !== 'string'
          ? topFragment.text
          : 'No hay fragmentos suficientes para mostrar evidencia.',
        section: sectionName,
        link: fallbackUrl
      }
    };
  }

  // --- 6. Flujo principal del popup ---
  async function init() {
    const isExtensionContext = typeof chrome !== 'undefined' && !!chrome.tabs;
    let currentTab = null;

    if (isExtensionContext) {
      try {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab && tab.url) {
          currentTab = tab;
          const urlObj = new URL(tab.url);

          if (siteTitle) siteTitle.textContent = tab.title ? tab.title.split(' - ')[0] : urlObj.hostname;
          if (siteUrl) {
            siteUrl.textContent = urlObj.hostname + urlObj.pathname;
            siteUrl.href = tab.url;
          }
        }
      } catch (e) {
        console.warn('No se pudo leer la pestaña de Chrome:', e);
      }
    }

    if (!currentTab) {
      mostrarDemo();
      return;
    }

    const targetUrl = currentTab.url;
    if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
      mostrarError('Esta pestaña no es una página web (http/https); no se puede analizar.');
      return;
    }

    if (statusBadge) statusBadge.classList.remove('error');
    if (retryBtn) retryBtn.style.display = 'none';
    if (statusText) statusText.textContent = 'Analizando...';

    // El backend en Render "duerme" tras un rato inactivo: si la primera respuesta
    // tarda, avisamos en vez de dejar el popup en un "Analizando..." mudo.
    const startedAt = Date.now();
    const waitHintId = setInterval(() => {
      const seconds = Math.round((Date.now() - startedAt) / 1000);
      if (statusText) statusText.textContent = `Analizando... (${seconds}s, el servidor puede estar despertando)`;
    }, 8000);

    try {
      // 1er intento: el backend descarga y limpia la página él mismo (misma lógica robusta
      // que usa el resto del proyecto, con guardas SSRF y extracción por párrafos).
      let result = await callBackend({ url: targetUrl });

      // Si el backend no pudo leer suficiente texto (típico de páginas que renderizan con JS),
      // usamos el texto que el navegador ya tiene pintado en la pestaña como fallback.
      if (!result.ok && result.status === 422) {
        if (statusText) statusText.textContent = 'Contenido dinámico detectado, leyendo la página...';
        const capturedText = await captureVisibleText(currentTab.id);
        if (!capturedText) {
          throw new Error('No se pudo leer texto visible en esta página.');
        }
        result = await callBackend({ url: targetUrl, text: capturedText });
      }

      if (!result.ok) {
        throw new Error(result.error || `Error HTTP ${result.status}`);
      }

      const uiData = adaptarRespuestaFastAPI(result.data, targetUrl);
      actualizarInterfaz(uiData);
    } catch (error) {
      console.error('No se pudo completar el análisis:', error);
      mostrarError(error.message || 'No se pudo contactar con el backend.');
    } finally {
      clearInterval(waitHintId);
    }
  }

  // --- 7. Funciones de renderizado ---
  function actualizarInterfaz(data) {
    if (statusBadge) statusBadge.classList.remove('error');
    if (retryBtn) retryBtn.style.display = 'none';
    if (statusText) statusText.textContent = '✓ Analizado';

    if (summaryContent) summaryContent.textContent = data.summary || '';
    if (disclaimerTextEl) disclaimerTextEl.textContent = data.disclaimer || '';
    if (exposureScoreEl) {
      exposureScoreEl.textContent = typeof data.score === 'number' ? `score ${data.score.toFixed(2)}` : '';
    }

    const risk = (data.risk_level || 'low').toLowerCase();
    setSemaforo(risk);

    if (data.evidence) {
      if (evidenceQuote) evidenceQuote.textContent = `"${data.evidence.quote || ''}"`;
      if (evidenceSection) evidenceSection.textContent = data.evidence.section || 'Sección';
      if (evidenceLink && data.evidence.link) evidenceLink.href = data.evidence.link;
    }

    if (data.categories && Array.isArray(data.categories)) {
      renderCategories(data.categories);
    }
  }

  function mostrarError(message) {
    if (statusBadge) statusBadge.classList.add('error');
    if (retryBtn) retryBtn.style.display = 'block';
    if (statusText) statusText.textContent = '⚠ Error';

    if (luzRed && luzYellow && luzGreen) {
      luzRed.className = 'luz red disabled';
      luzYellow.className = 'luz yellow disabled';
      luzGreen.className = 'luz green disabled';
    }
    if (iaSummaryBox) {
      iaSummaryBox.classList.remove('risk-high', 'risk-medium', 'risk-low');
      iaSummaryBox.classList.add('risk-error');
    }

    if (summaryContent) summaryContent.textContent = message;
    if (disclaimerTextEl) disclaimerTextEl.textContent = '';
    if (exposureScoreEl) exposureScoreEl.textContent = '';
    if (categoriesContainer) categoriesContainer.innerHTML = '';
    if (evidenceQuote) evidenceQuote.textContent = '';
    if (evidenceSection) evidenceSection.textContent = '';
  }

  function mostrarDemo() {
    const mockData = mockDataset[0];
    if (siteTitle) siteTitle.textContent = `${mockData.domain} (demo)`;
    if (siteUrl) {
      siteUrl.textContent = mockData.url;
      siteUrl.href = `https://${mockData.url}`;
    }
    if (statusText) statusText.textContent = 'Demo (fuera de la extensión)';

    actualizarInterfaz({
      risk_level: mockData.risk_level,
      score: null,
      disclaimer: 'Datos de ejemplo: esta vista no se está ejecutando dentro de la extensión de Chrome.',
      summary: mockData.summary,
      categories: mockData.categories,
      evidence: mockData.evidence
    });
  }

  function setSemaforo(level) {
    if (!luzRed || !luzYellow || !luzGreen || !iaSummaryBox) return;

    luzRed.className = 'luz red disabled';
    luzYellow.className = 'luz yellow disabled';
    luzGreen.className = 'luz green disabled';

    iaSummaryBox.classList.remove('risk-high', 'risk-medium', 'risk-low', 'risk-error');

    if (level === 'high' || level === 'alto') {
      luzRed.className = 'luz red active';
      iaSummaryBox.classList.add('risk-high');
    } else if (level === 'medium' || level === 'medio') {
      luzYellow.className = 'luz yellow active';
      iaSummaryBox.classList.add('risk-medium');
    } else if (level === 'low' || level === 'bajo') {
      luzGreen.className = 'luz green active';
      iaSummaryBox.classList.add('risk-low');
    } else {
      // 'unknown': la página no tenía fragmentos suficientes para estimar exposición.
      iaSummaryBox.classList.add('risk-error');
    }
  }

  function renderCategories(categories) {
    if (!categoriesContainer) return;
    categoriesContainer.innerHTML = '';

    if (categories.length === 0) {
      const tag = document.createElement('span');
      tag.className = 'tag-category-styled tag-darkblue';
      tag.innerHTML = `<span class="dot-styled"></span>Sin cláusulas críticas`;
      categoriesContainer.appendChild(tag);
      return;
    }

    categories.forEach((cat) => {
      const tag = document.createElement('span');
      const labelText = typeof cat === 'string' ? cat : cat.label;
      const colorClass = typeof cat === 'string' ? 'tag-darkblue' : cat.color;
      const confidenceText =
        typeof cat === 'object' && typeof cat.confidence === 'number'
          ? ` ${Math.round(cat.confidence * 100)}%`
          : '';

      tag.className = `tag-category-styled ${colorClass}`;
      tag.innerHTML = `<span class="dot-styled"></span>${labelText}${confidenceText}`;
      categoriesContainer.appendChild(tag);
    });
  }

  if (retryBtn) {
    retryBtn.addEventListener('click', () => {
      retryBtn.style.display = 'none';
      init();
    });
  }

  init();
});
