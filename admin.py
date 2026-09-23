import db

def consultar_todos_los_articulos():
    """Consulta general de auditoría de artículos con taxonomías (tags y categorías)."""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("\n--- AUDITORÍA GENERAL DE ARTÍCULOS ---")
    cursor.execute("""
        SELECT a.article_id, a.title, u.name AS autor, a.status, TO_CHAR(a.published_date, 'YYYY-MM-DD HH24:MI')
        FROM articles a
        JOIN users u ON a.user_id = u.user_id
        ORDER BY a.article_id ASC
    """)
    
    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    if not filas:
        print("No hay artículos registrados.")
    else:
        for f in filas:
            art_id, titulo, autor, estado, fecha = f
            tags = db.obtener_tags(art_id)
            categorias = db.obtener_categorias(art_id)
            
            tax_info = []
            if tags:
                tax_info.append(f"Tags: [{tags}]")
            if categorias:
                tax_info.append(f"Categorías: [{categorias}]")
            
            tax_str = f" | {' - '.join(tax_info)}" if tax_info else ""
            print(f"ID: {art_id} | Título: {titulo} | Autor: {autor} | Estado: [{estado}] | Fecha: {fecha}{tax_str}")

def menu_restaurar_usuarios():
    print("\n--- USUARIOS OCULTOS (INACTIVOS) ---")
    inactivos = db.obtener_usuarios_inactivos()
    if not inactivos:
        print("No hay usuarios inactivos por restaurar.")
        return

    for u in inactivos:
        print(f"ID: {u[0]} | Nombre: {u[1]} | Email: {u[2]}")

    print("\n  ADVERTENCIA: Al reactivar a un usuario, todas sus publicaciones y comentarios")
    print("    asociados no volverán a ser visibles automáticamente en la aplicación, deben reactivarse manualmente.")

    try:
        user_id = int(input("\nIngrese el ID del usuario a restaurar (0 para cancelar): "))
        if user_id == 0:
            return
        
        ids_validos = [u[0] for u in inactivos]
        if user_id in ids_validos:
            db.restaurar_usuario_logico(user_id)
            print(f"\n Usuario ID {user_id} restaurado exitosamente a estado ACTIVO.")
            print("   (Si deseas ocultar una publicación específica de este usuario, hazlo individualmente).")
        else:
            print(" El ID ingresado no está en la lista de inactivos.")
    except ValueError:
        print("X Debe ingresar un número entero válido.")
    except Exception as e:
        print(f"X Error al restaurar el usuario: {e}")

def menu_restaurar_articulos():
    print("\n--- ARTÍCULOS OCULTOS (INACTIVOS) ---")
    inactivos = db.obtener_articulos_inactivos()
    if not inactivos:
        print("No hay artículos inactivos por restaurar.")
        return

    for a in inactivos:
        print(f"ID: {a[0]} | Título: {a[1]} | Autor: {a[2]}")

    try:
        art_id = int(input("\nIngrese el ID del artículo a restaurar (0 para cancelar): "))
        if art_id == 0:
            return
        
        ids_validos = [a[0] for a in inactivos]
        if art_id in ids_validos:
            db.restaurar_articulo_logico(art_id)
            print(f" Artículo ID {art_id} restaurado exitosamente a estado ACTIVO.")
        else:
            print(" El ID ingresado no está en la lista de inactivos.")
    except ValueError:
        print("X Debe ingresar un número entero válido.")
    except Exception as e:
        print(f"X Error al restaurar el artículo: {e}")

def menu_restaurar_comentarios():
    print("\n--- COMENTARIOS OCULTOS (INACTIVOS) ---")
    inactivos = db.obtener_comentarios_inactivos()
    if not inactivos:
        print("No hay comentarios inactivos por restaurar.")
        return

    for c in inactivos:
        print(f"ID Comentario: {c[0]} | ID Artículo: {c[1]} | Autor: {c[2]} | Texto: {c[3]}")

    try:
        comment_id = int(input("\nIngrese el ID del comentario a restaurar (0 para cancelar): "))
        if comment_id == 0:
            return
        
        ids_validos = [c[0] for c in inactivos]
        if comment_id in ids_validos:
            db.restaurar_comentario_logico(comment_id)
            print(f" Comentario ID {comment_id} restaurado exitosamente a estado ACTIVO.")
        else:
            print(" El ID ingresado no está en la lista de inactivos.")
    except ValueError:
        print("X Debe ingresar un número entero válido.")
    except Exception as e:
        print(f"X Error al restaurar el comentario: {e}")

def main():
    while True:
        print("\n" + "="*45)
        print("    PANEL DE ADMINISTRACIÓN Y RESTAURACIÓN   ")
        print("="*45)
        print("1. Ver y Restaurar Usuarios Inactivos")
        print("2. Ver y Restaurar Artículos Inactivos")
        print("3. Ver y Restaurar Comentarios Inactivos")
        print("4. Auditoría General (Todos los artículos)")
        print("5. Salir")
        
        opcion = input("\nSeleccione una opción (1-5): ").strip()

        if opcion == "1":
            menu_restaurar_usuarios()
        elif opcion == "2":
            menu_restaurar_articulos()
        elif opcion == "3":
            menu_restaurar_comentarios()
        elif opcion == "4":
            consultar_todos_los_articulos()
        elif opcion == "5":
            print("\nSaliendo del panel de administración. ¡Hasta luego!")
            break
        else:
            print("\n Opción no válida. Intente de nuevo.")

if __name__ == "__main__":
    main()