"""
DATABRAIN - Fase 0 - Paso 1: Test minimo de deteccion del Tobii X2-30
=====================================================================
Objetivo: confirmar que el X2-30 es detectado y emite gaze. NADA mas.
Requiere: pip install tobii-research==1.11.0  (en la ZBook, Windows)

Si NO detecta el tracker:
  - Verificar que tobii-research sea 1.11.0 (no la 2.x): pip show tobii-research
  - Correr antes el "Installation & Configuration Tool" del X2-30
  - Confirmar que el tracker este enchufado por USB
"""

import time
import tobii_research as tr


def gaze_data_callback(gaze_data):
    """Se ejecuta ~30 veces por segundo, una por cada muestra."""
    left = gaze_data['left_gaze_point_on_display_area']   # (x, y) normalizado 0-1
    right = gaze_data['right_gaze_point_on_display_area']
    lv = gaze_data['left_gaze_point_validity']
    rv = gaze_data['right_gaze_point_validity']
    sys_ts = gaze_data['system_time_stamp']               # reloj PC (microseg)
    print(f"[{sys_ts}] L:{left} (v={lv})  R:{right} (v={rv})")


def main():
    print("Buscando eye trackers Tobii...")
    trackers = tr.find_all_eyetrackers()

    if len(trackers) == 0:
        print("X  No se encontraron eye trackers. Ver notas del encabezado.")
        return

    t = trackers[0]
    print("OK Conectado:")
    print(f"   Modelo:  {t.model}")
    print(f"   Nombre:  {t.device_name}")
    print(f"   Serial:  {t.serial_number}")
    print(f"   Address: {t.address}")

    print("\nSuscribiendo al gaze por 10 segundos. Mira la pantalla...")
    t.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    try:
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        t.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
        print("\nListo. Si viste coordenadas corriendo -> pasa al Paso 2.")


if __name__ == "__main__":
    main()
