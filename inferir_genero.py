import pandas as pd
import unicodedata
import re
import os
from datetime import datetime

# Archivo de entrada
archivo_entrada = 'data_in/nombres_unicos.csv'
currentDate = datetime.now().strftime("%Y%m%d%H%M%S")

# --- DICCIONARIOS ---
diccionario_masculino = set([
    "juan", "carlos", "andres", "luis", "miguel", "jose", "alberto", "fernando", "manuel", "moises",
    "samuel", "elias", "pablo", "pedro", "gabriel", "angel", "francisco", "daniel", "sebastian", "fabio",
    "ramon", "roberto", "ricardo", "diego", "oscar", "martin", "victor", "julio", "alvaro", "hector",
    "cesar", "sergio", "gustavo", "rafael", "jesus", "ignacio", "enrique", "jorge", "eduardo", "adrian",
    "bryan", "kevin", "alex", "david", "brandon", "christopher", "anthony", "alan", "jason", "nicolas",
    "dylan", "isaac", "nathan", "anderson", "william", "harold", "nelson", "aaron", "javier", "clemente",
    "benjamin", "salvador", "ernesto", "armando", "hugo", "felipe", "marco", "oswaldo", "osvaldo",
    "jaime", "leonardo", "esteban", "jimmy", "frank", "franklin", "welcome", "keneddy", "arnold", "arnoldo",
    "cristian", "cristiano", "cristobal", "anibal", "alberico", "eloy","bernardo", "almagro", "metodio", 
    "hyacinth", 
    # Compuestos (ejemplos, añadir muchos más)
    "juan jose", "luis daniel", "jose maria", "juan carlos", "miguel angel", "jose luis", "carlos alberto", "natividad bernardo"
])

diccionario_femenino = set([
    "maria", "ana", "sofia", "carla", "gabriela", "fernanda", "isabel", "priscila", "veronica", "magdalena",
    "antonia", "margarita", "raquel", "ester", "nancy", "pamela", "rosario", "nelly", "trinidad", "patricia",
    "catalina", "juliana", "adriana", "paola", "lucia", "daniela", "monica", "alejandra", "lorena", "karla",
    "vanessa", "ximena", "elena", "mariela", "melissa", "estefania", "kimberly", "ashley", "samantha", "valeria",
    "camila", "allison", "angela", "cristina", "victoria", "aurora", "gloria", "alicia", "silvia", "carolina", "xochil",
    "marisol", "mireya", "liliana", "yolanda", "irma", "miriam", "teresa", "mariana", "carmen", "beatriz", "martha", "luz", "diana", "sandra",
    "rocio", "xiomara", "elizabeth", "xinia", "xianny", "caridad", "dinorah", "lilian", "amparo", "ines", "felicitas",
    "mercedes", "angeles", "inmaculada", "purisima", "concepcion", "dolores", "refugio", "gladys", "consuelo", "adoracion", "edith",
    "francinieri", "yenori", "idali", "ivonne","lidiette","telli", "elzi","elsida", "liliam", "irene", "yueni", 
    # Compuestos (ejemplos, añadir muchos más)
    "maria jose", "ana maria", "maria fernanda", "maria de los angeles", "maria del carmen", "luz maria", "elisa del rosario",
    "irma de jesus", "carmen edith", "maria isabel", "maria luisa", "yenori idali", "ivonne lidiette", "liliam irene"
])

# Partículas a ignorar/eliminar para el análisis de componentes individuales
# (después de verificar el nombre completo en diccionario)
particulas_a_ignorar = re.compile(r'\b(de|del|la|los|las)\b')

def normalizar_nombre(nombre):
    if not isinstance(nombre, str):
        nombre = str(nombre)
    nombre = nombre.lower().strip()
    # Mantener esta normalización para la búsqueda inicial en diccionario
    nombre_unicode = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8')
    nombre_limpio = re.sub(r'[^a-z ]', '', nombre_unicode) # Solo minúsculas y espacios
    nombre_limpio = re.sub(r'\s+', ' ', nombre_limpio).strip() # Normalizar múltiples espacios a uno solo
    return nombre_limpio

