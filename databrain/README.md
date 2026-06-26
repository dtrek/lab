# DATABRAIN — Paquete de arranque para la ZBook (Fase 0)

**Plataforma:** HP ZBook con Windows 10. Todo esto corre **LOCAL** en la ZBook,
junto al hardware. **NO funciona en Colab/Linux** (el SDK del Tobii es solo
Windows/macOS). La única excepción es `04_test_facial_coding.py`, que no usa
hardware y puede correr en Colab.

## Contenido

```
databrain/
├── requirements.txt
├── 01_test_tobii_deteccion.py     # ¿el X2-30 se detecta y emite gaze?
├── 02_adaptador_tobii_lsl.py      # empuja el gaze del Tobii a un outlet LSL
├── 03_verificar_streams_lsl.py    # confirma que LSL ve los 4 sensores
└── 04_test_facial_coding.py       # prueba el modelo de emociones (opcional)
```

## Paso 1 — Crear el entorno (terminal de Windows)

```bat
:: Crear venv dedicado. Si pip se queja del SDK de Tobii, probar con
:: Python 3.10 o 3.8 (el tobii-research viejo no soporta los Python mas nuevos).
python -m venv databrain-env

:: Activar (Windows):
databrain-env\Scripts\activate

:: Actualizar pip:
python -m pip install -U pip setuptools

:: Instalar dependencias:
pip install -r requirements.txt
```

Si la instalación del `tobii-research` corta todo el `requirements.txt`,
instalá primero el resto y dejá el Tobii aparte:

```bat
pip install pylsl mne neurokit2 transformers torch pillow opencv-python pandas numpy matplotlib
pip install tobii-research==1.11.0
```

> **Importante:** `tobii-research` debe ser **1.11.0** (la última versión que
> soporta el X2-30). La 2.x ya no incluye el X2-30 y `find_all_eyetrackers()`
> devolvería lista vacía (falso negativo). Verificar con
> `pip show tobii-research`.

## Paso 2 — Validar el Tobii (único adaptador con desarrollo)

1. **`python 01_test_tobii_deteccion.py`** — corré este primero. Solo responde:
   ¿el X2-30 se detecta y emite gaze? Si ves coordenadas corriendo, pasá al
   siguiente.
2. **`python 02_adaptador_tobii_lsl.py`** — empuja el gaze del Tobii al outlet
   LSL `Databrain_Tobii_Gaze`, para que LabRecorder lo grabe sincronizado con
   los demás sensores. Dejalo corriendo.

## Paso 3 — Activar el LSL nativo en los otros tres sensores

- **Enobio:** NIC2 → activar salida LSL. **Gotcha:** inicializar el outlet LSL
  **ANTES** de que NIC2 conecte, o no lo detecta.
- **Shimmer:** Consensys Pro → activar LSL + **habilitar explícitamente el canal
  GSR** (si no, el dato no sale).
- **Neon:** Companion app → setting *"Stream over LSL"*. El teléfono y la ZBook
  deben estar en la **misma red**, con puertos LSL abiertos (UDP/TCP
  16571–16604). Probar esto **temprano**: es el típico punto que da guerra el
  primer día.

## Paso 4 — Verificar y grabar

- **`python 03_verificar_streams_lsl.py`** — lista todos los outlets LSL en la
  red. **Meta de la Fase 0:** ver **Tobii + Enobio + Shimmer + Neon** juntos
  acá.
- Abrir **LabRecorder** y grabar los cuatro streams sincronizados a XDF.

## Opcional — Facial coding

**`python 04_test_facial_coding.py`** prueba el modelo
`dima806/facial_emotions_image_detection` (Apache-2.0, ViT, ~91%). No depende del
hardware; se puede ir probando en Colab. Reemplazá la URL de ejemplo por la
ruta/URL de una foto de una cara real.

---

Ver el documento maestro en [`../docs/ARQUITECTURA.md`](../docs/ARQUITECTURA.md)
(secciones 12 y 13 para el plan por fases y el estado actual).
