import os
import re
import requests
import time

# === CONFIGURACIÓN ===
API_KEY = "e50d25377da7447ebe81c372482c8304"  # <--- PEGA AQUÍ TU LLAVE DE RAWG
ARCHIVO_JUEGOS = 'juegos.txt'
CARPETA_DESTINO = 'portadas'
# =====================

def inicializar_carpeta():
    if not os.path.exists(CARPETA_DESTINO):
        os.makedirs(CARPETA_DESTINO)
        print(f"✔️ Carpeta '{CARPETA_DESTINO}' lista.")

def limpiar_titulo(linea):
    # Quitamos el CUSA, versiones, etiquetas de PKG y texto entre paréntesis
    t = re.sub(r'CUSA\d{5}', '', linea, flags=re.IGNORECASE)
    t = re.sub(r'\b(?:up|v)\s?\d+(?:\.\d+)?\b', '', t, flags=re.IGNORECASE)
    t = re.sub(r'PS4\s*PKG.*', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\[.*?\]|\(.*?\)', '', t)
    # Limpieza de caracteres especiales comunes en listas de juegos
    t = t.replace('FIXED', '').replace('UPDATE', '').replace('OK', '')
    return t.strip()

def extraer_cusa(linea):
    match = re.search(r'CUSA\d{5}', linea, re.IGNORECASE)
    return match.group(0).upper() if match else None

def descargar_imagen(url, cusa):
    ruta = os.path.join(CARPETA_DESTINO, f"{cusa}.jpg")
    if os.path.exists(ruta):
        return False # Ya existe, no gastamos internet
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            with open(ruta, 'wb') as f:
                f.write(response.content)
            return True
    except:
        return False
    return False

def buscar_en_rawg(nombre):
    # Buscamos el juego en la base de datos de RAWG
    url = f"https://api.rawg.io/api/games?key={API_KEY}&search={nombre}&page_size=1"
    try:
        res = requests.get(url, timeout=10).json()
        if 'results' in res and len(res['results']) > 0:
            # Traemos la imagen principal (background_image)
            return res['results'][0].get('background_image')
    except Exception as e:
        print(f"Error de conexión: {e}")
    return None

def ejecutar():
    inicializar_carpeta()
    
    if not os.path.exists(ARCHIVO_JUEGOS):
        print(f"❌ Error: No encuentro el archivo '{ARCHIVO_JUEGOS}'")
        return

    with open(ARCHIVO_JUEGOS, 'r', encoding='utf-8') as f:
        # Filtramos líneas vacías o decorativas
        lineas = [l.strip() for l in f if l.strip() and not l.startswith('!')]

    print(f"🚀 Iniciando descarga de portadas para {len(lineas)} juegos...")

    for linea in lineas:
        cusa = extraer_cusa(linea)
        if not cusa:
            continue
        
        titulo = limpiar_titulo(linea)
        
        # Si ya tenemos la imagen, saltamos a la siguiente para ahorrar tiempo
        if os.path.exists(os.path.join(CARPETA_DESTINO, f"{cusa}.jpg")):
            print(f"⏩ Ya existe: {cusa} | {titulo[:30]}")
            continue

        print(f"🔍 Buscando: {titulo}...", end="\r")

        img_url = buscar_en_rawg(titulo)
        
        if img_url:
            if descargar_imagen(img_url, cusa):
                print(f"✅ Descargado: {cusa} - {titulo[:30]}...")
            else:
                print(f"❌ Error al guardar: {cusa}          ")
        else:
            print(f"⚠️ No encontrado en RAWG: {titulo[:30]}      ")
        
        # Pausa muy breve para ser respetuosos con la API
        time.sleep(0.2)

if __name__ == "__main__":
    ejecutar()
    print("\n✨ ¡Proceso terminado! Revisa tu carpeta 'portadas'.")