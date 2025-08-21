# Importar librerías
import pandas as pd
import ttkbootstrap as ttk
import json
import os
import re
import tkinter as tk
import calendar
import shutil  # Para copiar archivos
from ttkbootstrap.constants import PRIMARY, SUCCESS, INFO, SECONDARY, DANGER
from tkinter import messagebox, StringVar, Toplevel, simpledialog
from ttkbootstrap import Style
from datetime import datetime
from tkinter import *
from openpyxl import Workbook, load_workbook
from PIL import Image, ImageTk  # <-- AGREGADO PARA IMAGEN
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas

# Archivos JSON
ARCHIVO_CLIENTES = "Lista_de_clientes.json"
ARCHIVO_PROVEEDORES = "Lista_de_proveedores.json"  # Agregado para evitar errores
ALMACEN_JSON = "almacen.json"

# Verifica si los archivos existen al inicio
def verificar_archivos():
    for archivo in [ARCHIVO_CLIENTES, ALMACEN_JSON, ARCHIVO_PROVEEDORES]:
        if not os.path.exists(archivo):
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)

# Función para cargar datos desde JSON
def cargar_datos(archivo):
    if os.path.exists(archivo):
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                datos = json.load(f)
                return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, IOError):
            messagebox.showwarning("Error", f"El archivo {archivo} está corrupto o vacío.")
            return []
    return []

# Función para guardar datos en JSON
def guardar_datos(archivo, datos):
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except IOError:
        messagebox.showerror("Error", f"No se pudo guardar el archivo {archivo}.")

# Datos iniciales
verificar_archivos()  # Verifica archivos antes de cargar datos
almacen = cargar_datos(ALMACEN_JSON)
clientes = cargar_datos(ARCHIVO_CLIENTES)
proveedores = cargar_datos(ARCHIVO_PROVEEDORES)

# Crear ventana principal con ttkbootstrap
root = Style(theme="superhero").master
root.title("Fome-Ventas")
root.geometry("600x700")

# Cargar imagen al inicio
try:
    ruta_logo = os.path.join("IMAGENES", "logo.jpg")
    imagen_logo = Image.open(ruta_logo)
    imagen_logo = imagen_logo.resize((200, 200), Image.Resampling.LANCZOS)
    imagen_logo_tk = ImageTk.PhotoImage(imagen_logo)
except Exception as e:
    imagen_logo_tk = None
    print("Error al cargar imagen:", e)

# Función para limpiar la pantalla
def limpiar_pantalla():
    for widget in root.winfo_children():
        widget.destroy()

# Función para cerrar la aplicación y guardar todo
def cerrar_aplicacion():
    guardar_datos(ARCHIVO_CLIENTES, clientes)
    guardar_datos(ARCHIVO_PROVEEDORES, proveedores)
    guardar_datos(ALMACEN_JSON, almacen)
    root.destroy()

# --- FUNCIÓN EXPORTAR A EXCEL (UN SOLO ARCHIVO CON VARIAS HOJAS) ---
def exportar_excel():
    try:
        archivo_excel = "fome_ventas.xlsx"
        with pd.ExcelWriter(archivo_excel, engine="openpyxl") as writer:
            # Exportar clientes
            if clientes:
                df_clientes = pd.DataFrame(clientes)
                df_clientes.to_excel(writer, sheet_name="Clientes", index=False)

            # Exportar proveedores
            if proveedores:
                df_proveedores = pd.DataFrame(proveedores)
                df_proveedores.to_excel(writer, sheet_name="Proveedores", index=False)

            # Exportar almacén
            if almacen:
                df_almacen = pd.DataFrame(almacen)
                df_almacen.to_excel(writer, sheet_name="Almacén", index=False)

        messagebox.showinfo("Éxito", f"Datos exportados correctamente en {archivo_excel}.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron exportar los datos: {e}")

# --- MENÚ PRINCIPAL ---
def menu_principal():
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    # Mostrar imagen si se cargó correctamente
    if imagen_logo_tk:
        label_logo = ttk.Label(root, image=imagen_logo_tk)
        label_logo.image = imagen_logo_tk  # ¡Importante para evitar que se borre!
        label_logo.pack(pady=(30, 10))

    ttk.Label(frame, text="¡Bienvenido a Fome-Ventas!", font=("Arial", 16, "bold")).pack(pady=10)

    frame = ttk.Frame(root)
    frame.pack(pady=10)

    ttk.Button(frame, text="Menú Clientes", command=menu_clientes, bootstyle="primary", width=30).pack(pady=5)
    ttk.Button(frame, text="Menú Artículos", command=menu_articulos, bootstyle="success", width=30).pack(pady=5)
    ttk.Button(frame, text="Menú Proveedores", command=menu_proveedores, bootstyle="warning", width=30).pack(pady=5)
    ttk.Button(frame, text="Exportar Datos a Excel", command=exportar_excel, bootstyle="info", width=30).pack(pady=5)
    ttk.Button(frame, text="Salir", command=cerrar_aplicacion, bootstyle="danger", width=30).pack(pady=20)

