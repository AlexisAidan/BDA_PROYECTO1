import oracledb

USER = "system"
PASSWORD = "MiPassword123"  # Cambia esto por tu contraseña si es distinta
DSN = "localhost:1521/XEPDB1"

def ejecutar_main_sql():
    print("Conectando a la base de datos Oracle...")
    try:
        conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
        cursor = conn.cursor()
        print("Leyendo main.sql...")

        with open("main.sql", "r", encoding="utf-8") as f:
            contenido = f.read()

        # Limpiar espacios invisibles/especiales de la web (\xa0)
        contenido = contenido.replace('\xa0', ' ')

        # Separar por el carácter '/' que divide los bloques
        bloques = contenido.split('/')

        for idx, bloque in enumerate(bloques, 1):
            lineas_filtradas = []
            for linea in bloque.splitlines():
                l_strip = linea.strip()
                # Filtrar líneas vacías, comentarios y palabras basura de copia/pega como 'SQL' o '```'
                if not l_strip or l_strip.startswith('--') or l_strip.upper() in ['SQL', '```SQL', '```']:
                    continue
                lineas_filtradas.append(linea)

            if not lineas_filtradas:
                continue

            sql_stmt = "\n".join(lineas_filtradas).strip()
            sql_upper = sql_stmt.upper()

            # Determinar si es un bloque PL/SQL (BEGIN, DECLARE, PROCEDURE, FUNCTION)
            es_plsql = any(kw in sql_upper for kw in ["BEGIN", "DECLARE", "PROCEDURE", "FUNCTION"])

            if es_plsql:
                
                if not sql_stmt.endswith(';'):
                    sql_stmt += ';'
            else:
                
                if sql_stmt.endswith(';'):
                    sql_stmt = sql_stmt[:-1].strip()

            try:
                cursor.execute(sql_stmt)
            except Exception as e:
                print(f"\n[X] Error en el bloque #{idx}:")
                print("--- SENTENCIA FALLIDA ---")
                print(sql_stmt)
                print("------------------------")
                raise e

        conn.commit()
        cursor.close()
        conn.close()
        print(" Base de datos reinstalada y limpia con éxito.")

    except Exception as e:
        print(f"\nX Ocurrió un error al cargar el esquema: {e}")

if __name__ == "__main__":
    ejecutar_main_sql()