def inferir_genero_mejorado(nombre_norm):
    if not nombre_norm:
        return 'desconocido', 'nombre_vacio'

    # 1. Búsqueda en diccionario del nombre completo
    if nombre_norm in diccionario_masculino:
        return 'masculino', 'dic_completo'
    if nombre_norm in diccionario_femenino:
        return 'femenino', 'dic_completo'

    # 2. Procesamiento de nombres compuestos (si no se encontró el nombre completo)
    partes = nombre_norm.split()
    
    # Eliminar partículas para el análisis de partes individuales
    partes_sin_particulas = [p for p in partes if p not in ['de', 'del', 'la', 'los', 'las', 'de los']]

    if not partes_sin_particulas: # Si solo eran partículas
        return 'desconocido', 'solo_particulas'

    # 2.1. Analizar el primer nombre significativo
    primer_nombre = partes_sin_particulas[0]
    if primer_nombre in diccionario_masculino:
        # Considerar casos como "Jose Maria" (M) vs "Maria Jose" (F)
        # Si el primer nombre es Jose y hay un segundo nombre Maria, es Masculino
        if primer_nombre == "jose" and len(partes_sin_particulas) > 1 and partes_sin_particulas[1] == "maria":
            return 'masculino', 'dic_compuesto_especial_jose_maria'
        return 'masculino', 'dic_primer_nombre'
    
    if primer_nombre in diccionario_femenino:
        # Si el primer nombre es Maria y hay un segundo nombre Jose, es Femenino
        if primer_nombre == "maria" and len(partes_sin_particulas) > 1 and partes_sin_particulas[1] == "jose":
            return 'femenino', 'dic_compuesto_especial_maria_jose'
        return 'femenino', 'dic_primer_nombre'

    # 3. Heurísticas aplicadas al primer nombre significativo (o al nombre completo si es simple)
    # Usamos 'primer_nombre' para heurísticas, o 'nombre_norm' si prefieres aplicar al nombre completo
    # cuando no es compuesto o el compuesto no dio resultado claro.
    # Para esta implementación, usaremos 'primer_nombre' si es diferente de 'nombre_norm',
    # de lo contrario 'nombre_norm'.
    
    nombre_a_evaluar_heuristicas = primer_nombre # O nombre_norm si es un solo nombre o no se pudo con partes

    # Terminaciones femeninas fuertes
    if nombre_a_evaluar_heuristicas.endswith(('a', 'ia', 'ina', 'ela', 'isa', 'ana', 'ila', 'ita', 'ada', 'liz', 'luz', 'dad', 'cion', 'ione', ' اسلامیة')): # ' اسلامیة' no es relevante para CR
         if nombre_a_evaluar_heuristicas.endswith('elias'): # Excepción: Elias es M
            return 'masculino', 'heuristica_excepcion'
         # Podrías añadir más excepciones aquí (ej. Nicolas termina en 'as' pero es M)
         if nombre_a_evaluar_heuristicas not in ['elias', 'nicolas', 'jonas', 'tobias', 'isaias', 'matias', 'andres', 'zacarias']: # Algunos nombres masculinos terminan en 'as'
            return 'femenino', 'heuristica_terminacion_f'

    # Terminaciones masculinas fuertes
    if nombre_a_evaluar_heuristicas.endswith(('o', 'ol', 'or', 'an', 'en', 'in', 'on', 'un', 'er', 'el', 'iel', 'tor', 'ron', 'mar', 'air', 'din', 'us', 'ez', 'es', 'is')): # 'ez', 'es', 'is' pueden ser apellidos pero también nombres
        # Excepciones: Paz (F), Consuelo (F), Amparo (F), Rocio (F), Trinidad (F), Carmen (F), Mar (puede ser F)
        if nombre_a_evaluar_heuristicas not in ['paz', 'consuelo', 'amparo', 'rocio', 'trinidad', 'carmen', 'marisol', 'isabel', 'dolores', 'mercedes', 'angeles', 'nieves', 'lourdes', 'inés', 'ester', 'raquel']:
            if nombre_a_evaluar_heuristicas.endswith('es') and nombre_a_evaluar_heuristicas in ['andres', 'moises']: # Nombres M terminados en 'es'
                 return 'masculino', 'heuristica_terminacion_m'
            if not nombre_a_evaluar_heuristicas.endswith(('es', 'is', 'ez')): # Ser más cuidadoso con 'es', 'is', 'ez'
                 return 'masculino', 'heuristica_terminacion_m'
            # Si termina en 'es', 'is', 'ez' y no es una excepción femenina, podría ser masculino
            if nombre_a_evaluar_heuristicas.endswith(('es', 'is', 'ez')) and nombre_a_evaluar_heuristicas not in diccionario_femenino:
                return 'masculino', 'heuristica_terminacion_m_es_is_ez'


    # 4. Heurísticas aplicadas al último nombre significativo si hay más de uno
    if len(partes_sin_particulas) > 1:
        ultimo_nombre = partes_sin_particulas[-1]
        if ultimo_nombre != primer_nombre: # Evitar re-evaluar si solo hay un nombre significativo
            if ultimo_nombre in diccionario_masculino:
                return 'masculino', 'dic_ultimo_nombre'
            if ultimo_nombre in diccionario_femenino:
                return 'femenino', 'dic_ultimo_nombre'
            
            # Aplicar heurísticas al último nombre también
            if ultimo_nombre.endswith(('a', 'ia', 'ina', 'ela', 'ana', 'ada', 'liz', 'luz', 'dad', 'cion')):
                 if ultimo_nombre not in ['elias', 'nicolas', 'jonas', 'isaias', 'matias']:
                    return 'femenino', 'heuristica_ultimonombre_f'
            if ultimo_nombre.endswith(('o', 'or', 'an', 'el', 'iel', 'us')):
                if ultimo_nombre not in ['paz', 'luz', 'marisol', 'isabel']:
                    return 'masculino', 'heuristica_ultimonombre_m'


    # 5. Fallback MUY conservador (última letra del primer nombre significativo)
    #    Evitar 'e' como indicador femenino fuerte en fallback.
    if primer_nombre.endswith('a'):
        return 'femenino', 'fallback_primera_a'
    if primer_nombre.endswith('o'):
        return 'masculino', 'fallback_primera_o'

    
    return 'desconocido', 'sin_regla_clara'

