#Ejecuta el Script:
#-------------------------------------------------------------
#Abre una terminal o línea de comandos, navega al directorio del proyecto y ejecuta:
#python3 03ground_truth.py

#Puedes también usar los argumentos si tus carpetas se llaman diferente:
#python3 03ground_truth.py --validation_dir mi_carpeta_de_validacion --output_dir mi_carpeta_de_metricas

#-------------------------------------------------------------
#¿Qué hace el script?

#Encuentra el archivo de validación: Busca en data_validation/ (o el directorio especificado) el archivo *_muestras_para_validacion.csv más reciente.
#Lee los datos validados: Carga el archivo y se asegura de que existan las columnas GENERO (predicción de tu script original) y GENERO_VALIDADO (tu entrada manual).
#Filtra validados: Solo considera las filas donde GENERO_VALIDADO tenga un valor (es decir, las que realmente validaste).
#Calcula Métricas (usando scikit-learn):
#Accuracy: El porcentaje total de predicciones correctas.
#Classification Report: Proporciona precisión, recall, F1-score y "support" (número de ocurrencias reales) para cada clase ('masculino', 'femenino', 'desconocido', y cualquier otra que hayas usado en GENERO_VALIDADO).
#Precisión (por clase): De los que el sistema dijo que eran (ej. masculinos), cuántos realmente lo eran. (TP / (TP + FP))
#Recall (por clase): De los que realmente eran (ej. masculinos), cuántos identificó correctamente el sistema. (TP / (TP + FN))
#F1-score (por clase): Media armónica de precisión y recall, buen indicador general del rendimiento por clase.
#Confusion Matrix (Matriz de Confusión): Una tabla que muestra:
#Filas: Género real (de GENERO_VALIDADO).
#Columnas: Género predicho (de GENERO).
#Celdas: Número de veces que una instancia de un género real fue clasificada como un género predicho. Idealmente, los números más altos estarán en la diagonal (predicciones correctas).
#Muestra en Consola: Imprime las métricas en la terminal.
#Guarda en Archivo:
#Crea la carpeta 03_ground_truth/ si no existe.
#Guarda un archivo CSV (ej. 20231027103000_ground_truth_metrics.csv) que contiene:
#Información general (archivo fuente, fecha, total validados, accuracy).
#El reporte de clasificación detallado.
#La matriz de confusión.
#-------------------------------------------------------------

#-------------------------------------------------------------
#Interpretación de las Métricas:
#Accuracy alta: Bueno, pero puede ser engañoso si las clases están desbalanceadas (ej., si el 90% de tus nombres son masculinos y tu sistema siempre dice "masculino", tendrá un 90% de accuracy pero será inútil para los femeninos).
#Classification Report:
#Clase "desconocido":
#Si el recall para "masculino" y "femenino" es bajo, significa que tu sistema está fallando en identificar muchos nombres que sí tienen un género definido, mandándolos a "desconocido".
#Si la precision para "desconocido" (en y_pred) es baja cuando lo comparas con lo que validaste (quizás algunos "desconocidos" sí tenían género en tu validación), indica que tu sistema está siendo demasiado conservador.
#Clases "masculino" / "femenino":
#Busca un buen balance entre precision y recall (reflejado en el F1-score).
#Si la precision es baja para "masculino", significa que cuando tu sistema dice "masculino", a veces se equivoca (es un nombre femenino o desconocido).
#Si el recall es bajo para "masculino", significa que hay muchos nombres masculinos que tu sistema no está identificando como tal.
#Matriz de Confusión: Te muestra exactamente dónde se están cometiendo los errores. Por ejemplo, ¿cuántos nombres femeninos reales (GENERO_VALIDADO='femenino') fueron incorrectamente clasificados como masculinos (GENERO='masculino')?
#-------------------------------------------------------------


#!pip install scikit-learn 
import pandas as pd
import os
import argparse
from datetime import datetime
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def encontrar_archivo_validacion_mas_reciente(directorio_data_validation):
    """
    Encuentra el archivo de validación más reciente en la carpeta especificada
    basado en el sufijo '_muestras_para_validacion.csv'.
    """
    archivos_candidatos = []
    if not os.path.exists(directorio_data_validation):
        print(f"❌ Error: El directorio '{directorio_data_validation}' no existe.")
        return None

    for nombre_archivo in os.listdir(directorio_data_validation):
        if nombre_archivo.endswith('_muestras_para_validacion.csv'):
            archivos_candidatos.append(os.path.join(directorio_data_validation, nombre_archivo))

    if not archivos_candidatos:
        print(f"❌ Error: No se encontraron archivos '*_muestras_para_validacion.csv' en '{directorio_data_validation}'.")
        print("   Asegúrate de haber ejecutado primero el script 'generar_muestras_validacion.py' y completado la validación manual.")
        return None

    # Ordenar por fecha de modificación para obtener el más reciente
    # o por nombre si el nombre contiene la fecha al inicio
    # Asumimos que el nombre contiene la fecha y hora, por lo que el sort alfabético inverso funciona
    archivos_candidatos.sort(key=os.path.basename, reverse=True)
    return archivos_candidatos[0]

