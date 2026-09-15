import os
import sys
import zipfile
import urllib.request

URL_BASE = "https://www.inegi.org.mx/contenidos/programas/enigh/nc/2024/microdatos"
DIR_DATOS = "data"

ARCHIVOS = {
    "enigh2024_ns_poblacion_csv.zip": "poblacion.csv",
    "enigh2024_ns_trabajos_csv.zip": "trabajos.csv",
    "enigh2024_ns_ingresos_csv.zip": "ingresos.csv",
    "enigh2024_ns_concentradohogar_csv.zip": "concentradohogar.csv",
    "enigh2024_ns_hogares_csv.zip": "hogares.csv",
}

FD_URL = f"{URL_BASE}/889463924494.pdf"
FD_ARCHIVO = "FD_ENIGH2024.pdf"

COLUMNAS_ESPERADAS = {
    "poblacion.csv": ["folioviv", "foliohog", "numren", "sexo", "edad", "nivelaprob", "gradoaprob"],
    "trabajos.csv": ["folioviv", "foliohog", "numren", "id_trabajo", "htrab"],
    "ingresos.csv": ["folioviv", "foliohog", "numren", "clave", "ing_tri"],
    "concentradohogar.csv": ["folioviv", "foliohog", "ing_cor", "ingtrab", "educa_jefe", "factor"],
    "hogares.csv": ["folioviv", "foliohog"],
}


def descargar(url, destino):
    print(f"Descargando: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=300) as r, open(destino, "wb") as f:
        f.write(r.read())
    print(f"  guardado: {destino} ({os.path.getsize(destino) / 1e6:.1f} MB)")


def verificar(csv_ruta, columnas):
    with open(csv_ruta, encoding="utf-8") as f:
        encabezado = f.readline().strip().split(",")
    faltantes = [c for c in columnas if c not in encabezado]
    if faltantes:
        raise SystemExit(f"  ERROR: {csv_ruta} no contiene {faltantes}")
    print(f"  OK: {csv_ruta} ({len(encabezado)} columnas, incluye {columnas})")


def main():
    os.makedirs(DIR_DATOS, exist_ok=True)
    for zip_nombre, csv_nombre in ARCHIVOS.items():
        zip_ruta = os.path.join(DIR_DATOS, zip_nombre)
        csv_ruta = os.path.join(DIR_DATOS, csv_nombre)
        if os.path.exists(csv_ruta) and os.path.getsize(csv_ruta) > 1_000_000:
            print(f"{csv_nombre} ya existe, se omite la descarga.")
        else:
            descargar(f"{URL_BASE}/{zip_nombre}", zip_ruta)
            print(f"Descomprimiendo: {zip_nombre}")
            with zipfile.ZipFile(zip_ruta) as z:
                z.extractall(DIR_DATOS)
            os.remove(zip_ruta)
        verificar(csv_ruta, COLUMNAS_ESPERADAS[csv_nombre])

    fd_ruta = os.path.join(DIR_DATOS, FD_ARCHIVO)
    if not os.path.exists(fd_ruta):
        descargar(FD_URL, fd_ruta)
    print(f"Descriptor de archivos: {fd_ruta}")

    print("\nDescarga completa. Archivos listos en data/")
    print("Siguiente paso: python limpieza.py")


if __name__ == "__main__":
    main()