try:
    if not os.path.exists(archivo_entrada):
        raise FileNotFoundError(f"No se encontró el archivo '{archivo_entrada}'. Asegúrese de que esté en el mismo directorio que este script.")

    df = pd.read_csv(archivo_entrada, dtype={'nombre': str}) # Asegurar que nombre sea string

    if 'nombre' not in df.columns:
        raise ValueError("El archivo debe contener una columna llamada 'nombre'.")

    df.dropna(subset=['nombre'], inplace=True) # Eliminar filas donde 'nombre' es NaN

    df['nombre_original'] = df['nombre']
    df['nombre_normalizado'] = df['nombre'].apply(normalizar_nombre)

    # Aplicar inferencia mejorada
    resultados = df['nombre_normalizado'].apply(lambda x: pd.Series(inferir_genero_mejorado(x)))
    df[['GENERO', 'metodo_asignacion']] = resultados


    #------------------------
    # --- CREACIÓN Y GUARDADO DEL ARCHIVO DE DESCONOCIDOS ---
    # 1. Filtrar los desconocidos
    df_desconocidos = df[df['GENERO'] == 'desconocido'].copy() # Usar .copy() para evitar SettingWithCopyWarning

    # 2. Ordenar el DataFrame de desconocidos
    if not df_desconocidos.empty: # Solo ordenar y guardar si hay datos
        df_desconocidos.sort_values(by=['metodo_asignacion', 'GENERO', 'nombre_original'], inplace=True)

        # 3. Guardar el archivo de desconocidos
        if not os.path.exists('data_out'):
            os.makedirs('data_out')
        outfilename_desconocidos = f'{currentDate}_desconocidos_resultados.csv'
        df_desconocidos[['nombre_original', 'GENERO', 'metodo_asignacion']].to_csv(
            f'data_out/{outfilename_desconocidos}',
            sep=',',
            index=False,
            encoding='utf-8-sig'
        )
        print(f'✅ Archivo de desconocidos {outfilename_desconocidos} generado.')
    else:
        print("ℹ️ No se encontraron registros con género 'desconocido' para generar el archivo adicional.")
    # --- FIN DE LA SECCIÓN DE DESCONOCIDOS ---








    # Ordenar el DataFrame por la columna 'metodo_asignacion' antes de guardar
    df.sort_values(by=['metodo_asignacion', 'GENERO', 'nombre_original'], inplace=True)

    # Guardar el resultado principales
    if not os.path.exists('data_out'):
        os.makedirs('data_out')
    outfilename = f'{currentDate}_resultados.csv'
    df[['nombre_original', 'GENERO', 'metodo_asignacion']].to_csv(f'data_out/{outfilename}', sep=',', index=False, encoding='utf-8-sig') # utf-8-sig para Excel

    print(f'✅ Proceso finalizado. Archivo {outfilename} generado')

except FileNotFoundError as e:
    print(f"❌ Error de archivo: {e}")
except ValueError as e:
    print(f"❌ Error de valor: {e}")
except Exception as error:
    print(f"❌ Error inesperado: {error}")
finally:
    print("🔄 Proceso terminado.")