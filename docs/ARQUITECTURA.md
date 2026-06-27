# DATABRAIN — Documento Maestro de Arquitectura (v3 — final consolidado)

**Cómo usar este documento:** Es autosuficiente y está pensado para retomar el
proyecto desde cero en cualquier momento o sesión. Si se lo das a un asistente
nuevo, leé primero la sección 1 (contexto) y la sección 13 (estado actual y
próximos pasos). El asistente con el que se diseñó esto no conserva memoria
entre sesiones, por eso toda decisión y avance vive en este archivo. Última
actualización de estado: ver sección 13.

---

## 1. Contexto del proyecto

Databrain es un software propio para reemplazar iMotions, desarrollado para uso
interno (no comercializable), que corre sobre hardware ya existente. El objetivo
es eliminar el costo de licencia de iMotions conservando sus funciones clave
para estudios de marketing sensorial: publicidades (imagen y video), packaging,
productos tangibles, alimentos, sabores y fragancias.

El usuario trabaja con un enfoque **monosujeto** (un participante por sesión)
por capacidad técnica, en modo **offline** (se graba todo sincronizado y se
analiza después, sin monitoreo en vivo). El lenguaje de desarrollo es **Python**,
obligado por el ecosistema (LSL, MNE, NeuroKit2, SDKs, modelos de Hugging Face).

## 2. Hardware y plataforma

**Plataforma única:** HP ZBook con Windows 10. Windows es la plataforma correcta
porque los SDKs de los sensores están diseñados para ella. **Nota permanente:**
Microsoft terminó el soporte general de Windows 10 en octubre 2025, y algunos
proveedores migran su testing a Windows 11; por eso cada SDK debe verificarse en
Win 10 (ya hecho para el caso crítico, el Tobii — ver 5.1).

**Dispositivos:**

- **EEG:** Neuroelectrics Enobio 8 (software NIC2).
- **GSR:** Shimmer (software Consensys Pro).
- **Eye tracker de pantalla:** Tobii X2-30 (30 Hz).
- **Eye tracker de gafas:** Pupil Labs Neon ("just act natural"), con cámara de
  escena.
- **Webcam dedicada** para facial coding.
- **Cámara de escena secundaria** opcional (redundancia en estudios de producto
  físico).

## 3. Principio de diseño y arquitectura general

**Cuatro capas:** captura y sincronización (orquesta sensores, genera línea de
tiempo común), almacenamiento (persiste datos crudos sincronizados como fuente
de verdad), procesamiento (métricas por modalidad, heatmaps, AOIs) y salida
(datos, visualizaciones, reportes y, a futuro, informes por LLM).

**Principio rector:** los datos crudos sincronizados son el activo
irreemplazable. Todo lo demás se deriva de ellos y puede recalcularse, así que
la robustez se concentra en la captura y el timestamping. La decisión offline
simplifica radicalmente la captura: no se necesita baja latencia ni
visualización en vivo, solo registro robusto y bien timestampeado.

## 4. Capa de sincronización (el corazón del sistema)

Esta es la función por la que realmente se paga iMotions. La columna vertebral
es **Lab Streaming Layer (LSL)**, estándar de facto en investigación para
sincronizar streams heterogéneos sobre una línea de tiempo común. **Hallazgo
central del proyecto:** los cuatro sensores tienen camino confirmado a LSL, y
tres lo emiten de forma nativa sin programar el puente. Solo el Tobii requiere
un adaptador propio.

El video (cámara de escena secundaria y webcam) se registra con timestamps LSL
para alinear cada frame. El grabador central (LabRecorder, formato XDF, o un
módulo propio) escribe todo a un archivo unificado con la marca temporal común.

### Estado de los cuatro adaptadores

- **Enobio 8 — RESUELTO (LSL nativo).** NIC2 incluye integración LSL/TCP de
  fábrica y crea un outlet de EEG nativo; también puede recibir markers por LSL
  inlet. **Gotcha:** el outlet/inlet LSL debe inicializarse **antes** de que
  NIC2 conecte, o NIC2 no lo detecta. Ya probado funcionando fuera de iMotions.
  **Riesgo:** nulo.

