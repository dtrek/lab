"""
DATABRAIN - Test del modelo de facial coding (Hugging Face)
===========================================================
Modelo: dima806/facial_emotions_image_detection (Apache-2.0, ViT, ~91%)
Requiere: pip install transformers torch pillow
Corre en Linux/Colab o Windows indistintamente (no usa hardware).
"""

from transformers import pipeline

pipe = pipeline("image-classification",
                model="dima806/facial_emotions_image_detection")

# Reemplazar por la ruta/URL de una foto de una cara real para probar:
img = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/hub/parrots.png"
resultados = pipe(img)

print("Emociones detectadas (ordenadas por score):")
for r in resultados:
    print(f"  {r['label']:10s} -> {r['score']:.4f}")
