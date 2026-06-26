"""
DATABRAIN - Fase 0 - Paso 2: Adaptador Tobii X2-30 -> LSL
=========================================================
Crea un outlet LSL 'Databrain_Tobii_Gaze' para que LabRecorder lo
grabe junto a Enobio, Shimmer y Neon.
Requiere: pip install tobii-research==1.11.0 pylsl

Canales (8 floats):
  0 left_x  1 left_y  2 left_validity
  3 right_x 4 right_y 5 right_validity
  6 device_ts  7 system_ts
Coordenadas normalizadas 0-1. NaN cuando la muestra no es valida.
"""

import time
import math
import tobii_research as tr
from pylsl import StreamInfo, StreamOutlet, local_clock

SRATE = 30  # Hz nominal del X2-30


def build_outlet(tracker):
    info = StreamInfo(
        name='Databrain_Tobii_Gaze',
        type='Gaze',
        channel_count=8,
        nominal_srate=SRATE,
        channel_format='float32',
        source_id=f'tobii_{tracker.serial_number}'
    )
    chns = info.desc().append_child("channels")
    for label in ['left_x', 'left_y', 'left_validity',
                  'right_x', 'right_y', 'right_validity',
                  'device_ts', 'system_ts']:
        chns.append_child("channel").append_child_value("label", label)
    info.desc().append_child_value("manufacturer", "Tobii")
    info.desc().append_child_value("model", tracker.model)
    return StreamOutlet(info)


def make_callback(outlet):
    def gaze_data_callback(gaze_data):
        lx, ly = gaze_data['left_gaze_point_on_display_area']
        rx, ry = gaze_data['right_gaze_point_on_display_area']
        lv = gaze_data['left_gaze_point_validity']
        rv = gaze_data['right_gaze_point_validity']
        if not lv:
            lx, ly = math.nan, math.nan
        if not rv:
            rx, ry = math.nan, math.nan
        sample = [lx, ly, float(lv), rx, ry, float(rv),
                  float(gaze_data['device_time_stamp']),
                  float(gaze_data['system_time_stamp'])]
        outlet.push_sample(sample, timestamp=local_clock())
    return gaze_data_callback


def main():
    print("Buscando X2-30...")
    trackers = tr.find_all_eyetrackers()
    if not trackers:
        print("X  No se encontro el tracker. Volver al Paso 1.")
        return
    t = trackers[0]
    print(f"OK {t.model} ({t.serial_number})")

    outlet = build_outlet(t)
    print("Outlet LSL 'Databrain_Tobii_Gaze' creado.")
    print("Abri LabRecorder: deberia aparecer el stream en la lista.")

    cb = make_callback(outlet)
    t.subscribe_to(tr.EYETRACKER_GAZE_DATA, cb, as_dictionary=True)
    print("Streaming a LSL. Ctrl+C para frenar.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        t.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, cb)
        print("\nDetenido.")


if __name__ == "__main__":
    main()
