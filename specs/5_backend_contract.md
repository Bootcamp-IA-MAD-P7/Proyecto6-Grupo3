# SPEC 5 — Contrato del backend

**Proyecto:** Clasificador de politicas de privacidad — Proyecto 6, Grupo 3
**Version:** 1.0 (26 de julio de 2026)

> ⚠️ AVISO PARA ASISTENTES DE IA — LEER ANTES DE ACTUAR
> El backend de este documento YA ESTA IMPLEMENTADO y en funcionamiento en backend/.
> Este archivo es documentacion de referencia, NO una orden de construccion.
> - NO generes un backend nuevo, ni un main.py, ni endpoints, a partir de esta spec.
> - NO asumas que el backend no existe porque no lo veas en tu contexto: existe en el
>   repo. Comprueba backend/ antes de concluir nada.
> - Si te piden cambios en el backend, parte del codigo REAL existente y edítalo.
> - Si el codigo existente contradice esta spec, NO lo reescribas: reporta la
>   discrepancia y pregunta. Manda el codigo real + 2_spec, no este resumen.
> Reconstruir el backend por tu cuenta destruiria trabajo hecho. Ante la duda, para y pregunta.

> Este documento existe para **una** cosa: que Claude Code (o cualquier asistente)
> monte el backend sin inventarse ninguna decision. Todo lo que aqui aparece esta
> decidido por el equipo; lo que no cierra la logica final (semaforo, mapeo RGPD)
> se deja como hueco previsto detras de una interfaz estable, no sin resolver.
>
> El contrato de SALIDA (el JSON) es el del `2_spec` §9. El de DATOS/modelo es el
> `4_data_contract.md`. Este documento manda sobre la API; si algo choca con `2_spec`,
> manda `2_spec` y se corrige aqui.

---

## Por que hace falta

El backend se monta con un *stub* (datos inventados) ANTES de que exista el modelo,
para congelar el contrato y que el frontend se construya en paralelo. El dia que exista
el modelo se reemplaza una funcion; la forma de la respuesta no cambia. Diseñado para
**nivel experto desde el principio**: el contrato completo y todas las capas (traduccion,
semaforo, RGPD, scraper) cableadas detras de interfaces sustituibles, aunque su logica
llegue despues o nunca.

---

## Bloque para pegar en Claude Code