# --- GESTIÓN DE CLIENTES ---
def menu_clientes():
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)


    ttk.Label(frame, text="Menu Clientes", font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Button(frame, text="Ingresar Nuevo Cliente", command=ingresar_cliente, bootstyle="primary", width=30).pack(pady=5)
    ttk.Button(frame, text="Ver Clientes", command=ver_clientes, bootstyle="info", width=30).pack(pady=5)
    ttk.Button(frame, text="Buscar Cliente", command=buscar_cliente, bootstyle="success", width=30).pack(pady=5)
    ttk.Button(frame, text="Revisar estado de artículos", command=revisar_estado_articulos_cliente).pack(pady=5)
    ttk.Button(frame, text="Regresar al Menú", command=menu_principal, bootstyle="secondary", width=30).pack(pady=5)

def ingresar_cliente():
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Ingresar Nuevo Cliente", font=("Arial", 14, "bold")).pack(pady=10)

    # Entradas de datos del cliente
    ttk.Label(frame, text="Nombre").pack()
    entrada_nombre = ttk.Entry(frame)
    entrada_nombre.pack()

    ttk.Label(frame, text="Dirección").pack()
    entrada_direccion = ttk.Entry(frame)
    entrada_direccion.pack()

    ttk.Label(frame, text="Teléfono").pack()
    entrada_telefono = ttk.Entry(frame)
    entrada_telefono.pack()

    ttk.Label(frame, text="Abono inicial").pack()
    entrada_abono = ttk.Entry(frame)
    entrada_abono.pack()

    # Checkbox para marcar si es artículo por pedir
    es_por_pedir = BooleanVar(value=False)
    ttk.Checkbutton(frame, text="Es artículo por pedir", variable=es_por_pedir, bootstyle="warning").pack(pady=5)

    compras = []  # Inicializar lista de compras

    # --- Función interna para agregar artículo ---
    def agregar_articulo():
        ventana_articulo = Toplevel(root)
        ventana_articulo.title("Agregar Artículo")
        ventana_articulo.geometry("300x250")

        if es_por_pedir.get():
            ttk.Label(ventana_articulo, text="Nombre del artículo").pack()
            entrada_nombre_articulo = ttk.Entry(ventana_articulo)
            entrada_nombre_articulo.pack()

            ttk.Label(ventana_articulo, text="Cantidad").pack()
            entrada_cantidad = ttk.Entry(ventana_articulo)
            entrada_cantidad.pack()

            ttk.Label(ventana_articulo, text="Precio unitario").pack()
            entrada_precio = ttk.Entry(ventana_articulo)
            entrada_precio.pack()

            def guardar_manual():
                nombre = entrada_nombre_articulo.get().strip()
                try:
                    cantidad = int(entrada_cantidad.get())
                    precio = float(entrada_precio.get())
                    if cantidad <= 0 or precio <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("Error", "Cantidad y precio deben ser números mayores que cero.")
                    return

                total = cantidad * precio
                compras.append({
                    "Nombre": nombre,
                    "Cantidad": cantidad,
                    "Total": total,
                    "Por Pedir": True
                })
                ventana_articulo.destroy()

                if messagebox.askyesno("Agregar otro", "¿Agregar otro artículo por pedir?"):
                    agregar_articulo()

            ttk.Button(ventana_articulo, text="Guardar Artículo", command=guardar_manual).pack(pady=5)
            ttk.Button(ventana_articulo, text="Cancelar", command=ventana_articulo.destroy).pack(pady=5)

        else:
            ttk.Label(ventana_articulo, text="Seleccionar artículo").pack()
            seleccion_articulo = StringVar()
            articulo_menu = ttk.Combobox(ventana_articulo, textvariable=seleccion_articulo)
            articulo_menu['values'] = [item['Nombre'] for item in almacen]
            articulo_menu.pack()

            ttk.Label(ventana_articulo, text="Cantidad").pack()
            entrada_cantidad = ttk.Entry(ventana_articulo)
            entrada_cantidad.pack()

            def guardar_articulo():
                nombre_articulo = seleccion_articulo.get()
                try:
                    cantidad = int(entrada_cantidad.get())
                    if cantidad <= 0:
                        raise ValueError
                except ValueError:
                    messagebox.showwarning("Advertencia", "La cantidad debe ser un número mayor que cero.")
                    return

                for item in almacen:
                    if item["Nombre"] == nombre_articulo:
                        if cantidad > item["Stock"]:
                            messagebox.showwarning("Stock insuficiente", f"No hay suficiente stock de {nombre_articulo}.")
                            return
                        # Descontar stock
                        item["Stock"] -= cantidad
                        # Guardar cambios en archivo
                        guardar_datos(ALMACEN_JSON, almacen)

                        precio_total = item["Precio Público"] * cantidad
                        compras.append({
                            "Nombre": nombre_articulo,
                            "Cantidad": cantidad,
                            "Total": precio_total,
                            "Por Pedir": False
                        }) 
                        break

                ventana_articulo.destroy()

                if messagebox.askyesno("Agregar otro artículo", "¿Deseas agregar otro artículo?"):
                    agregar_articulo()

            ttk.Button(ventana_articulo, text="Guardar Artículo", command=guardar_articulo).pack(pady=5)
            ttk.Button(ventana_articulo, text="Cancelar", command=ventana_articulo.destroy).pack(pady=5)

    # --- Guardar cliente ---
    def guardar_cliente():
        nombre = entrada_nombre.get().strip()
        direccion = entrada_direccion.get().strip()
        telefono = entrada_telefono.get().strip()

        if not nombre or not direccion or not telefono:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

        try:
            abono = float(entrada_abono.get() or 0)
        except ValueError:
            messagebox.showwarning("Advertencia", "El abono inicial debe ser un número.")
            return

        total_compras = sum(compra["Total"] for compra in compras)
        deuda = total_compras - abono
        fecha_ingreso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        nuevo_cliente = {
            "id": len(clientes) + 1,
            "Nombre": nombre,
            "Dirección": direccion,
            "Teléfono": telefono,
            "Compras": compras,
            "Total Compras": total_compras,
            "Abono": abono,
            "Deuda": deuda,
            "Fecha Ingreso": fecha_ingreso,
            "Artículos": compras
        }

        clientes.append(nuevo_cliente)
        guardar_datos(ARCHIVO_CLIENTES, clientes)

        if es_por_pedir.get():
            carpeta = "por_pedir"
            os.makedirs(carpeta, exist_ok=True)
            archivo = os.path.join(carpeta, "artículos_por_pedir.xlsx")

            if not os.path.exists(archivo):
                df = pd.DataFrame(columns=["Cliente", "Dirección", "Teléfono", "Artículo", "Cantidad", "Precio Total", "Abono", "Restan"])
            else:
                df = pd.read_excel(archivo)

            for compra in compras:
                df = pd.concat([df, pd.DataFrame([{
                    "Cliente": nombre,
                    "Dirección": direccion,
                    "Teléfono": telefono,
                    "Artículo": compra["Nombre"],
                    "Cantidad": compra["Cantidad"],
                    "Precio Total": compra["Total"],
                    "Abono": abono,
                    "Restan": deuda
                }])], ignore_index=True)

            df.to_excel(archivo, index=False)

        messagebox.showinfo("Éxito", f"Cliente '{nombre}' registrado con ID {nuevo_cliente['id']} y fecha {fecha_ingreso}.")
        menu_clientes()

    ttk.Button(frame, text="Agregar Artículo", command=agregar_articulo).pack(pady=5)
    ttk.Button(frame, text="Guardar Cliente", command=guardar_cliente, bootstyle="success").pack(pady=5)
    ttk.Button(frame, text="Cancelar", command=menu_clientes, bootstyle="danger").pack(pady=5)


def ver_clientes():
    limpiar_pantalla()
    # Frame con canvas + scrollbar
    frame_contenedor = ttk.Frame(root)
    frame_contenedor.pack(fill="both", expand=True, pady=10)

    lienzo = tk.Canvas(frame_contenedor)
    scrollbar = ttk.Scrollbar(frame_contenedor, orient="vertical", command=lienzo.yview)
    frame_resultados = ttk.Frame(lienzo)

    frame_resultados.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))

    lienzo.create_window((0, 0), window=frame_resultados, anchor="nw")
    lienzo.configure(yscrollcommand=scrollbar.set)

    lienzo.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # 🔹 Vincular scroll con la rueda del mouse (Windows/macOS)
    def _on_mousewheel(event):
        try:
            lienzo.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    lienzo.bind_all("<MouseWheel>", _on_mousewheel)

    ttk.Label(frame_resultados, text="Lista de Clientes", font=("Arial", 14, "bold")).pack(pady=10)

    if not clientes:
        ttk.Label(frame_resultados, text="No hay clientes registrados.", font=("Arial", 12)).pack(pady=10)
    else:
        for cliente in clientes:
            ttk.Label(
                frame_resultados,
                text=f"ID: {cliente['id']} - Nombre: {cliente['Nombre']} - Teléfono: {cliente['Teléfono']} - Deuda: ${cliente['Deuda']:.2f}",
                font=("Arial", 10)
            ).pack(pady=2)

            # 🔹 Botón único de eliminar con manita
            ttk.Button(
                frame_resultados,
                text="Eliminar",
                command=lambda c=cliente: eliminar_cliente(c["id"]),
                bootstyle="danger",
                cursor="hand2"
            ).pack(pady=2)

    # Botón para buscar y quitar artículos por pedir
    ttk.Button(frame_resultados, text="Quitar Artículo por Pedir", command=buscar_y_quitar_articulo).pack(pady=10)

    # 🔹 Botón regresar al menú de clientes
    ttk.Button(frame_resultados, text="Regresar al Menú de Clientes", command=menu_clientes, bootstyle="secondary").pack(pady=10)


