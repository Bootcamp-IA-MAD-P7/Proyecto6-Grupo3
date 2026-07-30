from pathlib import Path
import joblib
import numpy as np
import pandas as pd

# 1. Rutas (ajusta el nombre del CSV de vuestro dataset extension)
ARTIFACTS = Path("artifacts")
EXTENSION_PATH = Path("data/processed/dataset_extension.csv")

# 2. Cargar el vocabulario original de OPP-115 (13.389 palabras)
vectorizer = joblib.load(ARTIFACTS / "tfidf_vectorizer.joblib")
vocab_opp115 = set(vectorizer.get_feature_names_out())

# 3. Cargar el dataset extension y FILTRAR SOLO INGLÉS
df_ext = pd.read_csv(EXTENSION_PATH)

# Asegúrate de filtrar por la columna de idioma (ej. "en") si el CSV tiene ambos
if "lang" in df_ext.columns:
    df_en = df_ext[df_ext["lang"] == "en"].copy()
else:
    # Si todo el CSV ya está en inglés
    df_en = df_ext.copy()

fragmentos = df_en["segment"].dropna().tolist()

print("=" * 60)
print(f"AUDITORÍA DE COBERTURA LÉXICA — DATASET EXTENSION (INGLÉS)")
print("=" * 60)
print(f"Total de fragmentos en inglés analizados : {len(fragmentos)}\n")

# 4. Cálculo de Cobertura y Palabras Desconocidas (OOV - Out Of Vocabulary)
coberturas = []
parrafos_vacios = 0
desconocidas_frecuencia = {}

for texto in fragmentos:
    # Tokenización simple por palabras (minúsculas, caracteres alfanuméricos)
    words = [w.strip(".,();:\"'?!") for w in texto.lower().split()]
    words = [w for w in words if w]  # quitar vacíos
    
    if not words:
        continue
        
    conocidas_count = 0
    for w in words:
        if w in vocab_opp115:
            conocidas_count += 1
        else:
            desconocidas_frecuencia[w] = desconocidas_frecuencia.get(w, 0) + 1
            
    ratio = conocidas_count / len(words)
    coberturas.append(ratio)
    
    if conocidas_count == 0:
        parrafos_vacios += 1

# 5. Métricas Globales
media_cobertura = np.mean(coberturas) * 100
min_cobertura = np.min(coberturas) * 100
p25_cobertura = np.percentile(coberturas, 25) * 100

print(f"Cobertura léxica MEDIA   : {media_cobertura:.2f}%")
print(f"Cobertura léxica MÍNIMA  : {min_cobertura:.2f}%")
print(f"Percentil 25 (el 25% peor): {p25_cobertura:.2f}% de palabras conocidas\n")

print(f"Párrafos 100% CIEGOS (0 palabras conocidas): {parrafos_vacios} "
      f"({parrafos_vacios / len(fragmentos) * 100:.2f}% del total)\n")

# 6. Top 15 Términos Modernos que el modelo NO conoce
print("--- TOP 15 PALABRAS DE 2026 INVISIBLES PARA EL MODELO (OPP-115) ---")
top_oov = sorted(desconocidas_frecuencia.items(), key=lambda x: x[1], reverse=True)
for i, (palabra, freq) in enumerate(top_oov[:15], 1):
    print(f" {i:2d}. '{palabra}' -> aparece {freq} veces en las políticas nuevas")