- **Pupil Labs Neon — CONFIRMADO (LSL nativo).** La Companion app trae soporte
  LSL incorporado (setting *"Stream over LSL"*), creando dos outlets: uno de
  gaze + eye-state (coordenadas en espacio de cámara de escena; opcionalmente
  diámetro pupilar y centro del globo ocular) y otro de eventos. El antiguo
  *"LSL Relay"* quedó deprecado para Neon (ya no se usa). **Notas:** la
  Companion app corre en el teléfono y transmite por red, así que el teléfono y
  la ZBook deben estar en la misma red, con puertos LSL abiertos (UDP/TCP
  16571–16604). No necesita estar grabando para streamear, pero se recomienda
  grabar igual en la app como backup. **Riesgo:** bajo.

- **Shimmer GSR — CONFIRMADO (LSL nativo desde nov-2025, + alternativas).**
  Consensys Pro tiene integración LSL nativa desde noviembre 2025. Alternativas
  probadas por la comunidad: scripts `shimmer_lsl_streamer` (GitHub) y la
  versión de ETH Zürich; y la API Python `pyshimmer` para control de bajo nivel.
  **Gotcha:** hay que habilitar explícitamente el canal GSR en Consensys para
  que el dato salga. **Riesgo:** bajo.

- **Tobii X2-30 — CONFIRMADO (requiere adaptador propio).** Único sensor sin LSL
  nativo. Se accede por código con el Tobii Pro SDK para Python
  (`tobii_research`). Detalles críticos en 5.1. **Riesgo:** bajo (acceso por SDK
  ya confirmado en la documentación oficial de Tobii).

## 5. Modos de gaze y perfiles de sesión

Databrain maneja tres pipelines de mirada:

- **Modo pantalla (alta precisión) — Tobii X2-30.** Gaze mapeado a coordenadas
  de pantalla; con la geometría del estímulo se generan heatmaps y AOIs. Para
  publicidades, packshots y packaging en display.
- **Modo mundo real — Pupil Labs Neon + cámara de escena.** El gaze se superpone
  sobre el video de escena. Para producto físico, fragancias y sabores.
- **Modo webcam (baja precisión, opcional, fase posterior).** Estima gaze desde
  la misma webcam del facial coding (WebGazer.js, L2CS-Net o similar) para
  estudios donde el cliente no contrató eye tracker dedicado. Heatmaps
  orientativos, no métricos (precisión de varios grados vs. ~0.5° del Tobii). Se
  comunica explícitamente como indicativo. No reemplaza al Tobii ni a las Pupil
  Labs.

### 5.1 Adaptador Tobii X2-30 → LSL (notas críticas)

El X2-30 está discontinuado (reemplazado por Tobii Pro Spark), pero la
documentación oficial de Tobii confirma soporte por SDK en Windows 7/8.1/10/11,
con *"soporte limitado"* y únicamente en versiones **1.2 a 1.11** del Tobii Pro
SDK.

**Implicancias prácticas:**

- Instalar la versión vieja fija: `pip install tobii-research==1.11.0` (la última
  que soporta el X2-30). El `pip install tobii-research` sin versión instala la
  2.x, que ya no incluye el X2-30 → `find_all_eyetrackers()` devolvería lista
  vacía (falso negativo).
- **Congelar el entorno** (virtualenv dedicado, sin updates) una vez funcionando,
  porque Tobii ya no testea este equipo y advierte posible degradación futura.
- Windows 10 figura como soportado para esta combinación.
- Que el X2-30 corra dentro de iMotions confirma que el hardware y drivers base
  están sanos en la ZBook; iMotions usa el SDK de Tobii por debajo.