def eliminar_cliente(id_cliente):
    global clientes
    clientes = [c for c in clientes if c["id"] != id_cliente]

    guardar_datos(ARCHIVO_CLIENTES, clientes)
    messagebox.showinfo("Éxito", f"Cliente con ID {id_cliente} eliminado correctamente.")
    ver_clientes()  # Volver a la lista de clientes después de eliminar


# Función para abrir la ventana de buscar y quitar artículos por pedir
def buscar_y_quitar_articulo():
    cliente_nombre = simpledialog.askstring("Buscar Cliente", "Ingrese el nombre del cliente:")
    if not cliente_nombre:
        return
    cliente_nombre = cliente_nombre.strip().lower()

    cliente = next((c for c in clientes if cliente_nombre in c["Nombre"].lower()), None)
    if not cliente:
        messagebox.showerror("Error", "Cliente no encontrado.")
        return

    articulos_pedir = [art for art in cliente.get("Artículos", []) if art.get("Por Pedir", False)]
    if not articulos_pedir:
        messagebox.showinfo("Información", "El cliente no tiene artículos por pedir.")
        return

    ventana = tk.Toplevel(root)
    ventana.title("Quitar Artículos por Pedir")
    ventana.geometry("750x600")

    lienzo = tk.Canvas(ventana)
    scrollbar = ttk.Scrollbar(ventana, orient="vertical", command=lienzo.yview)
    scroll_frame = ttk.Frame(lienzo)

    scroll_frame.bind(
        "<Configure>",
        lambda e: lienzo.configure(scrollregion=lienzo.bbox("all"))
    )

    lienzo.create_window((0, 0), window=scroll_frame, anchor="nw")
    lienzo.configure(yscrollcommand=scrollbar.set)

    lienzo.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    seleccionados = []

    for articulo in articulos_pedir:
        frame_articulo = ttk.LabelFrame(scroll_frame, text=f"{articulo['Nombre']} (x{articulo['Cantidad']})", padding=10)
        frame_articulo.pack(fill="x", padx=10, pady=5)

        # Mostrar artículos del almacén que coincidan por nombre
        opciones = [a for a in almacen if a["Nombre"].lower() == articulo["Nombre"].lower() and a.get("Stock", 0) > 0]
        if not opciones:
            ttk.Label(frame_articulo, text="No hay stock disponible en el almacén para este artículo.", foreground="red").pack(anchor="w")
            continue

        var = tk.BooleanVar()
        ttk.Checkbutton(frame_articulo, text="Entregar este artículo", variable=var).pack(anchor="w")

        seleccionados.append((articulo, var))

    def guardar_cambios():
        articulos_modificados = []
        for articulo, var in seleccionados:
            if var.get():
                articulo["Por Pedir"] = False
                articulo["FechaEntrega"] = datetime.now().strftime("%Y-%m-%d")
                articulos_modificados.append(articulo)

                # Descontar del stock correctamente usando clave "Stock"
                for stock_articulo in almacen:
                    if stock_articulo.get("Nombre", "").lower() == articulo["Nombre"].lower():
                        stock_actual = stock_articulo.get("Stock", 0)
                        cantidad_solicitada = articulo.get("Cantidad", 0)
                        stock_articulo["Stock"] = max(0, stock_actual - cantidad_solicitada)

                        # Registrar historial
                        if "Historial" not in stock_articulo:
                            stock_articulo["Historial"] = []
                        stock_articulo["Historial"].append({
                            "Cliente": cliente.get("Nombre", ""),
                            "Cantidad": cantidad_solicitada,
                            "Fecha": articulo["FechaEntrega"],
                            "Precio": articulo.get("Precio", 0.0)
                        })
                        break

                # Registrar como compra para exportación
                if "Compras" not in cliente:
                    cliente["Compras"] = []
                cliente["Compras"].append({
                    "Nombre": articulo["Nombre"],
                    "Cantidad": articulo["Cantidad"],
                    "Precio": articulo.get("Precio", 0.0),
                    "Fecha": articulo["FechaEntrega"],
                    "Por Pedir": False
                })

        guardar_datos(ARCHIVO_CLIENTES, clientes)
        guardar_datos(ALMACEN_JSON, almacen)
        exportar_excel()

        messagebox.showinfo("Éxito", "Artículos actualizados, descontados del stock y exportados.")
        ventana.destroy()

    ttk.Button(scroll_frame, text="Guardar", command=guardar_cambios, bootstyle="success").pack(pady=10)
    ttk.Button(scroll_frame, text="Cancelar", command=ventana.destroy, bootstyle="secondary").pack(pady=5)


def revisar_estado_articulos_cliente():
    cliente_nombre = simpledialog.askstring("Revisar Cliente", "Ingrese el nombre del cliente:")
    if not cliente_nombre:
        return
    cliente_nombre = cliente_nombre.strip().lower()

    cliente = next((c for c in clientes if cliente_nombre in c["Nombre"].lower()), None)
    if not cliente:
        messagebox.showerror("Error", "Cliente no encontrado.")
        return

    articulos_pedir = [art for art in cliente.get("Artículos", []) if art.get("Por Pedir", False)]
    articulos_entregados = [art for art in cliente.get("Artículos", []) if not art.get("Por Pedir", False)]

    mensaje = f"Cliente: {cliente['Nombre']}\n\n"

    if articulos_pedir:
        mensaje += "🔴 Artículos por pedir:\n"
        for art in articulos_pedir:
            mensaje += f"• {art['Nombre']} (x{art['Cantidad']})\n"
    else:
        mensaje += "✅ No hay artículos por pedir.\n"

    if articulos_entregados:
        mensaje += "\n🟢 Artículos entregados:\n"
        for art in articulos_entregados:
            fecha = art.get("FechaEntrega", "Sin fecha")
            mensaje += f"• {art['Nombre']} (x{art['Cantidad']}) - Entregado: {fecha}\n"
    else:
        mensaje += "\nℹ️ No hay artículos entregados."

    messagebox.showinfo("Estado de Artículos", mensaje)


