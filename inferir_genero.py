import pandas as pd
import unicodedata
import re
import os
from datetime import datetime

# Archivo de entrada
archivo_entrada = 'data_in/nombres_unicos.csv'

#CurrentDate
currentDate = datetime.now().strftime("%Y%m%d%H%M%S")


try: 
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
        "benjamin", "salvador",  "ernesto", "armando", "hugo", "felipe", "marco", "oswaldo", "osvaldo", "juan jose", 
        "jaime", "de jesus", "osvaldo", "leonardo", "esteban", "jimmy", "andres", "frank", "francisco", "franklin", "welcome", 
        "keneddy", "arnold", "arnoldo","cristian", "cristiano", "cristobal", "anibal", "alberto", "alberico", "luis daniel", "eloy"
    ])

    diccionario_femenino = set([
        "maria", "ana", "sofia", "carla", "gabriela", "fernanda", "isabel", "priscila", "veronica", "magdalena",
        "antonia", "margarita", "raquel", "ester", "nancy", "pamela", "rosario", "nelly", "trinidad", "patricia",
        "catalina", "juliana", "adriana", "paola", "lucia", "daniela", "monica", "alejandra", "lorena", "karla",
        "vanessa", "ximena", "elena", "mariela", "melissa", "estefania", "kimberly", "ashley", "samantha", "valeria",
        "camila", "allison", "angela", "cristina", "victoria", "aurora", "gloria", "alicia", "silvia", "carolina", "xochil" ,
        "marisol", "veronica", "mireya", "liliana", "yolanda", "irma", "aurora", "miriam", "teresa", "patricia",
        "mariana", "carmen", "beatriz", "martha", "luz", "diana", "sandra", "yolanda", "irma", "aurora",
        "miriam", "teresa", "patricia", "mariana", "beatriz", "martha", "diana", "sandra", "rocio", "xiomara", 
        "elizabeth", "xinia", "isabel", "xianny", "maria de la caridad", "caridad", "dinorah", "lilian", "amparo", "ines", "felicitas",
        "maria carmen", "mercedes","maria isabel", "maria del carmen", "maria de los angeles", "maria de los dolores", "maria de la luz", "maria de la paz",
        "maria de la esperanza", "maria de la salud", "maria de la merced", "maria de la asuncion", "maria de la inmaculada", "maria de la purisima",
        "maria de la concepcion", "maria de la visitacion", "maria de la luz", "angeles", "inmaculada", "purisima", "concepcion", "dolores", "elisa del rosario",
        "refugio", "gladys", "irma de jesus", "consuelo", "maria del carmen", "adoracion", "carmen edith", "edith", 'maria rosario'
         
    ])

    # Función para inferir género
    def inferir_genero(nombre):
        if nombre in diccionario_masculino:
            return 'masculino', 'diccionario'
        elif nombre in diccionario_femenino:
            return 'femenino', 'diccionario'
        else:
            if nombre.endswith(('a', 'ia', 'ina', 'ela', 'isa', 'ana', 'ila', 'ita', 'ona', 'nes', 'lian', 'liam', 'rah', 'dad', 'ma', 'ny', 'nia', 'ys', 'my')):
                return 'femenino', 'heuristica'
            elif nombre.endswith(('o', 'io', 'ito', 'eño', 'ano', 'el', 'iel', 'tor', 'ron')):
                return 'masculino', 'heuristica'
            else:
                # Como última opción de fallback
                if nombre[-1:] in ['a', 'e', 'i', 'y']:
                    return 'femenino', 'heuristica_fallback'
                else:
                    return 'masculino', 'heuristica_fallback'

    # Aplicar inferencia
    df[['GENERO', 'metodo_asignacion']] = df['nombre_normalizado'].apply(lambda x: pd.Series(inferir_genero(x)))


    # Guardar el resultado
    outfilename = f'{currentDate}_resultados.csv'

    df[['nombre_original', 'GENERO', 'metodo_asignacion']].to_csv(f'data_out/{outfilename}', sep= ',' , index=False)

    print(f'✅ Proceso finalizado. Archivo {outfilename} generado')

except Exception as error:
    print(f"❌ Error: {error}")
finally:
    print("🔄 Proceso terminado.")