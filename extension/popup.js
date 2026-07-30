document.addEventListener('DOMContentLoaded', async () => {
  // --- 1. Referencias a los elementos del DOM ---
  const luzRed = document.getElementById('luzRed');
  const luzYellow = document.getElementById('luzYellow');
  const luzGreen = document.getElementById('luzGreen');
  const statusText = document.getElementById('statusText');

  const siteAvatar = document.getElementById('siteAvatar');
  const siteTitle = document.getElementById('siteTitle');
  const siteUrl = document.getElementById('siteUrl');

  const iaSummaryBox = document.getElementById('iaSummaryBox');
  const summaryContent = document.getElementById('summaryContent');
  const categoriesContainer = document.getElementById('categoriesContainer');

  const evidenceQuote = document.getElementById('evidenceQuote');
  const evidenceSection = document.getElementById('evidenceSection');
  const evidenceLink = document.getElementById('evidenceLink');

  const dashboardBtn = document.getElementById('dashboardBtn');

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

  // --- 2. Dataset Mockout (Fallback si el backend falla) ---
  const mockDataset = [
    {
      domain: 'Spotify',
      url: 'spotify.com/legal/privacy-policy',
      risk_level: 'medium',
      summary: 'El documento especifica recolección activa de datos de uso y compartición con socios publicitarios.',
      categories: [{ label: 'Third Party Sharing', color: 'tag-green' }, { label: 'Data Collection/Usage', color: 'tag-darkblue' }],
      evidence: {
        quote: 'We share personal data with advertising partners to serve personalized content.',
        section: 'Third Party Sharing',
        link: 'https://spotify.com/legal/privacy-policy#section-3'
      }
    }
  ];

  // --- 3. Event listener para el botón de Dashboard ---
  if (dashboardBtn) {
    dashboardBtn.addEventListener('click', () => {
      const dashboardUrl = 'http://127.0.0.1:8001/dashboard';
      if (typeof chrome !== 'undefined' && chrome.tabs) {
        chrome.tabs.create({ url: dashboardUrl });
      } else {
        window.open(dashboardUrl, '_blank');
      }
    });
  }

  // --- 4. Adaptador de la API de FastAPI a la Interfaz ---
  function adaptarRespuestaFastAPI(apiData, fallbackUrl) {
    const doc = apiData.document || {};
    const exposure = doc.exposure || {};
    const rawCategories = doc.categories || [];
    const fragments = apiData.fragments || [];

    // Extraer solo categorías donde present === true
    const categoriesFiltered = rawCategories
      .filter(cat => cat.present === true)
      .map(cat => categoryConfig[cat.id] || { label: cat.id, color: 'tag-darkblue' });

    // Extraer la primera evidencia disponible en los fragmentos
    const topFragment = fragments[0] || {};
    const topLabel = topFragment.labels?.[0]?.id || '';
    const sectionName = categoryConfig[topLabel]?.label || 'Cláusula relevante';

    return {
      risk_level: exposure.level || 'low',
      summary: exposure.disclaimer || 'Análisis completado en función de las cláusulas detectadas.',
      categories: categoriesFiltered,
      evidence: {
        quote: topFragment.text && topFragment.text !== 'string' ? topFragment.text : 'Extracto relevante analizado por la IA.',
        section: sectionName,
        link: fallbackUrl
      }
    };
  }

  // --- 5. Flujo principal del popup ---
  async function init() {
    let currentTab = null;

    if (typeof chrome !== 'undefined' && chrome.tabs) {
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

    if (statusText) statusText.textContent = 'Analizando...';

    try {
      if (!currentTab) throw new Error('Modo fuera de extensión de Chrome');

      // Validar esquema HTTP/HTTPS para evitar errores de fetch
      let targetUrl = currentTab.url;
      if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
        targetUrl = 'https://example.com/privacy';
      }
      console.log('📤 Enviando petición a FastAPI...', { url: targetUrl });
      const response = await fetch('http://127.0.0.1:8001/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: targetUrl,
          text: currentTab.title || 'Solicitud desde extensión'
        })
      });

      if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);

      const apiData = await response.json();
      console.log('🚀 ¡RESPUESTA RECIBIDA DEL BACKEND!', apiData);
      const uiData = adaptarRespuestaFastAPI(apiData, targetUrl);
      console.log('🎨 Datos adaptados para la UI:', uiData);
      actualizarInterfaz(uiData);

    } catch (error) {
      console.warn('Backend inalcanzable o error de fetch. Usando datos de respaldo...', error);
      
      setTimeout(() => {
        const mockData = mockDataset[0];
        if (!currentTab && siteTitle && siteUrl) {
          siteTitle.textContent = mockData.domain;
          siteUrl.textContent = mockData.url;
          siteUrl.href = `https://${mockData.url}`;
        }
        actualizarInterfaz(mockData);
      }, 500);
    }
  }

  // --- 6. Funciones de Renderizado ---
  function actualizarInterfaz(data) {
    if (statusText) statusText.textContent = '✓ Analizado';

    if (summaryContent && data.summary) {
      summaryContent.textContent = data.summary;
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

  function setSemaforo(level) {
    if (!luzRed || !luzYellow || !luzGreen || !iaSummaryBox) return;

    luzRed.className = 'luz red disabled';
    luzYellow.className = 'luz yellow disabled';
    luzGreen.className = 'luz green disabled';

    iaSummaryBox.classList.remove('risk-high', 'risk-medium', 'risk-low');

    if (level === 'high' || level === 'alto') {
      luzRed.className = 'luz red active';
      iaSummaryBox.classList.add('risk-high');
    } else if (level === 'medium' || level === 'medio') {
      luzYellow.className = 'luz yellow active';
      iaSummaryBox.classList.add('risk-medium');
    } else {
      luzGreen.className = 'luz green active';
      iaSummaryBox.classList.add('risk-low');
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

      tag.className = `tag-category-styled ${colorClass}`;
      tag.innerHTML = `<span class="dot-styled"></span>${labelText}`;
      categoriesContainer.appendChild(tag);
    });
  }

  init();
});