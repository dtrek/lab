# DATABRAIN

Software propio de **neuromarketing** (estilo iMotions) para uso interno, no
comercializable. Reemplaza la licencia de iMotions conservando sus funciones
clave para estudios de marketing sensorial: publicidades (imagen y video),
packaging, productos tangibles, alimentos, sabores y fragancias.

- **Enfoque:** monosujeto (un participante por sesión), **offline** (se graba
  todo sincronizado y se analiza después, sin monitoreo en vivo).
- **Plataforma:** HP ZBook con Windows 10 (los SDKs de los sensores están
  diseñados para Windows).
- **Lenguaje:** Python (obligado por el ecosistema: LSL, MNE, NeuroKit2, SDKs,
  modelos de Hugging Face).

## Documentación

- **[docs/ARQUITECTURA.md](docs/ARQUITECTURA.md)** — Documento Maestro de
  Arquitectura (v3, final consolidado). Es la **fuente de verdad** del proyecto:
  contexto, hardware, capas, adaptadores LSL, modos de gaze, procesamiento,
  salidas, riesgos y plan por fases. Empezá por la sección 1 (contexto) y la
  sección 13 (estado actual y próximos pasos).

## Hardware

| Modalidad            | Dispositivo                          | Software / SDK        | LSL          |
|----------------------|--------------------------------------|-----------------------|--------------|
| EEG                  | Neuroelectrics Enobio 8              | NIC2                  | Nativo       |
| GSR                  | Shimmer                              | Consensys Pro         | Nativo       |
| Eye tracker pantalla | Tobii X2-30 (30 Hz)                  | Tobii Pro SDK 1.11    | Adaptador propio |
| Eye tracker gafas    | Pupil Labs Neon                     | Companion app         | Nativo       |
| Facial coding        | Webcam dedicada                      | Hugging Face (ViT)    | —            |

## Estructura del repo

```
.
├── README.md
├── docs/
│   └── ARQUITECTURA.md          # documento maestro (fuente de verdad)
└── databrain/                   # paquete de arranque para la ZBook (Fase 0)
    ├── README.md
    ├── requirements.txt
    ├── 01_test_tobii_deteccion.py
    ├── 02_adaptador_tobii_lsl.py
    ├── 03_verificar_streams_lsl.py
    └── 04_test_facial_coding.py
```

## Estado actual

**Diseño de arquitectura COMPLETO.** Aún no comenzó la implementación en la
ZBook. Próximo paso: ejecutar **Fase 0** (validar los 4 streams LSL en
LabRecorder). Ver `databrain/README.md` y la sección 12–13 de la arquitectura.