```
CONTEXTO
Backend de PrivacyLens: una API que recibe el texto de una politica de privacidad,
la clasifica en 9 categorias (multi-etiqueta) y devuelve el contrato del 2_spec §9.
El frontend es una web React + Vite (PrivacyLens) que YA existe como andamiaje (sin
codigo de app todavia); consume esta API. Entorno: uv + Python 3.12. Ejecutar con
`uv run ...` desde la raiz del repo. El codigo va en backend/.

STACK
- FastAPI + uvicorn, en el mismo entorno uv que el modelo.
- uvicorn escucha en el PUERTO 8000 (obligatorio: el proxy de Vite del frontend
  ya apunta a http://localhost:8000; ver frontend/vite.config.js).

ENDPOINTS (bajo el prefijo /api; el proxy de Vite reenvia /api/* sin quitar el prefijo)
- POST /api/analyze  -> recibe el texto, devuelve el contrato del §9.
- GET  /api/health   -> comprobacion de vida. Devuelve algo minimo tipo {"status":"ok"}.
  Sirve para "despertar" el servicio antes de una demo y para monitoreo.

CUERPO DE LA PETICION (POST /api/analyze)
- MVP: {"text": "<texto de la politica>"}
- Aceptar tambien {"url": "<url directa de la politica>"} como alternativa documentada.
  (La busqueda de la politica en el footer de una web -scraping- NO entra aqui: es capa
  aparte, Nivel Avanzado, con riesgo de SSRF; ver 2_spec §11.1.)

CONTRATO DE RESPUESTA = 2_spec §9, COMPLETO desde el primer dia. Con DOS campos añadidos
por decision de equipo: `translation_available` (dentro de document) y `stub` (raiz).
Estructura exacta:

{
  "model_version": "0.1.0",
  "stub": true,
  "document": {
    "source_language": "en",
    "translated": false,
    "translation_available": true,
    "exposure": {
      "level": "medium",
      "score": 0.5,
      "disclaimer": "Estimacion basada en los temas detectados, no en una lectura clausula por clausula."
    },
    "categories": [
      {
        "id": "third_party_sharing_collection",
        "present": true,
        "confidence": 0.91,
        "fragment_count": 7,
        "gdpr_reference": "TODO"
      }
      // ... una entrada por cada una de las 9 categorias detectadas
    ],
    "fragment_count": 84
  },
  "fragments": [
    {
      "id": 12,
      "text": "<texto del fragmento, SIEMPRE en el idioma ORIGINAL, nunca traducido>",
      "start": 4210,
      "end": 4276,
      "labels": [
        { "id": "third_party_sharing_collection", "score": 0.88 }
      ]
    }
  ]
}

REGLAS DEL CONTRATO
- Nombres de campo en INGLES.
- `text`, `start`, `end` se refieren SIEMPRE al documento ORIGINAL (no a la traduccion).
  start/end son posiciones de caracter en el texto original (las usa la extension para
  resaltar). Deben ser reales aunque las etiquetas sean inventadas por el stub.
- `stub`: true mientras devuelva datos inventados; pasa a false con el modelo real.
- `model_version`: "0.1.0" en el stub; sube cuando entre el modelo.
- `gdpr_reference`: "TODO" por ahora (el mapeo RGPD es capa posterior, 2_spec §8).
- `exposure`: valor PLACEHOLDER fijo por ahora (level "medium", score 0.5). La logica
  real del semaforo es 2_spec §7 y aun no tiene pesos definidos: NO simularla.

LAS 9 CATEGORIAS (orden oficial, de 4_data_contract.md; no reordenar)
first_party_collection_use, third_party_sharing_collection, user_choice_control,
user_access_edit_deletion, data_retention, data_security, policy_change, do_not_track,
international_specific_audiences.

TROCEADOR DE FRAGMENTOS
- Partir el texto de entrada en fragmentos por PARRAFOS (doble salto de linea) para el MVP.
- Calcular start/end como posiciones de caracter reales en el texto original.
- Vive en una funcion propia y reutilizable (no duplicar cuando llegue una version mejor).

STUB (comportamiento mientras no hay modelo)
- Inventa una probabilidad por categoria y por fragmento, con SEMILLA FIJA: la misma
  entrada produce SIEMPRE la misma salida (para que el frontend pruebe sin que baile).
- Rellena todo el contrato de arriba con esos datos inventados.
- El dia del modelo real: se reemplaza SOLO la funcion que produce las probabilidades
  por model.predict_proba(...). El contrato no cambia. `stub` pasa a false.

TRADUCCION (capa preparada, no implementada aun — nivel experto)
- El backend debe aceptar politicas en INGLES o ESPAÑOL. El modelo aprende en ingles,
  asi que el español se traduce a ingles ANTES de clasificar.
- Flujo cableado: detectar idioma -> si es español, traducir es->en -> clasificar en
  ingles -> devolver las etiquetas pegadas al texto ORIGINAL en español (nunca a la
  traduccion; ver regla de text/start/end).
- Interfaz agnostica: una funcion translate(text, source_lang) detras de la cual da igual
  el motor. Motor por defecto previsto: Opus-MT local (Helsinki-NLP/opus-mt-es-en,
  licencia Apache-2.0, corre con transformers, ~300 MB, sin API key). NO implementar el
  motor real ahora: en el stub, translate() devuelve el texto igual (no-op) y los campos
  quedan source_language detectado trivialmente, translated=false, translation_available=true.
- Degradacion elegante (requisito del suelo, 2_spec): si la traduccion falla, la respuesta
  pone translation_available=false y sigue en ingles; NO se cae.
- Alternativas anotadas (no implementar sin decision de equipo): NLLB (mejor calidad pero
  licencia CC-BY-NC, uso no comercial: choca con el caracter open-source del proyecto,
  solo si Opus-MT se queda corto) y DeepL API (nube, requiere key).

SEGURIDAD — los 4 minimos de 2_spec §11.1, AL MONTAR, no despues
1. Cero secretos en el repo. Config y claves en .env (ignorado); .env.example versionado.
2. Limite de tamaño del texto de entrada: 100000 caracteres. Si se supera -> error 400.
3. CORS restringido al ORIGEN del frontend, leido de variable de entorno. NUNCA
   allow_origins=["*"]. Nota: en local el frontend llama por el proxy de Vite (mismo
   origen), asi que el CORS casi no se dispara en desarrollo; PERO es obligatorio para
   produccion, donde front y back estan en dominios distintos. No lo desactives ni lo
   abras a "*" porque "en local no bloqueaba".
4. El saneo del texto renderizado es trabajo del FRONTEND (no dangerouslySetInnerHTML sin
   limpiar), NO del backend. Anotarlo, no implementarlo aqui.
- Trabajo futuro (NO del suelo): SSRF del futuro scraper; joblib.load de artefactos como
  vector de ejecucion (riesgo bajo hoy, artefactos propios del equipo).

FORMATO DE ERROR
- Texto que supera 100000 caracteres o llega vacio -> HTTP 400 + {"error": "<mensaje
  legible>"} para que el frontend lo pueda mostrar. Nunca romper con un 500 sin mensaje.

ENGANCHE CON EL MODELO
- La API sirve UN modelo base (el mejor de los cuatro) para el suelo, NO los cuatro.
- El meta-modelo (stacking) es Sprint 2 y se despliega como una sola pieza; encaja en
  este MISMO contrato sin cambiarlo.
- El modelo base debe emitir probabilidad por categoria (regla de calibracion 2_spec §6.4);
  la API asume que recibe probabilidades.

CONFIGURACION / VARIABLES DE ENTORNO (nada de localhost cableado a fuego)
- La URL del backend (para el front) y los origenes permitidos (para el CORS) van en
  variables de entorno, no en el codigo. En local apuntan a localhost; en despliegue se
  cambia la variable, sin tocar codigo.
- Puerto de uvicorn: 8000.

DESPLIEGUE
- Front: build estatico -> Vercel / Netlify / Cloudflare Pages (gratis).
- Back: Google Cloud Run (tier gratis, scale-to-zero) o Render gratis. Se ACEPTA el cold
  start en esta fase: se mitiga llamando a GET /api/health antes de una demo. "Siempre
  despierto" (Render Standard o Cloud Run con minimo de instancias) es una subida FUTURA
  ligada al alcance (p. ej. la extension en uso real), no una decision de ahora.
- Aviso de capacidad: el backend lleva torch (por la traduccion local), asi que necesita
  >=2 GB de RAM para correr siempre-encendido de pago; los tiers de 512 MB solo sirven si
  el backend fuera ligero (modelo clasico + traduccion por API, sin torch).

REGLAS DURAS (no negociables)
- NO cablear URLs ni origenes en el codigo: variables de entorno.
- NO usar allow_origins=["*"].
- NO romper el contrato del §9: si falta un campo, se añade al §9 primero.
- NO devolver el texto traducido en `text`: siempre el original.
- NO implementar el motor de traduccion real, el semaforo real ni el mapeo RGPD:
  quedan como capas cableadas detras de su interfaz.
- Ante un archivo/columna/dato que falte, lanzar excepcion (raise), no inventar valores.
- Todo lo que va al repo, en ingles (nombres de archivo, variables, funciones, rutas);
  comentarios y docs pueden ir en español.
```