def calcular_y_guardar_metricas(archivo_validacion, directorio_salida_metricas):
    """
    Lee el archivo de validación completado, calcula métricas y guarda los resultados.
    """
    try:
        df_val = pd.read_csv(archivo_validacion)
        print(f"✅ Archivo de validación '{archivo_validacion}' leído correctamente.")
    except FileNotFoundError:
        print(f"❌ Error: No se pudo encontrar el archivo de validación '{archivo_validacion}'.")
        return
    except Exception as e:
        print(f"❌ Error al leer el archivo CSV '{archivo_validacion}': {e}")
        return

    # Verificar columnas necesarias
    columnas_necesarias = ['GENERO', 'GENERO_VALIDADO']
    for col in columnas_necesarias:
        if col not in df_val.columns:
            print(f"❌ Error: La columna requerida '{col}' no se encuentra en el archivo de validación.")
            print("   Asegúrate de que el archivo de validación contiene las columnas 'GENERO' (predicción) y 'GENERO_VALIDADO' (manual).")
            return

    # Filtrar filas donde GENERO_VALIDADO no esté vacío (es decir, que fueron validadas)
    df_val_completado = df_val.dropna(subset=['GENERO_VALIDADO'])
    if df_val_completado.empty:
        print("❌ Error: No hay filas con 'GENERO_VALIDADO' completado en el archivo.")
        print("   Por favor, completa la validación manual en la columna 'GENERO_VALIDADO'.")
        return
    
    print(f"ℹ️ {len(df_val_completado)} registros validados encontrados para el cálculo de métricas.")

    y_true = df_val_completado['GENERO_VALIDADO']
    y_pred = df_val_completado['GENERO']

    # Obtener todas las etiquetas únicas presentes en y_true y y_pred para la matriz de confusión
    labels = sorted(list(set(y_true.unique()) | set(y_pred.unique())))


    # Calcular métricas
    accuracy = accuracy_score(y_true, y_pred)
    report_dict = classification_report(y_true, y_pred, output_dict=True, zero_division=0, labels=labels)
    conf_matrix = confusion_matrix(y_true, y_pred, labels=labels)

    print("\n--- Métricas de Clasificación ---")
    print(f"Accuracy General: {accuracy:.4f}")
    print("\nReporte de Clasificación:")
    print(classification_report(y_true, y_pred, zero_division=0, labels=labels))
    print("\nMatriz de Confusión:")
    # Crear un DataFrame para la matriz de confusión para mejor visualización
    df_conf_matrix = pd.DataFrame(conf_matrix, index=[f'Actual: {l}' for l in labels], columns=[f'Predicted: {l}' for l in labels])
    print(df_conf_matrix)

    # Preparar datos para guardar en CSV
    df_report = pd.DataFrame(report_dict).transpose()
    
    # Crear directorio de salida si no existe
    if not os.path.exists(directorio_salida_metricas):
        os.makedirs(directorio_salida_metricas)
        print(f"Directorio '{directorio_salida_metricas}' creado.")

    # Guardar reporte y matriz de confusión
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    nombre_archivo_salida = f"{timestamp}_ground_truth_metrics.csv"
    ruta_archivo_salida = os.path.join(directorio_salida_metricas, nombre_archivo_salida)

    try:
        with open(ruta_archivo_salida, 'w', encoding='utf-8-sig') as f:
            f.write(f"Metricas de Evaluacion para el archivo: {os.path.basename(archivo_validacion)}\n")
            f.write(f"Fecha de generacion de metricas: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de registros validados: {len(df_val_completado)}\n")
            f.write(f"Accuracy General: {accuracy:.4f}\n\n")
            
            f.write("Reporte de Clasificacion:\n")
            df_report.to_csv(f, index=True)
            f.write("\n\n")
            
            f.write("Matriz de Confusion:\n")
            df_conf_matrix.to_csv(f, index=True)
        
        print(f"\n✅ Métricas guardadas en '{ruta_archivo_salida}'.")

    except Exception as e:
        print(f"❌ Error al guardar el archivo de métricas '{ruta_archivo_salida}': {e}")

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Calcula métricas de clasificación a partir de un archivo de validación manual.")
        parser.add_argument(
            "--validation_dir",
            type=str,
            default="02data_validation",
            help="Directorio donde se encuentra el archivo de validación completado (por defecto: 02data_validation)."
        )
        parser.add_argument(
            "--output_dir",
            type=str,
            default="03ground_truth",
            help="Directorio donde se guardarán las métricas calculadas (por defecto: 03ground_truth)."
        )

        args = parser.parse_args()

        archivo_validacion_seleccionado = encontrar_archivo_validacion_mas_reciente(args.validation_dir)

        if archivo_validacion_seleccionado:
            print(f"ℹ️ Usando el archivo de validación más reciente: '{archivo_validacion_seleccionado}'")
            calcular_y_guardar_metricas(archivo_validacion_seleccionado, args.output_dir)
        else:
            print("🚫 No se pudo proceder sin un archivo de validación.")

       
    except Exception as error:
        print(f"❌ Error inesperado: {error}")
    finally:
        print("🔄 Proceso de cálculo de métricas terminado.")

