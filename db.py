import oracledb

USER = "system"
PASSWORD = "MiPassword123"  # Cambia esto por tu información personal
DSN = "localhost:1521/XEPDB1"

def get_connection():
    """Nueva conexión a Oracle Database."""
    return oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)


# USUARIOS


def obtener_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email FROM users WHERE status = 'ACTIVO' ORDER BY name ASC")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios

def obtener_usuarios_inactivos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, name, email FROM users WHERE status = 'INACTIVO' ORDER BY user_id ASC")
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return usuarios

def guardar_usuario(nombre, email):
    conn = get_connection()
    cursor = conn.cursor()
    out_id = cursor.var(oracledb.NUMBER)
    cursor.callproc("sp_guardar_usuario", [nombre, email, out_id])
    
    val = out_id.getvalue()
    new_id = int(val[0]) if isinstance(val, list) else int(val)
    
    cursor.close()
    conn.close()
    return new_id

def eliminar_usuario_logico(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_eliminar_usuario_logico", [user_id])
    cursor.close()
    conn.close()

def restaurar_usuario_logico(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_restaurar_usuario_logico", [user_id])
    cursor.close()
    conn.close()


# ARTÍCULOS


def listar_articulos():
    conn = get_connection()
    cursor = conn.cursor()
    ref_cursor = cursor.var(oracledb.CURSOR)
    cursor.callproc("sp_listar_articulos", [ref_cursor])
    
    res_cursor = ref_cursor.getvalue()
    rows = res_cursor.fetchall()
    
    articulos = []
    for r in rows:
        art_id, titulo, autor, fecha, texto, num_comments = r
        texto_str = str(texto) if texto else ""
        articulos.append((art_id, titulo, autor, fecha, texto_str, num_comments))
        
    res_cursor.close()
    cursor.close()
    conn.close()
    return articulos

def obtener_articulos_inactivos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.article_id, a.title, u.name 
        FROM articles a 
        JOIN users u ON a.user_id = u.user_id 
        WHERE a.status = 'INACTIVO' 
        ORDER BY a.article_id ASC
    """)
    articulos = cursor.fetchall()
    cursor.close()
    conn.close()
    return articulos

def crear_articulo(user_id, titulo, texto):
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
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_eliminar_articulo_logico", [article_id])
    cursor.close()
    conn.close()

def restaurar_articulo_logico(article_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_restaurar_articulo_logico", [article_id])
    cursor.close()
    conn.close()


# COMENTARIOS


def obtener_comentarios(article_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT comment_id, name, comment_text, url 
        FROM comments 
        WHERE article_id = :1 AND status = 'ACTIVO'
        ORDER BY comment_id ASC
    """, [article_id])
    comentarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return comentarios

def obtener_comentarios_inactivos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.comment_id, c.article_id, c.name, c.comment_text 
        FROM comments c 
        WHERE c.status = 'INACTIVO' 
        ORDER BY c.comment_id ASC
    """)
    comentarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return comentarios

def agregar_comentario(article_id, user_id, nombre, url, texto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_agregar_comentario", [article_id, user_id, nombre, url, texto])
    cursor.close()
    conn.close()

def eliminar_comentario_logico(comment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_eliminar_comentario_logico", [comment_id])
    cursor.close()
    conn.close()

def restaurar_comentario_logico(comment_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_restaurar_comentario_logico", [comment_id])
    cursor.close()
    conn.close()


#  TAGS Y CATEGORÍAS


def agregar_tag(article_id, nombre, url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_asignar_tag", [article_id, nombre, url])
    cursor.close()
    conn.close()

def obtener_tags(article_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fn_listar_tags(:1) FROM dual", [article_id])
    res = cursor.fetchone()
    tags = res[0] if res else ""
    cursor.close()
    conn.close()
    return tags or ""

def agregar_categoria(article_id, nombre, url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.callproc("sp_asignar_categoria", [article_id, nombre, url])
    cursor.close()
    conn.close()

def obtener_categorias(article_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fn_listar_categorias(:1) FROM dual", [article_id])
    res = cursor.fetchone()
    categorias = res[0] if res else ""
    cursor.close()
    conn.close()
    return categorias or ""