---

## Resumen de decisiones (para humanos)

| Tema | Decision |
|---|---|
| Framework | FastAPI + uvicorn, entorno uv, puerto 8000 |
| Endpoints | `POST /api/analyze`, `GET /api/health` (bajo `/api`) |
| Peticion | `{"text": ...}` (MVP); `{"url": ...}` documentado |
| Respuesta | Contrato §9 completo + `stub` y `translation_available` añadidos |
| Stub | Probabilidades fijas por semilla; `exposure` placeholder; `gdpr_reference` "TODO" |
| Troceador | Por parrafos; `start`/`end` reales sobre el original |
| Traduccion | Capa cableada, motor por defecto Opus-MT local (Apache-2.0); stub no-op |
| Seguridad | 4 minimos §11.1; limite 100000 chars; CORS por env var, nunca `*` |
| Errores | 400 + mensaje legible si vacio o >100000 chars |
| Modelo | La API sirve UN modelo base; meta = Sprint 2, mismo contrato |
| Config | URLs y origenes por variable de entorno |
| Despliegue | Front estatico gratis; back Cloud Run/Render gratis; cold start aceptado, warm-up con `/api/health` |

## Capas previstas pero NO implementadas ahora (huecos cableados)

- **Traduccion real** (Opus-MT local): la interfaz `translate()` existe; enchufar el motor es sustituir esa funcion. Suelo, 2_spec §5.
- **Semaforo real** (`exposure`): 2_spec §7, pendiente de pesos. Nivel Medio.
- **Mapeo RGPD** (`gdpr_reference`): 2_spec §8, pendiente. Nivel Avanzado.
- **Scraper del footer** (URL -> politica): capa SEPARADA de la API por el SSRF. Nivel Avanzado, 2_spec §11.1.
- **Meta-modelo** (stacking de los 4 base): Sprint 2; encaja en el mismo contrato.


