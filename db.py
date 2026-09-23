import oracledb

USER = "proyecto1"
PASSWORD = "MiPassword123"  # Cambia esto por tu contraseña si es distinta
DSN = "localhost:1521/FREEPDB1"

def get_connection():
    """Retorna una nueva conexión a Oracle Database."""
    return oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)

def obtener_usuarios():
    """Recupera la lista de usuarios registrados."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email FROM users ORDER BY name ASC")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios

def guardar_usuario(nombre, email):
    """Invoca el Stored Procedure sp_guardar_usuario."""
    conn = get_connection()
    cursor = conn.cursor()
    out_id = cursor.var(oracledb.NUMBER)
    cursor.callproc("sp_guardar_usuario", [nombre, email, out_id])
    
    val = out_id.getvalue()
    new_id = int(val[0]) if isinstance(val, list) else int(val)
    
    cursor.close()
    conn.close()
    return new_id

def listar_articulos():
    """Invoca sp_listar_articulos que retorna un SYS_REFCURSOR."""
    conn = get_connection()
    cursor = conn.cursor()
    ref_cursor = cursor.var(oracledb.CURSOR)
    cursor.callproc("sp_listar_articulos", [ref_cursor])
    
    res_cursor = ref_cursor.getvalue()
    rows = res_cursor.fetchall()
    
    # Se extraen y convierten a cadenas planas
    articulos = []
    for r in rows:
        art_id, titulo, autor, fecha, texto, num_comments = r
        texto_str = str(texto) if texto else ""
        articulos.append((art_id, titulo, autor, fecha, texto_str, num_comments))
        
    res_cursor.close()
    cursor.close()
    conn.close()
    return articulos

def crear_articulo(user_id, titulo, texto):
    """Invoca sp_crear_articulo."""
    conn = get_connection()
    cursor = conn.cursor()
    out_id = cursor.var(oracledb.NUMBER)
    cursor.callproc("sp_crear_articulo", [user_id, titulo, texto, out_id])
    
    val = out_id.getvalue()
    new_id = int(val[0]) if isinstance(val, list) else int(val)
    
    cursor.close()
    conn.close()
    return new_id

def eliminar_articulo_logico(article_id):
    """Invoca sp_eliminar_articulo_logico para ocultar el artículo sin borrarlo."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_eliminar_articulo_logico", [article_id])
    cursor.close()
    conn.close()

def obtener_comentarios(article_id):
    """Obtiene los comentarios de un artículo."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, comment_text, url 
        FROM comments 
        WHERE article_id = :1 
        ORDER BY comment_id ASC
    """, [article_id])
    comentarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return comentarios

def agregar_comentario(article_id, user_id, nombre, url, texto):
    """Invoca sp_agregar_comentario."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_agregar_comentario", [article_id, user_id, nombre, url, texto])
    cursor.close()
    conn.close()

def agregar_tag(article_id, nombre, url=None):
    """Invoca sp_asignar_tag; crea el tag si no existe y lo vincula al artículo."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_asignar_tag", [article_id, nombre, url])
    cursor.close()
    conn.close()

def obtener_tags(article_id):
    """Retorna los tags del artículo como texto mediante fn_listar_tags."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fn_listar_tags(:1) FROM dual", [article_id])
    tags = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return tags or ""

def agregar_categoria(article_id, nombre, url=None):
    """Invoca sp_asignar_categoria; crea la categoría si no existe y la vincula al artículo."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_asignar_categoria", [article_id, nombre, url])
    cursor.close()
    conn.close()

def obtener_categorias(article_id):
    """Retorna las categorías del artículo como texto mediante fn_listar_categorias."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fn_listar_categorias(:1) FROM dual", [article_id])
    categorias = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return categorias or ""