**Flujo del adaptador (patrón oficial del SDK):** buscar tracker
(`find_all_eyetrackers`) → conectar → calibrar (`ScreenBasedCalibration`,
necesario para heatmaps) → suscribir (`EYETRACKER_GAZE_DATA`,
`as_dictionary=True`). Dentro del callback de gaze, las dos tareas que el
adaptador realmente necesita: (1) capturar el timestamp (`system_time_stamp` /
`device_time_stamp`, base de toda la sincronización) y (2) hacer push de la
muestra a un outlet LSL propio en lugar de imprimirla. Las coordenadas llegan
normalizadas 0.0–1.0 relativas a la pantalla (`*_gaze_point_on_display_area`) —
formato ideal para heatmaps: coordenada normalizada × resolución del estímulo =
pixel mirado.

### 5.2 Perfiles de sesión (resuelven el conflicto gafas vs. facial coding)

Las gafas Pupil Labs ocluyen la zona ocular y degradan el facial coding. Por
eso, al crear un estudio se elige un perfil que activa/desactiva módulos:

- **Perfil "Eye tracking con gafas + GSR + EEG":** prioriza gaze de Pupil Labs;
  facial coding marcado como no confiable o desactivado.
- **Perfil "Facial coding con webcam + GSR + EEG":** webcam sin gafas; habilita
  facial coding de calidad (y opcionalmente el gaze webcam-based de baja
  precisión).

Databrain **nunca promete datos faciales confiables cuando hay gafas puestas.**
Esta lógica además calza con cómo se contrata cada estudio (el cliente paga gaze
o facial coding).

## 6. Presentación de estímulos y marcado

- **Estímulos en pantalla** (publicidades, imágenes, packaging): los presenta
  Databrain, registrando el timing exacto de aparición. Doble función: marca
  automática de cada segmento y geometría para los heatmaps.
- **Estímulos físicos** (aromas, sabores, envases): los entrega el moderador, no
  la computadora. En vez de botones en vivo, el momento de entrega queda
  registrado en el video de la cámara de escena, y el marcado se hace en
  post-proceso revisando esa grabación. Traslada el marcado a la fase de
  análisis, que es donde ya se trabaja.

## 7. Procesamiento por modalidad

- **EEG (Enobio 8) → MNE-Python (opcional Braindecode):** filtrado, limpieza de
  artefactos, y métricas de marketing como engagement, carga cognitiva y
  asimetría frontal alfa (proxy de valencia / aproximación-evitación).
- **GSR (Shimmer) → NeuroKit2:** separación tónica/fásica y detección de picos de
  respuesta electrodérmica (SCR) por estímulo, como indicador de
  activación/arousal.
- **Facial coding → modelo Hugging Face.** Candidato confirmado para v1:
  `dima806/facial_emotions_image_detection` — licencia Apache-2.0 (uso libre),
  basado en ViT (`google/vit-base-patch16-224-in21k`), ~91% de accuracy reportada
  sobre 7 emociones básicas (sad, disgust, angry, neutral, fear, surprise,
  happy), 85.8M params (liviano, corre en la ZBook), ~28k descargas/mes. Uso
  simple vía `transformers` pipeline (`"image-classification"`). Produce emoción
  dominante e intensidades por segmento. **Validez:** razonable para uso propio,
  pero no equivale a Affectiva en validación científica; tenerlo presente al
  comunicar resultados.
- **Gaze:** fijaciones, dwell time, recorridos y, en modo pantalla, heatmaps y
  AOIs.

## 8. Heatmaps y AOIs

Requeridos para estímulos estáticos y video, escalonados por fase.

- **Fase 1:** estáticos (packshots, packaging, piezas gráficas), AOIs fijas.
- **Fase 2:** video/publicidades, AOIs dinámicas frame a frame (más complejo,
  reutiliza la base de Fase 1).

## 9. Salidas

**Núcleo:** datos crudos sincronizados (CSV/Parquet o XDF, alineados por
timestamp), fuente de verdad llevable a Python/R. Sobre esa base: métricas por
modalidad, heatmaps y visualizaciones de gaze, y reporte agregado por estímulo
(por cada pieza: arousal de GSR, emoción dominante, índices de EEG, tiempo en
AOIs, etc. — lo que se le muestra al cliente). **Fase posterior:** dashboard
visual y capa de LLM que redacte informes a partir de las métricas
estructuradas.

