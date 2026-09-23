import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import db

class BlogApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Blog - Oracle PL/SQL")
        self.geometry("980x650")
        self.minsize(850, 550)

        self.usuario_activo_id = None
        self.usuario_activo_nombre = None
        self.dict_usuarios = {}
        self.articulos_db = {}

        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        self.crear_interfaz()
        self.cargar_usuarios()
        self.cargar_articulos()

    def crear_interfaz(self):
        top_bar = ttk.Frame(self, padding=10)
        top_bar.pack(fill=tk.X, side=tk.TOP)

        ttk.Label(top_bar, text="Usuario Activo:", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
        
        self.combo_usuarios = ttk.Combobox(top_bar, state="readonly", width=25)
        self.combo_usuarios.pack(side=tk.LEFT, padx=5)
        self.combo_usuarios.bind("<<ComboboxSelected>>", self.seleccionar_usuario)

        btn_nuevo_usuario = ttk.Button(top_bar, text="+ Registrar Usuario", command=self.modal_registrar_usuario)
        btn_nuevo_usuario.pack(side=tk.LEFT, padx=5)

        btn_ocultar_usuario = ttk.Button(top_bar, text="🗑 Eliminar Usuario", command=self.eliminar_usuario)
        btn_ocultar_usuario.pack(side=tk.LEFT, padx=5)

        btn_nuevo_articulo = ttk.Button(top_bar, text="✍ Publicar Artículo", command=self.modal_crear_articulo)
        btn_nuevo_articulo.pack(side=tk.RIGHT, padx=5)

        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, padx=10, pady=5)

        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = ttk.Labelframe(main_paned, text=" Artículos Publicados ", padding=10)
        main_paned.add(left_frame, weight=1)

        columns = ("id", "titulo", "autor", "comentarios")
        self.tree_articulos = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        self.tree_articulos.heading("id", text="ID")
        self.tree_articulos.heading("titulo", text="Título")
        self.tree_articulos.heading("autor", text="Autor")
        self.tree_articulos.heading("comentarios", text="Comentarios")

        self.tree_articulos.column("id", width=40, anchor="center")
        self.tree_articulos.column("titulo", width=180)
        self.tree_articulos.column("autor", width=90)
        self.tree_articulos.column("comentarios", width=80, anchor="center")

        self.tree_articulos.pack(fill=tk.BOTH, expand=True)
        self.tree_articulos.bind("<<TreeviewSelect>>", self.on_articulo_seleccionado)

        right_frame = ttk.Labelframe(main_paned, text=" Lectura del Artículo y Comentarios ", padding=10)
        main_paned.add(right_frame, weight=2)

        self.lbl_titulo = ttk.Label(right_frame, text="Seleccione un artículo para leer", font=("Helvetica", 14, "bold"))
        self.lbl_titulo.pack(anchor=tk.W, pady=5)

        self.lbl_meta = ttk.Label(right_frame, text="", font=("Helvetica", 9, "italic"))
        self.lbl_meta.pack(anchor=tk.W, pady=2)

        self.lbl_tags = ttk.Label(right_frame, text="", font=("Helvetica", 9))
        self.lbl_tags.pack(anchor=tk.W, pady=2)

        self.txt_contenido = tk.Text(right_frame, wrap=tk.WORD, height=10)
        self.txt_contenido.pack(fill=tk.BOTH, expand=True, pady=5)

        btn_box = ttk.Frame(right_frame)
        btn_box.pack(fill=tk.X, pady=5)

        btn_comentar = ttk.Button(btn_box, text="💬 Agregar Comentario", command=self.modal_agregar_comentario)
        btn_comentar.pack(side=tk.LEFT, padx=2)

        btn_ocultar_comentario = ttk.Button(btn_box, text="🗑 Eliminar Comentario", command=self.eliminar_comentario)
        btn_ocultar_comentario.pack(side=tk.LEFT, padx=2)

        btn_tag = ttk.Button(btn_box, text="🏷 Agregar Tag", command=lambda: self.modal_asignar_taxonomia("tag"))
        btn_tag.pack(side=tk.LEFT, padx=2)

        btn_categoria = ttk.Button(btn_box, text="📂 Agregar Categoría", command=lambda: self.modal_asignar_taxonomia("categoria"))
        btn_categoria.pack(side=tk.LEFT, padx=2)

        btn_eliminar = ttk.Button(btn_box, text="🗑 Eliminar Artículo", command=self.eliminar_articulo)
        btn_eliminar.pack(side=tk.RIGHT, padx=2)

        ttk.Label(right_frame, text="Comentarios:", font=("Helvetica", 10, "bold")).pack(anchor=tk.W, pady=(10, 2))
        
        self.txt_comentarios = tk.Text(right_frame, wrap=tk.WORD, height=5, state=tk.DISABLED)
        self.txt_comentarios.pack(fill=tk.X, pady=5)

    def cargar_usuarios(self):
        try:
            usuarios = db.obtener_usuarios()
            self.dict_usuarios = {f"{u[1]} ({u[2]})": u[0] for u in usuarios}
            self.combo_usuarios['values'] = list(self.dict_usuarios.keys())
            
            if usuarios:
                self.combo_usuarios.current(0)
                self.seleccionar_usuario(None)
            else:
                self.combo_usuarios.set("")
                self.usuario_activo_id = None
                self.usuario_activo_nombre = None
        except Exception as e:
            messagebox.showerror("Error de Base de Datos", f"No se pudieron cargar usuarios:\n{e}")

    def seleccionar_usuario(self, event):
        seleccion = self.combo_usuarios.get()
        if seleccion in self.dict_usuarios:
            self.usuario_activo_id = self.dict_usuarios[seleccion]
            self.usuario_activo_nombre = seleccion.split(" (")[0]

    def cargar_articulos(self):
        for item in self.tree_articulos.get_children():
            self.tree_articulos.delete(item)

        self.articulos_db.clear()

        try:
            articulos = db.listar_articulos()
            for art in articulos:
                art_id = str(art[0])
                self.articulos_db[art_id] = art
                self.tree_articulos.insert("", tk.END, iid=art_id, values=(art[0], art[1], art[2], art[5]))
        except Exception as e:
            messagebox.showerror("Error", f"Error al listar artículos:\n{e}")

    def on_articulo_seleccionado(self, event):
        selected_item = self.tree_articulos.selection()
        if not selected_item:
            return

        art_id = str(selected_item[0])
        art = self.articulos_db.get(art_id)
        if not art:
            return

        _, titulo, autor, fecha, texto, _ = art

        self.lbl_titulo.config(text=titulo)
        self.lbl_meta.config(text=f"Por: {autor} | Fecha: {fecha}")

        self.txt_contenido.delete("1.0", tk.END)
        self.txt_contenido.insert(tk.END, texto)

        self.cargar_comentarios(art_id)
        self.refrescar_taxonomia(int(art_id))

    def cargar_comentarios(self, article_id):
        self.txt_comentarios.config(state=tk.NORMAL)
        self.txt_comentarios.delete("1.0", tk.END)

        try:
            comentarios = db.obtener_comentarios(article_id)
            if not comentarios:
                self.txt_comentarios.insert(tk.END, "Aún no hay comentarios activos en este artículo.")
            else:
                for c in comentarios:
                    self.txt_comentarios.insert(tk.END, f"• [ID: {c[0]}] {c[1]}: {c[2]}\n")
        except Exception as e:
            self.txt_comentarios.insert(tk.END, f"Error al cargar comentarios: {e}")

        self.txt_comentarios.config(state=tk.DISABLED)

    def refrescar_taxonomia(self, article_id):
        try:
            partes = []
            tags = db.obtener_tags(article_id)
            categorias = db.obtener_categorias(article_id)
            if tags:
                partes.append(f"🏷 Tags: {tags}")
            if categorias:
                partes.append(f"📂 Categorías: {categorias}")
            self.lbl_tags.config(text="  |  ".join(partes))
        except Exception as e:
            self.lbl_tags.config(text=f"Error al cargar tags/categorías: {e}")

    def modal_asignar_taxonomia(self, tipo):
        selected_item = self.tree_articulos.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Seleccione un artículo de la lista.")
            return

        art_id = int(selected_item[0])
        etiqueta = "Tag" if tipo == "tag" else "Categoría"
        nombre = simpledialog.askstring(f"Nueva {etiqueta}", f"Nombre de la {etiqueta.lower()}:", parent=self)
        if not nombre:
            return

        try:
            if tipo == "tag":
                db.agregar_tag(art_id, nombre.strip())
            else:
                db.agregar_categoria(art_id, nombre.strip())
            messagebox.showinfo("Éxito", f"{etiqueta} asignada correctamente.")
            self.refrescar_taxonomia(art_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo asignar la {etiqueta.lower()}:\n{e}")

    def modal_registrar_usuario(self):
        nombre = simpledialog.askstring("Nuevo Usuario", "Ingrese Nombre:", parent=self)
        if not nombre:
            return
        email = simpledialog.askstring("Nuevo Usuario", "Ingrese Email:", parent=self)
        if not email:
            return

        try:
            new_id = db.guardar_usuario(nombre.strip(), email.strip())
            messagebox.showinfo("Éxito", f"Usuario registrado exitosamente con ID: {new_id}")
            self.cargar_usuarios()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el usuario:\n{e}")

    def eliminar_usuario(self):
        if not self.usuario_activo_id:
            messagebox.showwarning("Atención", "No hay ningún usuario activo seleccionado.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar Eliminacion",
            f"¿Desea Eliminar al usuario '{self.usuario_activo_nombre}'?\n\n(Sus publicaciones deberan ser eliminadas del sistema manualmente).",
            parent=self
        )

        if confirmar:
            try:
                db.eliminar_usuario_logico(self.usuario_activo_id)
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
                self.cargar_usuarios()
                self.cargar_articulos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el usuario:\n{e}")

    def modal_crear_articulo(self):
        if not self.usuario_activo_id:
            messagebox.showwarning("Atención", "Seleccione o registre un usuario primero.")
            return

        win = tk.Toplevel(self)
        win.title("Publicar Nuevo Artículo")
        win.geometry("500x400")

        ttk.Label(win, text="Título:").pack(anchor=tk.W, padx=10, pady=(10,0))
        entry_titulo = ttk.Entry(win, width=60)
        entry_titulo.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(win, text="Contenido:").pack(anchor=tk.W, padx=10, pady=(10,0))
        txt_contenido = tk.Text(win, wrap=tk.WORD, height=12)
        txt_contenido.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        def guardar():
            tit = entry_titulo.get().strip()
            text = txt_contenido.get("1.0", tk.END).strip()
            if not tit or not text:
                messagebox.showwarning("Incompleto", "Ingrese título y contenido.", parent=win)
                return

            try:
                db.crear_articulo(self.usuario_activo_id, tit, text)
                messagebox.showinfo("Éxito", "Artículo publicado correctamente.", parent=win)
                win.destroy()
                self.cargar_articulos()
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar:\n{e}", parent=win)

        ttk.Button(win, text="Publicar", command=guardar).pack(pady=10)

    def eliminar_articulo(self):
        selected_item = self.tree_articulos.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Seleccione un artículo de la lista.")
            return

        art_id = int(selected_item[0])
        confirmar = messagebox.askyesno(
            "Confirmar Eliminacion",
            "¿Desea eliminar esta publicación del sistema público?",
            parent=self
        )

        if confirmar:
            try:
                db.eliminar_articulo_logico(art_id)
                messagebox.showinfo("Éxito", "La publicación ha sido eliminada correctamente.")
                self.lbl_titulo.config(text="Seleccione un artículo para leer")
                self.lbl_meta.config(text="")
                self.lbl_tags.config(text="")
                self.txt_contenido.delete("1.0", tk.END)
                self.txt_comentarios.config(state=tk.NORMAL)
                self.txt_comentarios.delete("1.0", tk.END)
                self.txt_comentarios.config(state=tk.DISABLED)
                self.cargar_articulos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo ocultar el artículo:\n{e}")

    def modal_agregar_comentario(self):
        selected_item = self.tree_articulos.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Seleccione un artículo para comentar.")
            return

        art_id = int(selected_item[0])
        texto_comentario = simpledialog.askstring("Nuevo Comentario", "Escriba su comentario:", parent=self)
        if not texto_comentario:
            return

        try:
            nombre = self.usuario_activo_nombre or "Anónimo"
            db.agregar_comentario(art_id, self.usuario_activo_id, nombre, None, texto_comentario.strip())
            messagebox.showinfo("Éxito", "Comentario agregado.")
            self.cargar_articulos()
            self.cargar_comentarios(art_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el comentario:\n{e}")

    def eliminar_comentario(self):
        selected_item = self.tree_articulos.selection()
        if not selected_item:
            messagebox.showwarning("Atención", "Seleccione un artículo primero para ver sus comentarios.")
            return

        comment_id = simpledialog.askinteger("Eliminar Comentario", "Ingrese el ID del comentario a eliminar:", parent=self)
        if not comment_id:
            return

        try:
            db.eliminar_comentario_logico(comment_id)
            messagebox.showinfo("Éxito", f"Comentario #{comment_id} eliminado.")
            art_id = int(selected_item[0])
            self.cargar_articulos()
            self.cargar_comentarios(art_id)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo eliminar el comentario:\n{e}")

if __name__ == "__main__":
    app = BlogApp()
    app.mainloop()