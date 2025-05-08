### Instrucciones de ejeccuón de este programa
#------------------------------------------------------------- 
#Ejecutar desde la Terminal:

#Abre una terminal o línea de comandos, navega al directorio donde guardaste el script y ejecútalo.
#Con valores por defecto (500 muestras por género, busca en data_out):
#python generar_muestras_validacion.py

## Especificando el tamaño de la muestra:
## python3 02datavalidation.py --sample_size 100

#Especificando el directorio de entrada y el archivo de salida (si es necesario):
#python generar_muestras_validacion.py --input_dir mi_otra_carpeta_out --sample_size 200 --output_file data_validation/mis_muestras_custom.csv

#-------------------------------------------------------------
#¿Qué hace el script?

#Encuentra el archivo de resultados más reciente: Busca en la carpeta data_out (o la que especifiques) el último archivo que termine en _resultados_completos.csv (este es el nombre que sugerí para el archivo principal en el script anterior).
#Lee el archivo: Carga los datos de ese CSV.
#Identifica Géneros: Encuentra todas las categorías únicas en la columna GENERO (deberían ser 'masculino', 'femenino', 'desconocido').
#Toma Muestras: Para cada categoría de género:
#Filtra los registros correspondientes a ese género.
#Si hay suficientes registros, toma una muestra aleatoria del tamaño especificado (sample_size).
#Si hay menos registros que sample_size, toma todos los registros disponibles para ese género.
#Usa random_state=42 para que si ejecutas el script múltiples veces con los mismos datos de entrada, obtengas la misma muestra (esto es bueno para la reproducibilidad).
#Combina las Muestras: Une todas las muestras en un solo DataFrame.
#Prepara para Validación:
#Añade una nueva columna llamada GENERO_VALIDADO, que estará vacía.
#Selecciona las columnas más relevantes para la validación: nombre_original, GENERO (el inferido por tu script), metodo_asignacion, y GENERO_VALIDADO.
#Guarda el Archivo de Salida: Guarda este DataFrame en un nuevo archivo CSV (por defecto, en la carpeta data_validation con un nombre que incluye la fecha y hora).
#-------------------------------------------------------------

#Siguiente Paso: Validación Manual

#Abre el archivo CSV generado (ej., 02data_validation/YYYYMMDDHHMMSS_muestras_para_validacion.csv).
#Revisa cada nombre_original.
#En la columna GENERO_VALIDADO, escribe el género correcto (ej., 'masculino', 'femenino', o quizás 'unisex'/'ambiguo' si encuentras esos casos y decides manejarlos).
#La columna GENERO te muestra lo que tu script original infirió, y metodo_asignacion te dice cómo llegó a esa conclusión. Esto te ayudará a entender dónde acierta 
#y dónde falla tu sistema.
#Ejecutar el python del siguiente script "03ground_truth.py" para generar el archivo de ground truth con los resultados de la validación manual.



import pandas as pd
import os
import argparse
from datetime import datetime

def encontrar_archivo_resultados_mas_reciente(directorio_data_out):
    """
    Encuentra el archivo de resultados más reciente en la carpeta data_out
    basado en el prefijo de fecha y el sufijo '_resultados_completos.csv'.
    """
    archivos_candidatos = []
    if not os.path.exists(directorio_data_out):
        print(f"❌ Error: El directorio '{directorio_data_out}' no existe.")
        return None

    for nombre_archivo in os.listdir(directorio_data_out):
        if nombre_archivo.endswith('_resultados_completos.csv'): # Asegúrate que coincide con el nombre del archivo principal
            archivos_candidatos.append(nombre_archivo)

    if not archivos_candidatos:
        print(f"❌ Error: No se encontraron archivos '*_resultados_completos.csv' en '{directorio_data_out}'.")
        return None

    # Ordenar para obtener el más reciente (asumiendo formato YYYYMMDDHHMMSS al inicio)
    archivos_candidatos.sort(reverse=True)
    return os.path.join(directorio_data_out, archivos_candidatos[0])