def buscar_cliente():
    limpiar_pantalla()

    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Buscar Cliente", font=("Arial", 14, "bold")).pack(pady=10)

    ttk.Label(frame, text="Nombre").pack()
    entrada_busqueda = ttk.Entry(frame)
    entrada_busqueda.pack()

    # Frame con scrollbar para resultados
    frame_contenedor = ttk.Frame(frame)
    frame_contenedor.pack(fill="both", expand=True, pady=10)

    lienzo = tk.Canvas(frame_contenedor)
    scrollbar = ttk.Scrollbar(frame_contenedor, orient="vertical", command=lienzo.yview)
    frame_resultados = ttk.Frame(lienzo)

    frame_resultados.bind(
        "<Configure>",
        lambda e: lienzo.configure(scrollregion=lienzo.bbox("all"))
    )

    lienzo.create_window((0, 0), window=frame_resultados, anchor="nw")
    lienzo.configure(yscrollcommand=scrollbar.set)

    lienzo.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    def realizar_busqueda():
        for widget in frame_resultados.winfo_children():
            widget.destroy()

        nombre_buscar = entrada_busqueda.get().strip().lower()
        resultados = [c for c in clientes if c["Nombre"].lower().startswith(nombre_buscar)]

        if resultados:
            for cliente in resultados:
                info = f"ID: {cliente['id']} - Nombre: {cliente['Nombre']} - Teléfono: {cliente['Teléfono']} - Deuda: ${cliente['Deuda']:.2f}"
                ttk.Label(frame_resultados, text=info, font=("Arial", 10)).pack(pady=2)

                # Entrada para abono
                ttk.Label(frame_resultados, text="Abonar monto:").pack()
                entry_abono = ttk.Entry(frame_resultados)
                entry_abono.pack()

                def abonar(c=cliente, entry=entry_abono):
                    try:
                        monto = float(entry.get())
                        if monto <= 0:
                            raise ValueError
                    except ValueError:
                        messagebox.showwarning("Advertencia", "Ingrese un monto válido.")
                        return

                    # Actualizar los datos del cliente
                    c["Abono"] += monto
                    c["Deuda"] = max(0, c["Deuda"] - monto)
                    guardar_datos(ARCHIVO_CLIENTES, clientes)

                    messagebox.showinfo("Éxito", f"Se abonaron ${monto:.2f} a la cuenta de {c['Nombre']}. Nueva deuda: ${c['Deuda']:.2f}")
                    buscar_cliente()  # Refrescar pantalla

                ttk.Button(frame_resultados, text="Abonar", command=abonar, bootstyle="success").pack(pady=5)
                ttk.Separator(frame_resultados, orient="horizontal").pack(fill="x", pady=5)
        else:
            ttk.Label(frame_resultados, text="No se encontraron clientes con ese nombre.", font=("Arial", 10)).pack(pady=5)

    ttk.Button(frame, text="Buscar", command=realizar_busqueda, bootstyle="success").pack(pady=5)
    ttk.Button(frame, text="Regresar", command=menu_clientes, bootstyle="secondary").pack(pady=5)


def guardar_txt(nombre_cliente, fecha_compra, nota_texto):
    base_nombre = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in nombre_cliente.strip())
    nombre_archivo = f"nota_{base_nombre}_{fecha_compra}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(nota_texto)
    messagebox.showinfo("Guardado", f"Nota guardada como TXT: {nombre_archivo}")


def guardar_pdf(nombre_cliente, fecha_compra, nota_texto):
    # Crear carpeta de salida si no existe
    carpeta = "notas_pdf"
    os.makedirs(carpeta, exist_ok=True)

    # Nombre del archivo
    nombre_archivo = f"nota_{nombre_cliente}_{fecha_compra}.pdf".replace(" ", "_")
    ruta_archivo = os.path.join(carpeta, nombre_archivo)

    # Crear PDF
    c = pdf_canvas.Canvas(ruta_archivo, pagesize=letter)
    width, height = letter
    y = height - 50

    for linea in nota_texto.split("\n"):
        c.drawString(40, y, linea)
        y -= 15
        if y < 50:  # Nueva página si no cabe
            c.showPage()
            y = height - 50

    c.save()
    messagebox.showinfo("Guardado", f"Nota guardada como PDF:\n{ruta_archivo}")


def crear_botones(nota_window, nombre_cliente, fecha_compra, nota_texto):
    frame_botones = ttk.Frame(nota_window)
    frame_botones.pack(pady=10)

    ttk.Button(
        frame_botones,
        text="Guardar como TXT",
        command=lambda: guardar_txt(nombre_cliente, fecha_compra, nota_texto),
        bootstyle="info"
    ).pack(side="left", padx=5)

    ttk.Button(
        frame_botones,
        text="Guardar como PDF",
        command=lambda: guardar_pdf(nombre_cliente, fecha_compra, nota_texto),
        bootstyle="success"
    ).pack(side="left", padx=5)

    ttk.Button(
        frame_botones,
        text="Cerrar",
        command=nota_window.destroy,
        bootstyle="secondary"
    ).pack(side="left", padx=5)


def imprimir_nota(cliente):
    # Crear una nueva ventana
    nota_window = tk.Toplevel(root)
    nota_window.title("Nota de Compra")
    nota_window.geometry("400x600")

    # Cargar logo
    try:
        logo_path = os.path.join("IMAGENES", "logo.jpg")
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((150, 150), Image.Resampling.LANCZOS)
        logo_tk = ImageTk.PhotoImage(logo_img)
        label_logo = ttk.Label(nota_window, image=logo_tk)
        label_logo.image = logo_tk  # mantener referencia
        label_logo.pack(pady=10)
    except Exception:
        pass  # Si no carga, simplemente no mostrar logo

    # Datos del cliente y compra
    nombre_cliente = cliente.get("Nombre", "")
    fecha_compra = datetime.now().strftime("%Y-%m-%d")
    hora_compra = datetime.now().strftime("%H:%M:%S")
    articulos = cliente.get("Artículos", [])
    total_compra = cliente.get("Total Compras", 0.0)
    abono = cliente.get("Abono", 0.0)
    deuda = cliente.get("Deuda", 0.0)

    # Texto de la nota
    nota_texto = f"*** NOTA DE COMPRA ***\n\n"
    nota_texto += f"Cliente: {nombre_cliente}\n"
    nota_texto += f"Fecha: {fecha_compra}   Hora: {hora_compra}\n\n"
    nota_texto += "Artículos:\n"

    for art in articulos:
        nombre_art = art.get("Nombre", "")
        cantidad = art.get("Cantidad", 0)
        total = art.get("Total", 0.0)
        nota_texto += f"- {nombre_art} x{cantidad} = ${total:.2f}\n"

    nota_texto += f"\nTotal: ${total_compra:.2f}\n"
    nota_texto += f"Abono: ${abono:.2f}\n"
    nota_texto += f"Deuda: ${deuda:.2f}\n"
    nota_texto += "\n¡Gracias por su compra!"

    # Mostrar la nota en un widget de texto
    text_widget = tk.Text(nota_window, wrap="word", font=("Arial", 10), padx=10, pady=10)
    text_widget.insert("1.0", nota_texto)
    text_widget.configure(state="disabled")
    text_widget.pack(expand=True, fill="both")

    # Crear los botones (TXT / PDF / Cerrar)
    crear_botones(nota_window, nombre_cliente, fecha_compra, nota_texto)