**Decisión de arquitectura para la interfaz (Fase 3): app web local.** El
dashboard y la operación del estudio se construyen como una **app web servida por
la propia ZBook** (backend en Python hablando con los sensores + frontend web en
`localhost`), no como un sitio remoto. Razón: los sensores están enchufados por
USB a la ZBook y sus SDKs corren localmente; un sitio alojado en internet/GitHub
no puede acceder a ese hardware (límite de seguridad del navegador). La web local
da lo mejor de ambos mundos: interfaz linda con la **identidad visual de
Databrain** (brand guidelines) y la comodidad de manejarla desde el navegador.
Beneficio clave: cualquier dispositivo en la misma red (un **celular**, una
tablet) puede abrir la interfaz. Caso de uso confirmado: **control remoto
iniciar/terminar captura desde el celular** en estudios de campo (p. ej. una
tienda, en "modo mundo real" con las Pupil Labs), donde el investigador no está
pegado a la ZBook. Esto es solo control (manda dos órdenes, no transmite datos),
así que **respeta la decisión offline**: no se hace monitoreo de datos neuro en
vivo. Un panel de **pre-flight checklist** (¿los 4 sensores conectados?, ¿señal
limpia?, ¿batería del Shimmer?) antes de grabar también cae en esta categoría y
es compatible con offline.

## 10. Stack tecnológico

Base: Python. Componentes confirmados:

- **Lab Streaming Layer (LSL) + LabRecorder (XDF)** — sincronización y grabación.
- **NIC2 (LSL nativo)** — Enobio.
- **Consensys Pro (LSL nativo)** o `pyshimmer`/scripts comunitarios — Shimmer.
- **Neon Companion app (LSL nativo)** — Pupil Labs.
- **`tobii_research` 1.11 + adaptador propio** — Tobii X2-30.
- **MNE-Python / Braindecode** — EEG.
- **NeuroKit2** — GSR.
- **`dima806/facial_emotions_image_detection` (Apache-2.0) vía `transformers`** —
  facial coding.
- **WebGazer.js / L2CS-Net** — modo webcam opcional.
- **OpenCV / Pandas / NumPy** — video, datos, heatmaps.

## 11. Riesgos y notas honestas

- **LSL sincroniza, no analiza.** El gran trabajo de desarrollo está en el
  procesamiento (limpiar EEG, extraer índices, generar heatmaps válidos, alinear
  con estímulos), no en la captura. Ahí se va la mayor parte del esfuerzo.
- **Red de la Neon:** teléfono + ZBook en la misma red y firewall con puertos LSL
  abiertos es el típico punto que da guerra el primer día. Probar temprano. En
  **estudios de campo** (tienda) no confiar en el WiFi del lugar: llevar **red
  propia** (router portátil / hotspot dedicado) al que se conectan ZBook + celu
  del investigador + celu de las Neon. Arma una "burbuja" de red independiente del
  lugar y resuelve de entrada este riesgo.
- **Tobii congelado:** usar 1.11 y no actualizar. Funciona hoy; podría degradarse
  en updates futuros.
- **Facial coding open source ≠ Affectiva** en validación. Apto para uso propio.
- **Win 10:** combinación validada para el caso crítico (Tobii), pero verificar
  cada SDK nuevo que se sume.

## 12. Plan de implementación por fases

- **Fase 0 — Validación de adaptadores** (despeja el riesgo antes de construir).
  Enobio, Shimmer y Pupil Labs emiten LSL nativo → solo verificar cada stream en
  LabRecorder. Único desarrollo: el adaptador Tobii. Tareas: (a) instalar NIC2,
  inicializar outlet LSL antes de conectar, verificar stream Enobio; (b) activar
  LSL en Consensys Pro con canal GSR habilitado, verificar stream Shimmer; (c)
  activar *"Stream over LSL"* en la Neon Companion, confirmar misma red + puertos
  16571-16604, verificar streams gaze/eventos; (d) `pip install
  tobii-research==1.11.0` en virtualenv dedicado, correr script
  `find_all_eyetrackers()` + suscripción; si imprime coordenadas, escribir el
  adaptador callback → outlet LSL. **Meta:** los cuatro streams visibles
  simultáneamente en LabRecorder.

