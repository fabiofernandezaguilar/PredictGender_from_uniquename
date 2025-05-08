import pandas as pd
import unicodedata
import re
import os

# Archivo de entrada
archivo_entrada = 'nombres_unicos_312915.csv'

if not os.path.exists(archivo_entrada):
    raise FileNotFoundError(f"No se encontró el archivo '{archivo_entrada}'. Asegúrese de que esté en el mismo directorio que este script.")

# Cargar los nombres
df = pd.read_csv(archivo_entrada)

if 'nombre' not in df.columns:
    raise ValueError("El archivo debe contener una columna llamada 'nombre'.")

# Normalizar los nombres
def normalizar_nombre(nombre):
    nombre = str(nombre).lower().strip()
    nombre = unicodedata.normalize('NFKD', nombre).encode('ASCII', 'ignore').decode('utf-8')
    nombre = re.sub(r'[^a-zA-Z ]', '', nombre)
    return nombre

df['nombre_original'] = df['nombre']  # Guardar copia del nombre original
df['nombre_normalizado'] = df['nombre'].apply(normalizar_nombre)

# Diccionarios ampliados básicos
diccionario_masculino = set([
    "juan", "carlos", "andres", "luis", "miguel", "jose", "alberto", "fernando", "manuel", "moises",
    "samuel", "elias", "pablo", "pedro", "gabriel", "angel", "francisco", "daniel", "sebastian", "fabio",
    "ramon", "roberto", "ricardo", "diego", "oscar", "martin", "victor", "julio", "alvaro", "hector",
    "cesar", "sergio", "gustavo", "rafael", "jesus", "ignacio", "enrique", "jorge", "eduardo", "adrian",
    "bryan", "kevin", "alex", "david", "brandon", "christopher", "anthony", "alan", "jason", "nicolas",
    "dylan", "isaac", "nathan", "anderson", "william", "harold", "nelson", "aaron", "javier", "clemente",
    "benjamin", "salvador",  "ernesto", "armando", "hugo", "felipe", "marco", "oswaldo", "osvaldo"  
])

diccionario_femenino = set([
    "maria", "ana", "sofia", "carla", "gabriela", "fernanda", "isabel", "priscila", "veronica", "magdalena",
    "antonia", "margarita", "raquel", "ester", "nancy", "pamela", "rosario", "nelly", "trinidad", "patricia",
    "catalina", "juliana", "adriana", "paola", "lucia", "daniela", "monica", "alejandra", "lorena", "karla",
    "vanessa", "ximena", "elena", "mariela", "melissa", "estefania", "kimberly", "ashley", "samantha", "valeria",
    "camila", "allison", "angela", "cristina", "victoria", "aurora", "gloria", "alicia", "silvia", "carolina", "xochil" ,
    "marisol", "veronica", "mireya", "liliana", "yolanda", "irma", "aurora", "miriam", "teresa", "patricia",
    "mariana", "carmen", "beatriz", "martha", "luz", "diana", "sandra", "yolanda", "irma", "aurora",
    "miriam", "teresa", "patricia", "mariana", "carmen", "beatriz", "martha", "luz", "diana", "sandra", "rocio", "xiomara", "elizabeth", "xinia", "isabel", "xianny"
])

# Función para inferir género
def inferir_genero(nombre):
    if nombre in diccionario_masculino:
        return 'masculino', 'diccionario'
    elif nombre in diccionario_femenino:
        return 'femenino', 'diccionario'
    else:
        if nombre.endswith(('a', 'ia', 'ina', 'ela', 'isa', 'ana', 'ila', 'ita', 'ona')):
            return 'femenino', 'heuristica'
        elif nombre.endswith(('o', 'io', 'ito', 'eño', 'ano', 'el', 'iel', 'tor')):
            return 'masculino', 'heuristica'
        else:
            # Como última opción de fallback
            if nombre[-1:] in ['a', 'e', 'i', 'y']:
                return 'femenino', 'heuristica_fallback'
            else:
                return 'masculino', 'heuristica_fallback'

# Aplicar inferencia
df[['genero_asignado', 'metodo_asignacion']] = df['nombre_normalizado'].apply(lambda x: pd.Series(inferir_genero(x)))

# Guardar el resultado
df[['nombre_original', 'genero_asignado', 'metodo_asignacion']].to_csv('resultado_con_genero_v3-1.csv', index=False)

print("✅ Proceso finalizado. Archivo generado: resultado_con_genero_final.csv")