# --- GESTIÓN DE ARTÍCULOS ---
def menu_articulos():
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Menú Artículos", font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Button(frame, text="Agregar Artículo", command=agregar_articulo, bootstyle=PRIMARY, width=30).pack(pady=5)
    ttk.Button(frame, text="Buscar Artículo", command=buscar_articulo, bootstyle=SUCCESS, width=30).pack(pady=5)
    ttk.Button(frame, text="Ver Artículos", command=ver_articulos, bootstyle=INFO, width=30).pack(pady=5)
    ttk.Button(frame, text="Eliminar Artículo", command=eliminar_articulo, bootstyle=DANGER, width=30).pack(pady=5)
    ttk.Button(frame, text="Regresar al Menú", command=menu_principal, bootstyle=SECONDARY, width=30).pack(pady=5)

def agregar_articulo():
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Agregar Artículo", font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Label(frame, text="Nombre del Artículo").pack()
    nombre_var = StringVar()
    entry_nombre = ttk.Combobox(frame, textvariable=nombre_var, values=[a["Nombre"] for a in almacen], state="normal")
    entry_nombre.pack()

    ttk.Label(frame, text="Precio Público").pack()
    entry_precio = ttk.Entry(frame)
    entry_precio.pack()

    ttk.Label(frame, text="Precio Proveedor").pack()
    entry_precio_proveedor = ttk.Entry(frame)
    entry_precio_proveedor.pack()

    ttk.Label(frame, text="Cantidad").pack()
    entry_cantidad = ttk.Entry(frame)
    entry_cantidad.pack()

    # Función que se ejecuta al seleccionar un artículo existente
    def autocompletar_campos(event):
        nombre = entry_nombre.get().strip()
        articulo_existente = next((a for a in almacen if a["Nombre"].lower() == nombre.lower()), None)
        if articulo_existente:
            entry_precio.delete(0, tk.END)
            entry_precio.insert(0, articulo_existente["Precio Público"])
            entry_precio_proveedor.delete(0, tk.END)
            entry_precio_proveedor.insert(0, articulo_existente["Precio Proveedor"])

    entry_nombre.bind("<<ComboboxSelected>>", autocompletar_campos)

    def guardar_articulo():
        nombre = entry_nombre.get().strip()
        precio_publico = entry_precio.get().strip()
        precio_proveedor = entry_precio_proveedor.get().strip()
        cantidad = entry_cantidad.get().strip()

        # Validación de campos
        if not nombre or not precio_publico or not precio_proveedor:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

        try:
            precio_publico = float(precio_publico)
            precio_proveedor = float(precio_proveedor)
            cantidad = int(cantidad)
        except ValueError:
            messagebox.showwarning("Advertencia", "Ingrese valores numéricos válidos.")
            return

        if precio_publico <= 0 or precio_proveedor <= 0 or cantidad < 0:
            messagebox.showwarning("Advertencia", "Ingrese datos válidos.")
            return
        
        ganancia = precio_publico - precio_proveedor  # Cálculo de ganancia

        # Si ya existe, solo aumentamos el stock
        for articulo in almacen:
            if articulo["Nombre"].lower() == nombre.lower():
                articulo["Stock"] += cantidad
                articulo["Precio Público"] = precio_publico  # Actualiza si el precio cambió
                articulo["Precio Proveedor"] = precio_proveedor
                guardar_datos(ALMACEN_JSON, almacen)
                messagebox.showinfo("Éxito", f"Stock actualizado para '{nombre}'.")
                
                respuesta = messagebox.askyesno("Agregar otro artículo", "¿Deseas agregar otro artículo?")
                if respuesta:
                    agregar_articulo()
                else:
                    menu_articulos()
                return

        # Si no existe, lo agregamos como nuevo
        nuevo_articulo = {
            "ID": len(almacen) + 1,
            "Nombre": nombre,
            "Precio Público": precio_publico,
            "Precio Proveedor": precio_proveedor,
            "Stock": cantidad,
            "Fecha Ingreso": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        almacen.append(nuevo_articulo)
        guardar_datos(ALMACEN_JSON, almacen)
        messagebox.showinfo("Éxito", f"Artículo '{nombre}' guardado correctamente.")
        respuesta = messagebox.askyesno("Agregar otro artículo", "¿Deseas agregar otro artículo?")
        if respuesta:
            agregar_articulo()
        else:
            menu_articulos()
    ttk.Button(frame, text="Guardar", command=guardar_articulo, bootstyle=SUCCESS).pack(pady=5)
    ttk.Button(frame, text="Cancelar", command=menu_articulos, bootstyle=DANGER).pack(pady=5)

def buscar_articulo():
    global articulos_encontrados  # Declarar como global
    articulos_encontrados = []  # Inicializar la variable

    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Buscar Artículo", font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Label(frame, text="Ingrese el Nombre del Artículo").pack()
    entry_nombre = ttk.Entry(frame)
    entry_nombre.pack()

      # Frame para resultados
    frame_resultado = ttk.Frame(frame)
    frame_resultado.pack(pady=10)

     # Crear un Listbox para mostrar los artículos encontrados
    listbox_articulos = tk.Listbox(frame, width=50)
    listbox_articulos.pack(pady=10)


    def realizar_busqueda():
        nombre = entry_nombre.get().strip().lower()
        if not nombre:
           messagebox.showwarning("Advertencia", "Ingrese un nombre válido.")
           return
    
    # Limpiar el Listbox antes de la búsqueda
        listbox_articulos.delete(0, tk.END)

        global articulos_encontrados
        articulos_encontrados = [a for a in almacen if nombre in a["Nombre"].lower()]

        if not articulos_encontrados:
           messagebox.showinfo("Resultado", "Artículo no encontrado.")
           return
    
    # Llenar el Listbox con los artículos encontrados
        for articulo in articulos_encontrados:
            listbox_articulos.insert(tk.END, articulo['Nombre'])


    def ver_detalle():
        seleccion = listbox_articulos.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para ver los detalles.")
            return

        # Obtener el nombre del artículo seleccionado
        nombre_seleccionado = listbox_articulos.get(seleccion[0])
        articulo_detalle = next((a for a in almacen if a["Nombre"] == nombre_seleccionado), None)

        if articulo_detalle:
            # Mostrar detalles del artículo
            detalle = f"Nombre: {articulo_detalle['Nombre']}\n" \
                      f"Precio Público: ${articulo_detalle['Precio Público']:.2f}\n" \
                      f"Precio Proveedor: ${articulo_detalle['Precio Proveedor']:.2f}\n" \
                      f"Stock: {articulo_detalle['Stock']}\n" \
                      f"Fecha Ingreso: {articulo_detalle['Fecha Ingreso']}"
            messagebox.showinfo("Detalles del Artículo", detalle)

    ttk.Button(frame, text="Buscar", command=realizar_busqueda, bootstyle=SUCCESS).pack(pady=5)
    ttk.Button(frame, text="Ver Detalle", command=ver_detalle, bootstyle=INFO).pack(pady=5)
    ttk.Button(frame, text="Regresar", command=menu_articulos, bootstyle=SECONDARY).pack(pady=5)

    if articulos_encontrados:
        ttk.Label(root, text="Resultados de la Búsqueda", font=("Arial", 14, "bold")).pack(pady=10)
        for articulo in articulos_encontrados:
            info = f"{articulo['Nombre']} - Precio Público: ${articulo['Precio Público']:.2f} - Precio Proveedor: ${articulo['Precio Proveedor']:.2f}"
            ttk.Label(root, text=info, font=("Arial", 12)).pack(pady=5)
            
# Función para ver artículos y poder editar
def ver_articulos():
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Lista de Artículos", font=("Arial", 14, "bold")).pack(pady=10)

    if not almacen:
        ttk.Label(frame, text="No hay artículos en el almacén.", font=("Arial", 12)).pack(pady=10)
    else:
         # Crear un Treeview para mejor visualización y selección
        tree = ttk.Treeview(frame, columns=("Nombre", "Stock", "Precio Público", "Precio Proveedor"), show='headings', selectmode='browse')
        tree.heading("Nombre", text="Nombre")
        tree.heading("Stock", text="Cantidad en Stock")
        tree.heading("Precio Público", text="Precio Público")
        tree.heading("Precio Proveedor", text="Precio Proveedor")
        tree.pack(pady=10)

        for articulo in almacen:
            nombre = articulo.get('Nombre', 'SIN NOMBRE')
            cantidad = articulo.get('Stock', 0)
            precio_publico = articulo.get('Precio Público', 0.0)
            precio_proveedor = articulo.get('Precio Proveedor', 0.0)

            tree.insert('', tk.END, values=(
                nombre,
                cantidad,
                f"${precio_publico:.2f}",
                f"${precio_proveedor:.2f}"
            ))


        def seleccionar_articulo():
            selected_item = tree.focus()
            if not selected_item:
                messagebox.showwarning("Advertencia", "Seleccione un artículo para editar.")
                return
            valores = tree.item(selected_item, 'values')
            nombre = valores[0]
            
            # Buscar el artículo en almacen
            for articulo in almacen:
                if articulo['Nombre'] == nombre:
                    abrir_formulario_edicion(articulo)
                    break

        ttk.Button(frame, text="Editar Artículo", command=seleccionar_articulo, bootstyle=PRIMARY).pack(pady=5)

    ttk.Button(frame, text="Regresar", command=menu_articulos, bootstyle=SECONDARY).pack(pady=10)

def abrir_formulario_edicion(articulo):
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Editar Artículo", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

     # Variables para los campos
    nombre_var = tk.StringVar(value=articulo['Nombre'])
    stock = tk.StringVar(value=str(articulo['Stock']))
    precio_publico_var = tk.StringVar(value=str(articulo['Precio Público']))
    precio_proveedor_var = tk.StringVar(value=str(articulo['Precio Proveedor']))

      # Función para guardar cambios
    def guardar_cambios():
        # Obtener los valores ingresados
        nuevo_nombre = nombre_var.get().strip()
        nuevo_stock = stock.get().strip()
        nuevo_precio_publico = precio_publico_var.get().strip()
        nuevo_precio_proveedor = precio_proveedor_var.get().strip()

        # Validar y convertir stock
        try:
             nuevo_stock = int(nuevo_stock) if nuevo_stock else articulo.get('Stock', 0)
        except ValueError:
            messagebox.showerror("Error", "Cantidad en stock debe ser un número entero.")
            return

        try:
            nuevo_precio_publico = float(nuevo_precio_publico) if nuevo_precio_publico else articulo.get('Precio Público', 0.0)
        except ValueError:
            messagebox.showerror("Error", "Precio Público debe ser un número válido.")
            return
        
        # Validar precios
        try:
            nuevo_precio_proveedor = float(nuevo_precio_proveedor) if nuevo_precio_proveedor else articulo.get('Precio Proveedor', 0.0)
        except ValueError:
            messagebox.showerror("Error", "Precio Proveedor debe ser un número válido.")
            return
        
           # Guardar los datos actualizados
        articulo['Nombre'] = nuevo_nombre if nuevo_nombre else articulo.get('Nombre', '')
        articulo['Stock'] = nuevo_stock
        articulo['Precio Público'] = nuevo_precio_publico
        articulo['Precio Proveedor'] = nuevo_precio_proveedor

        # Guardar cambios
        guardar_datos(ALMACEN_JSON, almacen)
        messagebox.showinfo("Éxito", "Artículo actualizado correctamente.")
        ver_articulos()

    # Campos de entrada
    ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
    ttk.Entry(frame, textvariable=nombre_var).grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Cantidad en Stock:").grid(row=2, column=0, sticky='e', padx=5, pady=5)
    ttk.Entry(frame, textvariable=stock).grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Precio Público:").grid(row=3, column=0, sticky='e', padx=5, pady=5)
    ttk.Entry(frame, textvariable=precio_publico_var).grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Precio Proveedor:").grid(row=4, column=0, sticky='e', padx=5, pady=5)
    ttk.Entry(frame, textvariable=precio_proveedor_var).grid(row=4, column=1, padx=5, pady=5)

    ttk.Button(frame, text="Guardar", command=guardar_cambios, bootstyle=SUCCESS).grid(row=5, column=0, padx=5, pady=10)
    ttk.Button(frame, text="Cancelar", command=ver_articulos, bootstyle=SECONDARY).grid(row=5, column=1, padx=5, pady=10)

def eliminar_articulo():
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Eliminar Artículo", font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Label(frame, text="Ingrese el Nombre del Artículo a eliminar").pack()
    entry_nombre = ttk.Entry(frame)
    entry_nombre.pack()

    # Crear un Listbox para mostrar los artículos
    listbox_articulos = tk.Listbox(frame, width=50)
    listbox_articulos.pack(pady=10)

    # Llenar el Listbox con los artículos del almacén
    for articulo in almacen:
        listbox_articulos.insert(tk.END, articulo['Nombre'])

    def eliminar():
        global almacen
        # Obtener el índice del artículo seleccionado
        seleccion = listbox_articulos.curselection()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para eliminar.")
            return

        # Obtener el nombre del artículo seleccionado
        nombre = listbox_articulos.get(seleccion[0]).strip().lower()

        # Filtrar el almacen para eliminar el artículo seleccionado
        almacen_filtrado = [a for a in almacen if a["Nombre"].lower() != nombre]

        if len(almacen) == len(almacen_filtrado):
            messagebox.showinfo("Resultado", "Artículo no encontrado.")
        else:
          almacen = almacen_filtrado

        guardar_datos(ALMACEN_JSON, almacen)
        messagebox.showinfo("Éxito", f"Artículo '{nombre}' eliminado correctamente.")
        
        # Actualizar el Listbox
        listbox_articulos.delete(seleccion)

    ttk.Button(frame, text="Eliminar", command=eliminar, bootstyle=DANGER).pack(pady=5)
    ttk.Button(frame, text="Cancelar", command=menu_articulos, bootstyle=SECONDARY).pack(pady=5)



# --- GESTIÓN DE PROVEEDORES ---
def menu_proveedores():
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Menú Proveedores", font=("Arial", 14, "bold")).pack(pady=10)

    ttk.Button(frame, text="Ingresar Nuevo Proveedor", command=ingresar_proveedor, bootstyle="primary", width=30).pack(pady=5)
    ttk.Button(frame, text="Ver Proveedores", command=ver_proveedores, bootstyle="info", width=30).pack(pady=5)
    ttk.Button(frame, text="Buscar Proveedor", command=buscar_proveedor, bootstyle="success", width=30).pack(pady=5)
    ttk.Button(frame, text="Eliminar Proveedor", command=eliminar_proveedor, bootstyle="danger", width=30).pack(pady=5)
    ttk.Button(frame, text="Regresar al Menú", command=menu_principal, bootstyle="secondary", width=30).pack(pady=5)


def ingresar_proveedor():
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Ingresar Nuevo Proveedor", font=("Arial", 14, "bold")).pack(pady=10)

    ttk.Label(frame, text="Nombre").pack()
    entrada_nombre = ttk.Entry(frame)
    entrada_nombre.pack()

    ttk.Label(frame, text="Teléfono").pack()
    entrada_telefono = ttk.Entry(frame)
    entrada_telefono.pack()

    articulos = []

    def agregar_articulo_proveedor():
        ventana = Toplevel(root)
        ventana.title("Agregar Artículo del Proveedor")
        ventana.geometry("300x300")

        ttk.Label(ventana, text="Nombre del artículo").pack()
        entrada_nombre_art = ttk.Entry(ventana)
        entrada_nombre_art.pack()

        ttk.Label(ventana, text="Precio Proveedor").pack()
        entrada_precio_proveedor = ttk.Entry(ventana)
        entrada_precio_proveedor.pack()

        ttk.Label(ventana, text="Precio Público").pack()
        entrada_precio_publico = ttk.Entry(ventana)
        entrada_precio_publico.pack()

        ttk.Label(ventana, text="Cantidad").pack()
        entrada_cantidad = ttk.Entry(ventana)
        entrada_cantidad.pack()

        def guardar_art():
            try:
                nombre = entrada_nombre_art.get().strip()
                precio_prov = float(entrada_precio_proveedor.get())
                precio_pub = float(entrada_precio_publico.get())
                cantidad = int(entrada_cantidad.get())
            except ValueError:
                messagebox.showwarning("Error", "Datos inválidos en el artículo")
                return

            articulo = {
                "Nombre": nombre,
                "Precio Proveedor": precio_prov,
                "Precio Público": precio_pub,
                "Cantidad": cantidad
            }
            articulos.append(articulo)

            # Agregar al almacén
            existente = next((a for a in almacen if a["Nombre"].lower() == nombre.lower()), None)
            if existente:
                existente["Stock"] += cantidad
                existente["Precio Público"] = precio_pub
                existente["Precio Proveedor"] = precio_prov
            else:
                almacen.append({
                    "ID": len(almacen) + 1,
                    "Nombre": nombre,
                    "Precio Público": precio_pub,
                    "Precio Proveedor": precio_prov,
                    "Stock": cantidad,
                    "Fecha Ingreso": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            guardar_datos(ALMACEN_JSON, almacen)

            ventana.destroy()
            if messagebox.askyesno("Agregar otro", "¿Desea agregar otro artículo?"):
                agregar_articulo_proveedor()

        ttk.Button(ventana, text="Guardar Artículo", command=guardar_art).pack(pady=5)

    def guardar_proveedor():
        nombre = entrada_nombre.get().strip()
        telefono = entrada_telefono.get().strip()

        if not nombre or not telefono:
            messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
            return

        nuevo_proveedor = {
            "id": len(proveedores) + 1,
            "Nombre": nombre,
            "Teléfono": telefono,
            "Artículos": articulos
        }
        proveedores.append(nuevo_proveedor)
        guardar_datos(ARCHIVO_PROVEEDORES, proveedores)
        messagebox.showinfo("Éxito", f"Proveedor '{nombre}' registrado con {len(articulos)} artículos.")
        menu_proveedores()

    ttk.Button(frame, text="Agregar Artículo", command=agregar_articulo_proveedor).pack(pady=5)
    ttk.Button(frame, text="Guardar Proveedor", command=guardar_proveedor, bootstyle="success").pack(pady=5)
    ttk.Button(frame, text="Cancelar", command=menu_proveedores, bootstyle="danger").pack(pady=5)


def ver_proveedores():
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Lista de Proveedores", font=("Arial", 14, "bold")).pack(pady=10)

    if not proveedores:
        ttk.Label(frame, text="No hay proveedores registrados.", font=("Arial", 12)).pack(pady=10)
    else:
        for prov in proveedores:
            ttk.Label(frame, text=f"ID: {prov['id']} - {prov['Nombre']} - Tel: {prov['Teléfono']}", font=("Arial", 10)).pack(pady=2)

    ttk.Button(frame, text="Regresar", command=menu_proveedores, bootstyle="secondary").pack(pady=10)


def buscar_proveedor():
    nombre = simpledialog.askstring("Buscar Proveedor", "Ingrese el nombre del proveedor:")
    if not nombre:
        return
    nombre = nombre.strip().lower()

    proveedor = next((p for p in proveedores if nombre in p["Nombre"].lower()), None)
    if not proveedor:
        messagebox.showerror("Error", "Proveedor no encontrado.")
        return

    articulos = "\n".join([f"- {a['Nombre']} x{a['Cantidad']} (Pub: ${a['Precio Público']}, Prov: ${a['Precio Proveedor']})" for a in proveedor["Artículos"]])
    messagebox.showinfo("Proveedor Encontrado", f"Nombre: {proveedor['Nombre']}\nTel: {proveedor['Teléfono']}\n\nArtículos:\n{articulos}")


def eliminar_proveedor():
    nombre = simpledialog.askstring("Eliminar Proveedor", "Ingrese el nombre del proveedor:")
    if not nombre:
        return
    nombre = nombre.strip().lower()

    global proveedores
    proveedores_filtrados = [p for p in proveedores if p["Nombre"].lower() != nombre]
    if len(proveedores) == len(proveedores_filtrados):
        messagebox.showinfo("Resultado", "Proveedor no encontrado.")
    else:
        proveedores = proveedores_filtrados
        guardar_datos(ARCHIVO_PROVEEDORES, proveedores)
        messagebox.showinfo("Éxito", f"Proveedor '{nombre}' eliminado correctamente.")
    ver_proveedores()

# DATOS DE EXCEL
def exportar_excel():
    try:
        if not almacen:
            messagebox.showinfo("Información", "No hay artículos en el almacén.")
            return

        hoy = datetime.now().strftime("%Y-%m-%d")  # Fecha actual

        # ---- Exportar CLIENTES separados por artículos por pedir y en stock ----
        lista_clientes = []
        for cliente in clientes:
            articulos_pedir = []
            articulos_stock = []

            for articulo in cliente.get("Artículos", []):
                if articulo.get("Por Pedir", False):
                    articulos_pedir.append(f"{articulo['Nombre']} (x{articulo['Cantidad']})")
                else:
                    articulos_stock.append(f"{articulo['Nombre']} (x{articulo['Cantidad']})")

            lista_clientes.append({
                "Nombre": cliente.get("Nombre", ""),
                "Teléfono": cliente.get("Teléfono", ""),
                "Dirección": cliente.get("Dirección", ""),
                "Artículos por pedir": ", ".join(articulos_pedir),
                "Artículos en stock": ", ".join(articulos_stock),
                "Abono": cliente.get("Abono", 0),
                "Deuda": cliente.get("Deuda", 0),
                "Fecha de Ingreso": hoy
            })

        df_clientes = pd.DataFrame(lista_clientes)
        archivo_excel = "clientes.xlsx"

        # ---- Exportar HISTORIAL de artículos comprados desde el ALMACÉN ----
        historial_general = []
        for articulo in almacen:
            historial = articulo.get("Historial", [])
            for registro in historial:
                historial_general.append({
                    "Artículo": articulo["Nombre"],
                    "Cantidad": registro["Cantidad"],
                    "Precio": registro["Precio"],
                    "Cliente": registro["Cliente"],
                    "Fecha": registro["Fecha"]
                })

        with pd.ExcelWriter(archivo_excel, engine="openpyxl") as writer:
            # Hoja de Clientes
            df_clientes.to_excel(writer, sheet_name="Clientes", index=False)

            # Hoja de Historial de Ventas
            if historial_general:
                df_historial = pd.DataFrame(historial_general)
                df_historial.sort_values(by="Fecha", inplace=True)
                df_historial["Subtotal"] = df_historial["Cantidad"] * df_historial["Precio"]
                total = df_historial["Subtotal"].sum()
                total_row = pd.DataFrame([{
                    "Artículo": "TOTAL",
                    "Cantidad": "",
                    "Precio": "",
                    "Cliente": "",
                    "Fecha": "",
                    "Subtotal": total
                }])
                df_historial = pd.concat([df_historial, total_row], ignore_index=True)
                df_historial.to_excel(writer, sheet_name="Historial Ventas", index=False)

            # Hoja de Resumen por fecha
            resumen = {}
            for cliente in clientes:
                for compra in cliente.get("Compras", []):
                    if not compra.get("Por Pedir", False):
                        try:
                            fecha = pd.to_datetime(compra["Fecha"])
                        except Exception:
                            continue
                        nombre = compra["Nombre"]
                        key = (nombre, fecha.date(), fecha.month, fecha.year)
                        resumen[key] = resumen.get(key, 0) + compra["Cantidad"]

            data_resumen = []
            for (nombre, dia, mes, anio), cantidad in resumen.items():
                data_resumen.append({
                    "Nombre del Artículo": nombre,
                    "Día": dia,
                    "Mes": mes,
                    "Año": anio,
                    "Cantidad Vendida": cantidad
                })

            if data_resumen:
                df_resumen = pd.DataFrame(data_resumen)
                df_resumen.to_excel(writer, sheet_name="Resumen Ventas", index=False)

        # ---- Generar corte mensual ----
        hoy_dt = datetime.now()
        mes = calendar.month_name[hoy_dt.month].lower()
        anio = str(hoy_dt.year)
        carpeta_corte = os.path.join("cortes", anio, mes)
        os.makedirs(carpeta_corte, exist_ok=True)

        nombre_archivo_corte = f"clientes_corte_{mes}_{anio}.xlsx"
        ruta_corte_clientes = os.path.join(carpeta_corte, nombre_archivo_corte)

        df_corte = df_clientes.copy()
        total_abonos = df_corte['Abono'].sum()
        total_deudas = df_corte['Deuda'].sum()

        fila_totales = {
            "Nombre": "TOTALES",
            "Teléfono": "",
            "Dirección": "",
            "Artículos por pedir": "",
            "Artículos en stock": "",
            "Abono": total_abonos,
            "Deuda": total_deudas,
            "Fecha de Ingreso": ""
        }

        df_corte = pd.concat([df_corte, pd.DataFrame([fila_totales])], ignore_index=True)
        df_corte.to_excel(ruta_corte_clientes, index=False)

        # ---- Exportar artículos del almacén y por pedir ----
        articulos_normales = []
        articulos_por_pedir = []

        for articulo in almacen:
            ganancia = (articulo['Precio Público'] - articulo['Precio Proveedor']) * articulo['Stock']
            articulo['Ganancia'] = ganancia

            if articulo.get('Por Pedir', False):
                articulo['Fecha de Pedido'] = hoy  # Agregar fecha al artículo por pedir
                articulos_por_pedir.append(articulo)
            else:
                articulos_normales.append(articulo)

        if articulos_normales:
            df_almacen = pd.DataFrame(articulos_normales)
            total_stock = df_almacen['Stock'].sum()
            total_ganancia = df_almacen['Ganancia'].sum()
            fila_total = {'Nombre': 'TOTAL', 'Stock': total_stock, 'Ganancia': total_ganancia}
            df_almacen = pd.concat([df_almacen, pd.DataFrame([fila_total])], ignore_index=True)
            df_almacen.to_excel("almacen.xlsx", index=False)

        if articulos_por_pedir:
            df_pedir = pd.DataFrame(articulos_por_pedir)
            total_stock_pedir = df_pedir['Stock'].sum()
            total_ganancia_pedir = df_pedir['Ganancia'].sum()
            fila_total_pedir = {'Nombre': 'TOTAL', 'Stock': total_stock_pedir, 'Ganancia': total_ganancia_pedir, 'Fecha de Pedido': ""}
            df_pedir = pd.concat([df_pedir, pd.DataFrame([fila_total_pedir])], ignore_index=True)
            df_pedir.to_excel("articulos_por_pedir.xlsx", index=False)

        # ---- Copiar archivos al corte mensual ----
        shutil.copy("clientes.xlsx", os.path.join(carpeta_corte, "clientes.xlsx"))
        if os.path.exists("almacen.xlsx"):
            shutil.copy("almacen.xlsx", os.path.join(carpeta_corte, "almacen.xlsx"))
        if os.path.exists("articulos_por_pedir.xlsx"):
            shutil.copy("articulos_por_pedir.xlsx", os.path.join(carpeta_corte, "articulos_por_pedir.xlsx"))

        messagebox.showinfo("Éxito", "Datos exportados y corte mensual generado correctamente.")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar a Excel: {str(e)}")

# Iniciar la aplicación mostrando el menú principal
menu_principal()

# Iniciar el bucle principal de la aplicación
root.mainloop()

