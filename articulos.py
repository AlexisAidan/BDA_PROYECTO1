import db

def consultar_todos_los_articulos():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("\n--- TODOS LOS ARTÍCULOS EN LA BASE DE DATOS (INCLUYENDO BORRADOS LOGICAMENTE) ---")
    cursor.execute("""
        SELECT a.article_id, a.title, u.name AS autor, a.status, a.published_date,
               fn_listar_tags(a.article_id) AS tags,
               fn_listar_categorias(a.article_id) AS categorias
        FROM articles a
        JOIN users u ON a.user_id = u.user_id
        ORDER BY a.article_id ASC
    """)
    
    filas = cursor.fetchall()
    if not filas:
        print("No hay artículos registrados.")
    else:
        for f in filas:
            art_id, titulo, autor, estado, fecha, tags, categorias = f
            print(f"ID: {art_id} | Título: {titulo} | Autor: {autor} | Estado: [{estado}] | Fecha: {fecha}")
            print(f"    Tags: {tags or '-'} | Categorías: {categorias or '-'}")
            
    cursor.close()
    conn.close()

if __name__ == "__main__":
    consultar_todos_los_articulos()