- **Fase 1 — Captura y análisis base.** Grabación sincronizada de los 4 sensores
  a XDF; presentación de estímulos en pantalla con marcado automático;
  procesamiento por modalidad (MNE / NeuroKit2 / modelo facial); heatmaps
  estáticos; salida de datos crudos + reporte agregado por estímulo.

- **Fase 2 — Heatmaps sobre video.** AOIs dinámicas frame a frame; refinamiento
  de métricas.

- **Fase 3 — Extras.** Dashboard como **app web local** (servida por la ZBook,
  con la identidad visual de Databrain) que incluye **control remoto de la captura
  desde el celular** (iniciar/terminar) y un **pre-flight checklist** de sensores;
  capa de LLM para informes; módulo gaze webcam-based. Ver la "Decisión de
  arquitectura para la interfaz" en la sección 9.

## 13. ESTADO ACTUAL Y PRÓXIMOS PASOS

*Sección de retomada. Actualizar acá cada vez que se avance.*

**Fase actual:** **Fase 0 EN CURSO en la ZBook.** El entorno ya está montado y
funcionando: Python 3.10.11 instalado junto a la 3.14 del sistema, virtualenv
dedicado (`databrain-proyecto\databrain-env\`) con `tobii-research==1.11.0`,
`pylsl 1.18.2`, `mne 1.12.1`, `torch` y demás dependencias. Claude Code corre
localmente en la ZBook para asistir contra el hardware real.

**Decisiones cerradas:** todas las de las secciones 1–10 (offline, monosujeto,
Win 10 en ZBook, 3 modos de gaze, perfiles de sesión, salidas, stack).

**Decisiones nuevas (esta sesión):**

- **Interfaz/dashboard (Fase 3) = app web local** servida por la ZBook, con la
  identidad visual de Databrain. Ver detalle en sección 9.
- **Control remoto de la captura desde el celular** (iniciar/terminar) para
  estudios de campo (tienda, modo mundo real con Pupil Labs). Solo control, no
  monitoreo de datos en vivo → respeta el offline.
- **Red propia de campo** (router portátil / hotspot) para los estudios fuera del
  laboratorio. Ver sección 11.

**Adaptadores LSL — progreso de Fase 0 en la ZBook:**

- **Tobii X2-30:** ✅ **DETECTADO Y EMITIENDO GAZE en la ZBook** (script
  `01_test_tobii_deteccion.py` verificado esta sesión con `tobii-research
  1.11.0`). Era el único sensor con desarrollo propio y el de mayor riesgo →
  **riesgo despejado**. Siguiente: validar el adaptador
  `02_adaptador_tobii_lsl.py` (outlet LSL `Databrain_Tobii_Gaze`) y verlo en
  `03_verificar_streams_lsl.py`.
- **Enobio:** resuelto (nativo, ya probado fuera de iMotions).
- **Shimmer:** confirmado (Consensys Pro nativo / `pyshimmer`).
- **Pupil Labs Neon:** ⬜ **ÚNICO PENDIENTE** — confirmado nativo; falta activar
  *"Stream over LSL"* en la Companion app (misma red + puertos 16571-16604) y
  verificar el stream en la ZBook.

**Modelo facial:** elegido `dima806/facial_emotions_image_detection`
(Apache-2.0) — falta integrar.

**Próximo paso inmediato:** (1) verificar el stream LSL del Tobii con el adaptador
`02` + `03`; (2) **validar la Pupil Labs Neon** (lo único que falta de los 4
sensores); (3) ver los cuatro streams juntos en LabRecorder = **meta de la Fase
0**. Ver `databrain/README.md` para el paso a paso.

**Pendiente de definir más adelante:** detalle de índices de EEG a calcular;
formato exacto del reporte al cliente; elección final entre Consensys Pro nativo
vs. `pyshimmer` para el Shimmer.