def generar_muestras_para_validacion(archivo_entrada, tamano_muestra_por_genero, archivo_salida):
    """
    Lee el archivo de resultados, toma muestras aleatorias por género y
    guarda un nuevo archivo para validación manual.
    """
    try:
        df = pd.read_csv(archivo_entrada)
        print(f"✅ Archivo de entrada '{archivo_entrada}' leído correctamente. Columnas: {df.columns.tolist()}")
    except FileNotFoundError:
        print(f"❌ Error: No se pudo encontrar el archivo de entrada '{archivo_entrada}'.")
        return
    except Exception as e:
        print(f"❌ Error al leer el archivo CSV '{archivo_entrada}': {e}")
        return

    if 'GENERO' not in df.columns or 'nombre_original' not in df.columns:
        print("❌ Error: El archivo de entrada debe contener las columnas 'GENERO' y 'nombre_original'.")
        return

    generos_unicos = df['GENERO'].unique()
    print(f"ℹ️ Géneros encontrados en el archivo: {generos_unicos}")

    lista_muestras = []

    for genero in generos_unicos:
        df_genero = df[df['GENERO'] == genero]
        n_registros_genero = len(df_genero)

        if n_registros_genero == 0:
            print(f"ℹ️ No hay registros para el género '{genero}'. Se omitirá.")
            continue

        # Ajustar el tamaño de la muestra si hay menos registros que el solicitado
        tamano_real_muestra = min(tamano_muestra_por_genero, n_registros_genero)

        if tamano_real_muestra > 0 :
            muestra = df_genero.sample(n=tamano_real_muestra, random_state=42) # random_state para reproducibilidad
            lista_muestras.append(muestra)
            print(f"ℹ️ Muestra tomada para '{genero}': {len(muestra)} registros.")
        else:
            print(f"ℹ️ No se tomaron muestras para '{genero}' (0 registros disponibles o tamaño de muestra 0).")


    if not lista_muestras:
        print("❌ No se pudo generar ninguna muestra. Verifique los datos de entrada.")
        return

    df_muestras_combinadas = pd.concat(lista_muestras)

    # Añadir columna para la validación manual
    df_muestras_combinadas['GENERO_VALIDADO'] = '' # Inicialmente vacía

    # Seleccionar y reordenar columnas para el archivo de salida
    columnas_salida = ['nombre_original', 'GENERO', 'metodo_asignacion', 'GENERO_VALIDADO']
    # Asegurarse de que todas las columnas de salida existan en df_muestras_combinadas
    columnas_existentes_para_salida = [col for col in columnas_salida if col in df_muestras_combinadas.columns]
    
    # Si falta 'metodo_asignacion' (por ejemplo, si el archivo de entrada no lo tiene), lo omitimos de la salida
    if 'metodo_asignacion' not in df_muestras_combinadas.columns and 'metodo_asignacion' in columnas_salida:
        print("⚠️ Advertencia: La columna 'metodo_asignacion' no se encontró en los datos. Se omitirá de la salida de validación.")
        columnas_existentes_para_salida.remove('metodo_asignacion')


    df_final_muestras = df_muestras_combinadas[columnas_existentes_para_salida]

    try:
        df_final_muestras.to_csv(archivo_salida, index=False, encoding='utf-8-sig')
        print(f"✅ Muestras para validación guardadas en '{archivo_salida}'. Contiene {len(df_final_muestras)} registros.")
        print("➡️ Siguiente paso: Abra este archivo y complete la columna 'GENERO_VALIDADO' manualmente.")
    except Exception as e:
        print(f"❌ Error al guardar el archivo de muestras '{archivo_salida}': {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera un archivo CSV con muestras aleatorias de nombres por género para validación manual.")
    parser.add_argument(
        "--input_dir",
        type=str,
        default="01data_out",
        help="Directorio donde se encuentra el archivo de resultados (por defecto: 01data_out)."
    )
    parser.add_argument(
        "--sample_size",
        type=int,
        default=500,
        help="Número de registros a muestrear por cada categoría de género (por defecto: 500)."
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default=f"02data_validation/{datetime.now().strftime('%Y%m%d%H%M%S')}_muestras_para_validacion.csv",
        help="Nombre del archivo CSV de salida para las muestras."
    )

    args = parser.parse_args()

    # Crear directorio de salida para validación si no existe
    output_dir_validation = os.path.dirname(args.output_file)
    if output_dir_validation and not os.path.exists(output_dir_validation):
        os.makedirs(output_dir_validation)
        print(f"Directorio '{output_dir_validation}' creado.")


    archivo_resultados_principal = encontrar_archivo_resultados_mas_reciente(args.input_dir)

    if archivo_resultados_principal:
        print(f"ℹ️ Usando el archivo de resultados más reciente: '{archivo_resultados_principal}'")
        generar_muestras_para_validacion(archivo_resultados_principal, args.sample_size, args.output_file)
    else:
        print("🚫 No se pudo proceder sin un archivo de entrada.")

    print("🔄 Proceso de generación de muestras terminado.")