"""
DATABRAIN - Fase 0 - Paso 3: Verificar streams LSL en la red
============================================================
Lista todos los outlets LSL disponibles. Sirve para confirmar que
los 4 sensores estan emitiendo antes de grabar con LabRecorder.
Requiere: pip install pylsl

Antes de correr, asegurate de haber activado el LSL en cada equipo:
  - Enobio:  NIC2 -> activar salida LSL (inicializar ANTES de conectar)
  - Shimmer: Consensys Pro -> activar LSL + habilitar canal GSR
  - Neon:    Companion app -> setting "Stream over LSL" (misma red!)
  - Tobii:   correr 02_adaptador_tobii_lsl.py
"""

from pylsl import resolve_streams

print("Buscando streams LSL en la red (5 seg)...\n")
streams = resolve_streams(wait_time=5.0)

if not streams:
    print("X  No se encontro ningun stream. Revisar que cada equipo")
    print("   tenga el LSL activado y este en la misma red.")
else:
    print(f"OK Se encontraron {len(streams)} stream(s):\n")
    for s in streams:
        print(f"  - Nombre: {s.name()}")
        print(f"    Tipo:   {s.type()}")
        print(f"    Canales:{s.channel_count()}  @ {s.nominal_srate()} Hz")
        print(f"    Source: {s.source_id()}\n")

print("Meta Fase 0: ver Tobii + Enobio + Shimmer + Neon juntos aca")
print("y poder grabarlos sincronizados desde LabRecorder.")
