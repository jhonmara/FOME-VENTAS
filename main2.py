# Importar librerías
import pandas as pd
import ttkbootstrap as ttk
import json
import ttkbootstrap as tb
import os
import re
import tkinter as tk
import calendar
import shutil  # Para copiar archivos
import reportlab
import cryptography
import hashlib
import functools

# --- Rutas de los logos ---
logo_fome_path = os.path.join(os.getcwd(), "IMAGENES", "logo.jpg")
logo_mara_path = os.path.join(os.getcwd(), "IMAGENES", "logo_presi.png")

# --- FIX para error con md5 y reportlab ---
# Esto asegura compatibilidad con versiones recientes de Python
_md5_old = hashlib.md5

def _md5_fixed(*args, **kwargs):
    kwargs.pop("usedforsecurity", None)
    return _md5_old(*args, **kwargs)

hashlib.md5 = _md5_fixed

from ttkbootstrap.constants import PRIMARY, SUCCESS, INFO, SECONDARY, DANGER
from tkinter import messagebox, StringVar, Toplevel, simpledialog, BooleanVar, Text
from ttkbootstrap import Style
from datetime import datetime
from tkinter import *
from openpyxl import Workbook, load_workbook
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas as pdf_canvas

# Archivos JSON
ARCHIVO_CLIENTES = "Lista_de_clientes.json"
ARCHIVO_PROVEEDORES = "Lista_de_proveedores.json"
ALMACEN_JSON = "almacen.json"
VENTAS_JSON = "Ventas_completadas.json"

# --- Inicialización de referencias globales ---
entrada_nombre = None
entrada_direccion = None
entrada_telefono = None
entrada_abono = None
es_por_pedir = None
compras = []
entrada_nombre_proveedor = None
entrada_telefono_proveedor = None
articulos_proveedor = []

# Verifica si los archivos existen al inicio y crea si no
def verificar_archivos():
    """Verifica la existencia de los archivos JSON y los crea si no existen."""
    for archivo in [ARCHIVO_CLIENTES, ALMACEN_JSON, ARCHIVO_PROVEEDORES, VENTAS_JSON]:
        if not os.path.exists(archivo):
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4)
    # Crear carpeta de notas si no existe
    os.makedirs(os.path.join(os.getcwd(), "notas_clientes"), exist_ok=True)
    os.makedirs(os.path.join(os.getcwd(), "IMAGENES"), exist_ok=True)


# Función para cargar datos desde JSON
def cargar_datos(archivo):
    """Carga datos desde un archivo JSON, maneja errores si el archivo está vacío o corrupto."""
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
    """Guarda datos en un archivo JSON con formato legible."""
    try:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
    except IOError:
        messagebox.showerror("Error", f"No se pudo guardar el archivo {archivo}.")

# Datos iniciales
verificar_archivos()
almacen = cargar_datos(ALMACEN_JSON)
clientes = cargar_datos(ARCHIVO_CLIENTES)
proveedores = cargar_datos(ARCHIVO_PROVEEDORES)
ventas = cargar_datos(VENTAS_JSON)

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
    """Destruye todos los widgets en la ventana principal."""
    for widget in root.winfo_children():
        widget.destroy()

# Función para cerrar la aplicación y guardar todo
def cerrar_aplicacion():
    """Guarda todos los datos y cierra la aplicación."""
    guardar_datos(ARCHIVO_CLIENTES, clientes)
    guardar_datos(ARCHIVO_PROVEEDORES, proveedores)
    guardar_datos(ALMACEN_JSON, almacen)
    root.destroy()

# --- FUNCIÓN EXPORTAR A EXCEL (UN SOLO ARCHIVO CON VARIAS HOJAS) ---
def exportar_excel_basico():
    """
    Exporta los datos de clientes, proveedores, almacén y ventas a un solo
    archivo Excel con varias hojas.
    """
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
            
            # Exportar ventas
            if ventas:
                df_ventas = pd.DataFrame(ventas)
                df_ventas.to_excel(writer, sheet_name="Ventas", index=False)


        messagebox.showinfo("Éxito", f"Datos exportados correctamente en {archivo_excel}.")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron exportar los datos: {e}")


# --- MENÚ PRINCIPAL ---
def menu_principal():
    """Muestra la pantalla del menú principal."""
    limpiar_pantalla()
    
    # Marco principal
    frame_menu = ttk.Frame(root)
    frame_menu.pack(pady=20, expand=True)

    # Mostrar imagen si se cargó correctamente
    if imagen_logo_tk:
        label_logo = ttk.Label(frame_menu, image=imagen_logo_tk)
        label_logo.image = imagen_logo_tk
        label_logo.pack(pady=(30, 10))

    ttk.Label(frame_menu, text="¡Bienvenido a Fome-Ventas!", font=("Arial", 16, "bold")).pack(pady=10)

    frame_botones = ttk.Frame(frame_menu)
    frame_botones.pack(pady=10)

    ttk.Button(frame_botones, text="Menú Clientes", command=menu_clientes, bootstyle="primary", width=30).pack(pady=5)
    ttk.Button(frame_botones, text="Menú Artículos", command=menu_articulos, bootstyle="success", width=30).pack(pady=5)
    ttk.Button(frame_botones, text="Menú Proveedores", command=menu_proveedores, bootstyle="warning", width=30).pack(pady=5)
    ttk.Button(frame_botones, text="Exportar Datos a Excel", command=exportar_excel, bootstyle="info", width=30).pack(pady=5)
    ttk.Button(frame_botones, text="Salir", command=cerrar_aplicacion, bootstyle="danger", width=30).pack(pady=20)

# --- GESTIÓN DE CLIENTES ---
def menu_clientes():
    """Muestra la pantalla del menú de clientes."""
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
    """Muestra el formulario para ingresar un nuevo cliente."""
    global entrada_nombre, entrada_direccion, entrada_telefono, entrada_abono, es_por_pedir, compras
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    compras = []  # Inicializar lista de compras

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

    def agregar_articulo():
        """
        Muestra una ventana para elegir si el artículo es por pedir o de almacén
        y luego abre la ventana correspondiente.
        """
        def abrir_manual():
            """Abre la ventana para agregar un artículo por pedir manualmente."""
            # Asegúrate de destruir la ventana de selección antes de abrir la nueva
            ventana_seleccionar_tipo.destroy()
            ventana_articulo = Toplevel(root)
            ventana_articulo.title("Agregar Artículo por Pedir")
            ventana_articulo.geometry("300x250")

            def guardar_manual():
                """Guarda el artículo por pedir y pregunta si desea agregar otro."""
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
                    "Por Pedir": True,
                    "Precio Unitario": precio
                })

                # Preguntar si quiere agregar otro artículo, volviendo al menú de selección
                if messagebox.askyesno("Agregar otro artículo", "¿Desea agregar otro artículo?"):
                    ventana_articulo.destroy()
                    agregar_articulo()
                else:
                    ventana_articulo.destroy()

            ttk.Label(ventana_articulo, text="Nombre del artículo").pack()
            entrada_nombre_articulo = ttk.Entry(ventana_articulo)
            entrada_nombre_articulo.pack()

            ttk.Label(ventana_articulo, text="Cantidad").pack()
            entrada_cantidad = ttk.Entry(ventana_articulo)
            entrada_cantidad.pack()

            ttk.Label(ventana_articulo, text="Precio unitario").pack()
            entrada_precio = ttk.Entry(ventana_articulo)
            entrada_precio.pack()

            ttk.Button(ventana_articulo, text="Guardar Artículo", command=guardar_manual).pack(pady=5)
            ttk.Button(ventana_articulo, text="Cancelar", command=ventana_articulo.destroy).pack(pady=5)

        def abrir_almacen():
            """Abre la ventana para agregar un artículo desde el almacén."""
            # Asegúrate de destruir la ventana de selección antes de abrir la nueva
            ventana_seleccionar_tipo.destroy()
            ventana_articulo = Toplevel(root)
            ventana_articulo.title("Agregar Artículo de Almacén")
            ventana_articulo.geometry("300x250")

            def guardar_articulo():
                """Guarda el artículo del almacén y pregunta si desea agregar otro."""
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
                        precio_total = item["Precio Público"] * cantidad
                        compras.append({
                            "Nombre": nombre_articulo,
                            "Cantidad": cantidad,
                            "Total": precio_total,
                            "Por Pedir": False,
                            "Precio Unitario": item["Precio Público"]
                        })
                        break

                # Preguntar si quiere agregar otro artículo, volviendo al menú de selección
                if messagebox.askyesno("Agregar otro artículo", "¿Desea agregar otro artículo?"):
                    ventana_articulo.destroy()
                    agregar_articulo()
                else:
                    ventana_articulo.destroy()
            
            ttk.Label(ventana_articulo, text="Seleccionar artículo").pack()
            seleccion_articulo = ttk.Combobox(ventana_articulo, values=[item['Nombre'] for item in almacen])
            seleccion_articulo.pack()

            ttk.Label(ventana_articulo, text="Cantidad").pack()
            entrada_cantidad = ttk.Entry(ventana_articulo)
            entrada_cantidad.pack()

            ttk.Button(ventana_articulo, text="Guardar Artículo", command=guardar_articulo).pack(pady=5)
            ttk.Button(ventana_articulo, text="Cancelar", command=ventana_articulo.destroy).pack(pady=5)

        # Ventana de selección
        ventana_seleccionar_tipo = Toplevel(root)
        ventana_seleccionar_tipo.title("Seleccionar Tipo de Artículo")
        ventana_seleccionar_tipo.geometry("300x150")

        ttk.Label(ventana_seleccionar_tipo, text="¿Qué tipo de artículo desea agregar?").pack(pady=10)
        ttk.Button(ventana_seleccionar_tipo, text="Artículo Por Pedir", command=abrir_manual, bootstyle="info").pack(pady=5)
        ttk.Button(ventana_seleccionar_tipo, text="Artículo de Almacén", command=abrir_almacen, bootstyle="success").pack(pady=5)
        ttk.Button(ventana_seleccionar_tipo, text="Cancelar", command=ventana_seleccionar_tipo.destroy, bootstyle="danger").pack(pady=5)

    ttk.Button(frame, text="Agregar Artículo", command=agregar_articulo).pack(pady=5)
    ttk.Button(frame, text="Guardar Cliente", command=guardar_cliente, bootstyle="success").pack(pady=5)
    ttk.Button(frame, text="Cancelar", command=menu_clientes, bootstyle="danger").pack(pady=5)
# --- Guardar cliente ---
def guardar_cliente():
    """
    Guarda los datos del nuevo cliente, y llama a la función para
    gestionar el pago antes de generar la nota.
    """
    global clientes, compras, entrada_abono

    nombre = entrada_nombre.get().strip()
    direccion = entrada_direccion.get().strip()
    telefono = entrada_telefono.get().strip()

    if not nombre or not direccion or not telefono:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        return

    try:
        abono_inicial = float(entrada_abono.get() or 0)
    except ValueError:
        messagebox.showwarning("Advertencia", "El abono inicial debe ser un número.")
        return

    total_compras = sum(compra.get("Total", 0) for compra in compras)
    
    # Creamos un diccionario temporal para la nota
    cliente_temporal = {
        "Nombre": nombre,
        "Dirección": direccion,
        "Teléfono": telefono,
        "Compras": compras,
        "Total Compras": total_compras,
        "Abono": abono_inicial,
        "Deuda": total_compras - abono_inicial,
        "Artículos": compras
    }

    # Llamamos a la nueva ventana para gestionar el pago antes de guardar
    mostrar_ventana_pago(cliente_temporal)

def mostrar_ventana_pago(cliente):
    """
    Muestra una ventana para ingresar la cantidad recibida y calcular el cambio.
    """
    ventana_pago = Toplevel(root)
    ventana_pago.title("Pago del Cliente")
    ventana_pago.geometry("300x150")

    total_a_pagar = cliente.get("Total Compras", 0)
    abono_inicial = cliente.get("Abono", 0)
    
    ttk.Label(ventana_pago, text=f"Total de la compra: ${total_a_pagar:.2f}", font=("Arial", 12, "bold")).pack(pady=10)
    ttk.Label(ventana_pago, text=f"Abono inicial: ${abono_inicial:.2f}").pack()
    
    ttk.Label(ventana_pago, text="Cantidad recibida:").pack()
    entrada_recibido = ttk.Entry(ventana_pago)
    entrada_recibido.pack()
    entrada_recibido.insert(0, str(total_a_pagar))

    def procesar_pago():
        try:
            cantidad_recibida = float(entrada_recibido.get())
        except ValueError:
            messagebox.showwarning("Error", "La cantidad recibida debe ser un número.")
            return
        
        # Calcular el cambio
        cambio = cantidad_recibida - total_a_pagar
        
        # Determinar si hay deuda o si todo está pagado
        if cantidad_recibida < total_a_pagar:
            cliente["Deuda"] = total_a_pagar - cantidad_recibida
            cliente["Abono"] = cantidad_recibida
            messagebox.showinfo("Deuda", f"El cliente aún debe: ${cliente['Deuda']:.2f}")
        else:
            cliente["Deuda"] = 0.0
            cliente["Abono"] = total_a_pagar
            if cambio > 0:
                messagebox.showinfo("Cambio", f"Dar de cambio al cliente: ${cambio:.2f}")

        # Guardar cliente y venta
        fecha_ingreso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nuevo_cliente = {
            "id": len(clientes) + 1,
            "Nombre": cliente["Nombre"],
            "Dirección": cliente["Dirección"],
            "Teléfono": cliente["Teléfono"],
            "Compras": cliente["Compras"],
            "Total Compras": total_a_pagar,
            "Abono": cliente["Abono"],
            "Deuda": cliente["Deuda"],
            "Fecha Ingreso": fecha_ingreso,
            "Artículos": cliente["Artículos"]
        }
        
        ventas.append({
            "Cliente": cliente["Nombre"],
            "Fecha": fecha_ingreso,
            "Articulos": cliente["Artículos"],
            "Total Venta": total_a_pagar,
            "Abono": cliente["Abono"],
            "Deuda Pendiente": cliente["Deuda"]
        })
        
        clientes.append(nuevo_cliente)
        
        guardar_datos(VENTAS_JSON, ventas)
        guardar_datos(ARCHIVO_CLIENTES, clientes)

        messagebox.showinfo("Éxito", f"Cliente '{cliente['Nombre']}' registrado correctamente.")
        
        ventana_pago.destroy()
        limpiar_pantalla()
        # Llamamos a imprimir_nota con los datos actualizados
        imprimir_nota(nuevo_cliente, on_complete_callback=menu_clientes)
    
    ttk.Button(ventana_pago, text="Procesar Pago", command=procesar_pago, bootstyle="success").pack(pady=10)

# --- Guardar cliente ---
def guardar_cliente():
    """
    Guarda los datos del nuevo cliente, y llama a la función para
    gestionar el pago antes de generar la nota.
    """
    global clientes, compras, entrada_abono

    nombre = entrada_nombre.get().strip()
    direccion = entrada_direccion.get().strip()
    telefono = entrada_telefono.get().strip()

    if not nombre or not direccion or not telefono:
        messagebox.showwarning("Advertencia", "Todos los campos son obligatorios.")
        return

    try:
        abono_inicial = float(entrada_abono.get() or 0)
    except ValueError:
        messagebox.showwarning("Advertencia", "El abono inicial debe ser un número.")
        return

    total_compras = sum(compra.get("Total", 0) for compra in compras)
    
    # Creamos un diccionario temporal para la nota
    cliente_temporal = {
        "Nombre": nombre,
        "Dirección": direccion,
        "Teléfono": telefono,
        "Compras": compras,
        "Total Compras": total_compras,
        "Abono": abono_inicial,
        "Deuda": total_compras - abono_inicial,
        "Artículos": compras
    }

    # Llamamos a la nueva ventana para gestionar el pago antes de guardar
    mostrar_ventana_pago(cliente_temporal)

def mostrar_ventana_pago(cliente):
    """
    Muestra una ventana para ingresar la cantidad recibida y calcular el cambio.
    """
    ventana_pago = Toplevel(root)
    ventana_pago.title("Pago del Cliente")
    ventana_pago.geometry("300x150")

    total_a_pagar = cliente.get("Total Compras", 0)
    abono_inicial = cliente.get("Abono", 0)
    
    ttk.Label(ventana_pago, text=f"Total de la compra: ${total_a_pagar:.2f}", font=("Arial", 12, "bold")).pack(pady=10)
    ttk.Label(ventana_pago, text=f"Abono inicial: ${abono_inicial:.2f}").pack()
    
    ttk.Label(ventana_pago, text="Cantidad recibida:").pack()
    entrada_recibido = ttk.Entry(ventana_pago)
    entrada_recibido.pack()
    entrada_recibido.insert(0, str(total_a_pagar))

    def procesar_pago():
        try:
            cantidad_recibida = float(entrada_recibido.get())
        except ValueError:
            messagebox.showwarning("Error", "La cantidad recibida debe ser un número.")
            return
        
        # Calcular el cambio
        cambio = cantidad_recibida - total_a_pagar
        
        # Determinar si hay deuda o si todo está pagado
        if cantidad_recibida < total_a_pagar:
            cliente["Deuda"] = total_a_pagar - cantidad_recibida
            cliente["Abono"] = cantidad_recibida
            messagebox.showinfo("Deuda", f"El cliente aún debe: ${cliente['Deuda']:.2f}")
        else:
            cliente["Deuda"] = 0.0
            cliente["Abono"] = total_a_pagar
            if cambio > 0:
                messagebox.showinfo("Cambio", f"Dar de cambio al cliente: ${cambio:.2f}")

        # Guardar cliente y venta
        fecha_ingreso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nuevo_cliente = {
            "id": len(clientes) + 1,
            "Nombre": cliente["Nombre"],
            "Dirección": cliente["Dirección"],
            "Teléfono": cliente["Teléfono"],
            "Compras": cliente["Compras"],
            "Total Compras": total_a_pagar,
            "Abono": cliente["Abono"],
            "Deuda": cliente["Deuda"],
            "Fecha Ingreso": fecha_ingreso,
            "Artículos": cliente["Artículos"]
        }
        
        ventas.append({
            "Cliente": cliente["Nombre"],
            "Fecha": fecha_ingreso,
            "Articulos": cliente["Artículos"],
            "Total Venta": total_a_pagar,
            "Abono": cliente["Abono"],
            "Deuda Pendiente": cliente["Deuda"]
        })
        
        clientes.append(nuevo_cliente)
        
        guardar_datos(VENTAS_JSON, ventas)
        guardar_datos(ARCHIVO_CLIENTES, clientes)

        messagebox.showinfo("Éxito", f"Cliente '{cliente['Nombre']}' registrado correctamente.")
        
        ventana_pago.destroy()
        limpiar_pantalla()
        # Llamamos a imprimir_nota con los datos actualizados
        imprimir_nota(nuevo_cliente, on_complete_callback=menu_clientes)
    
    ttk.Button(ventana_pago, text="Procesar Pago", command=procesar_pago, bootstyle="success").pack(pady=10)
    
def imprimir_nota(cliente, on_complete_callback=None):
    """
    Genera y muestra la nota de compra en una ventana de Toplevel.
    Ahora solo muestra el abono y deuda si el cliente no ha pagado el total.
    """
    nota_window = Toplevel(root)
    nota_window.title("Nota de Compra")
    nota_window.geometry("450x650")

    nombre_cliente = cliente.get("Nombre", "")
    fecha_compra = datetime.now().strftime("%Y-%m-%d")
    hora_compra = datetime.now().strftime("%H:%M:%S")
    articulos = cliente.get("Artículos", [])
    total_compra = float(cliente.get("Total Compras", 0.0))
    abono = float(cliente.get("Abono", 0.0))
    deuda = float(cliente.get("Deuda", 0.0))

    # --- Crear folio único ---
    base_nombre = re.sub(r"\W+", "_", nombre_cliente).strip("_") or "cliente"
    carpeta_notas = os.path.join(os.getcwd(), "notas_clientes")
    os.makedirs(carpeta_notas, exist_ok=True)
    folio_path = os.path.join(carpeta_notas, "ultimo_folio.txt")
    try:
        with open(folio_path, "r") as f:
            ultimo_folio = int(f.read().strip() or "0")
    except Exception:
        ultimo_folio = 0
    nuevo_folio = ultimo_folio + 1
    with open(folio_path, "w") as f:
        f.write(str(nuevo_folio))

    # --- Lógica para consolidar artículos ---
    articulos_consolidados = {}
    for art in articulos:
        nombre_art = art.get("Nombre", "")
        precio_unit = art.get("Precio Unitario", art.get("Total", 0) / max(art.get("Cantidad", 1), 1))
        cantidad = art.get("Cantidad", 0)

        if nombre_art in articulos_consolidados:
            articulos_consolidados[nombre_art]["Cantidad"] += cantidad
            articulos_consolidados[nombre_art]["Total"] += float(art.get("Total", 0))
        else:
            articulos_consolidados[nombre_art] = {
                "Cantidad": cantidad,
                "PrecioUnitario": precio_unit,
                "Total": float(art.get("Total", 0))
            }
    
    # --- Contenido de la nota en texto plano para la ventana y el TXT ---
    nota_texto = ""
    nota_texto += "********** NOTA DE COMPRA **********\n"
    nota_texto += "DIRECCIÓN DE FOMENTO ECONÓMICO\n"
    nota_texto += "Calle 24 de Febrero, Colonia Lomas del Panteón\n"
    nota_texto += "Maravatío, Michoacán\n"
    nota_texto += "SEDATU del Panteón\n"
    nota_texto += f"Folio: {nuevo_folio}\n"
    nota_texto += "----------------------------------------\n"
    nota_texto += f"Cliente: {nombre_cliente}\n"
    nota_texto += f"Fecha: {fecha_compra}  Hora: {hora_compra}\n"
    nota_texto += f"Teléfono: {cliente.get('Teléfono','')}  Ciudad: {cliente.get('Dirección','')}\n"
    nota_texto += "----------------------------------------\n"
    nota_texto += f"{'CANT.':<5} {'ARTÍCULO':<25} {'PRECIO':>8} {'IMPORTE':>10}\n"
    nota_texto += "-"*50 + "\n"

    for nombre_art, art in articulos_consolidados.items():
        cantidad = art.get("Cantidad", 0)
        precio_unit = art.get("PrecioUnitario", 0)
        total_art = art.get("Total", 0)
        nota_texto += f"{str(cantidad):<5} {nombre_art:<25} ${precio_unit:>7.2f} ${total_art:>9.2f}\n"

    nota_texto += "-"*50 + "\n"
    nota_texto += f"{'TOTAL:':<30} ${total_compra:>9.2f}\n"
    
    # Solo agrega el abono y la deuda si hay deuda pendiente
    if deuda > 0:
        nota_texto += f"{'ABONO:':<30} ${abono:>9.2f}\n"
        nota_texto += f"{'DEUDA:':<30} ${deuda:>9.2f}\n"
    
    nota_texto += "----------------------------------------\n"
    nota_texto += "¡Gracias por su compra!\n"
    nota_texto += "RECIBÍ PRODUCTOS EN BUEN ESTADO\n"

    text_widget = Text(nota_window, wrap="word", font=("Arial", 10), padx=10, pady=10)
    text_widget.insert("1.0", nota_texto)
    text_widget.configure(state="disabled")
    text_widget.pack(expand=True, fill="both")

    # --- Guardar TXT ---
    def guardar_txt():
        fecha_archivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        nombre_archivo = f"nota_{base_nombre}_{fecha_archivo}.txt"
        ruta_completa = os.path.join(carpeta_notas, nombre_archivo)
        try:
            with open(ruta_completa, "w", encoding="utf-8") as f:
                f.write(nota_texto)
            messagebox.showinfo("Guardado", f"Nota guardada como TXT en:\n{ruta_completa}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo TXT: {e}")

    # --- Guardar PDF y cerrar la ventana ---
    def guardar_y_aceptar():
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas as pdf_canvas
        except ImportError:
            messagebox.showerror("Error", "La biblioteca 'reportlab' no está instalada o no se importó correctamente.")
            return

        fecha_archivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        nombre_archivo = os.path.join(
            carpeta_notas, f"nota_{base_nombre}_{fecha_archivo}_F{nuevo_folio}.pdf"
        )
        c = pdf_canvas.Canvas(nombre_archivo, pagesize=letter)
        width, height = letter

        # --- Logos y encabezado ---
        try:
            if os.path.exists(logo_mara_path):
                c.drawImage(logo_mara_path, 40, height-110, width=120, height=80, preserveAspectRatio=True, mask='auto')
            
            if os.path.exists(logo_fome_path):
                c.drawImage(logo_fome_path, width-170, height-110, width=120, height=80, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width/2, height-50, "DIRECCIÓN DE FOMENTO ECONÓMICO")
        c.setFont("Helvetica", 11)
        c.drawCentredString(width/2, height-65, "Calle 24 de Febrero, Colonia Lomas del Panteón")
        c.drawCentredString(width/2, height-80, "Maravatío, Michoacán")
        c.drawCentredString(width/2, height-95, "SEDATU del Panteón")


        # --- Datos del cliente ---
        y_cliente = height - 130
        c.setFont("Helvetica", 11)
        c.drawString(50, y_cliente, f"Nombre: {nombre_cliente}")
        c.drawRightString(width - 50, y_cliente, f"Fecha: {fecha_compra}")
        y_cliente -= 20
        c.drawString(50, y_cliente, f"Ciudad: {cliente.get('Dirección','')}")
        c.drawRightString(width - 50, y_cliente, f"Teléfono: {cliente.get('Teléfono','')}")
        
        # MOdificación para que el folio aparezca debajo del teléfono
        y_cliente -= 20
        # Ahora se dibuja el folio con el mismo tamaño y color que el anterior
        c.setFont("Helvetica-Bold", 16) # Aumenta el tamaño de la fuente
        c.setFillColorRGB(1, 0, 0) # Cambia el color a rojo
        c.drawRightString(width - 50, y_cliente, f"Folio No. {nuevo_folio}")
        c.setFillColorRGB(0, 0, 0) # Vuelve el color a negro para el resto del texto
        y_cliente -= 20

        # --- Dibujar tabla (recuadro) ---
        tabla_top = y_cliente
        tabla_bottom = 200
        c.rect(50, tabla_bottom, width-100, tabla_top - tabla_bottom)

        # Ajuste de las líneas verticales para alinear con las columnas de texto
        c.line(110, tabla_bottom, 110, tabla_top)
        # La coordenada X para la línea del precio se ajusta para que coincida con el texto
        c.line(400, tabla_bottom, 400, tabla_top) 
        c.line(480, tabla_bottom, 480, tabla_top)

        c.setFont("Helvetica-Bold", 11)
        c.drawString(55, tabla_top - 15, "CANT.")
        c.drawString(120, tabla_top - 15, "ARTÍCULO")
        c.drawString(405, tabla_top - 15, "PRECIO")
        c.drawString(485, tabla_top - 15, "IMPORTE")

        c.line(50, tabla_top - 20, width-50, tabla_top - 20)

        # --- Renglones de artículos dentro del recuadro ---
        c.setFont("Helvetica", 10)
        y_art = tabla_top - 40
        for nombre_art, art in articulos_consolidados.items():
            cantidad = art.get("Cantidad", 0)
            precio_unit = art.get("PrecioUnitario", 0)
            total_art = art.get("Total", 0)
            
            c.drawString(55, y_art, str(cantidad))
            c.drawString(120, y_art, nombre_art)
            c.drawRightString(470, y_art, f"${precio_unit:.2f}") 
            c.drawRightString(560, y_art, f"${total_art:.2f}")  

            y_art -= 20
            if y_art < tabla_bottom + 20:
                break

        # --- Totales y abonos ---
        c.setFont("Helvetica-Bold", 12)
        c.drawString(width-190, 180, "TOTAL $")
        c.drawRightString(width-60, 180, f"${total_compra:.2f}")

        # Solo agrega el abono y la deuda al PDF si hay deuda pendiente
        if deuda > 0:
            c.drawString(width-190, 160, "ABONO $")
            c.drawRightString(width-60, 160, f"${abono:.2f}")
            
            c.drawString(width-190, 140, "DEUDA $")
            c.drawRightString(width-60, 140, f"${deuda:.2f}")

        # --- Pie de página ---
        c.setFont("Helvetica", 10)
        c.drawString(50, 100, "RECIBÍ PRODUCTOS EN BUEN ESTADO")
        c.drawCentredString(width/2, 50, "¡Gracias por su compra!")
        c.save()
        messagebox.showinfo("Guardado", f"Nota guardada como PDF en:\n{nombre_archivo}")
        
        # Cierra la ventana actual y llama al callback si existe
        nota_window.destroy()
        if on_complete_callback:
            on_complete_callback()


    # --- Botones de la ventana ---
    frame_botones = ttk.Frame(nota_window)
    frame_botones.pack(pady=10)
    ttk.Button(frame_botones, text="Guardar como TXT", command=guardar_txt).pack(side="left", padx=5)
    ttk.Button(frame_botones, text="Guardar y Aceptar", command=guardar_y_aceptar).pack(side="left", padx=5)
    ttk.Button(frame_botones, text="Cancelar", command=nota_window.destroy).pack(side="left", padx=5)

def ver_clientes():
    """Muestra la lista de clientes con opciones para ver y eliminar."""
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

            # Botón único de eliminar con manita
            ttk.Button(
                frame_resultados,
                text="Eliminar",
                command=lambda c=cliente: eliminar_cliente(c["id"]),
                bootstyle="danger",
                cursor="hand2"
            ).pack(pady=2)

    ttk.Button(frame_resultados, text="Quitar Artículo por Pedir", command=buscar_y_quitar_articulo).pack(pady=10)

    ttk.Button(frame_resultados, text="Regresar al Menú de Clientes", command=menu_clientes, bootstyle="secondary").pack(pady=10)


def buscar_cliente():
    """Muestra una ventana para buscar un cliente y ver su información."""
    cliente_nombre = simpledialog.askstring("Buscar Cliente", "Ingrese el nombre del cliente:")
    
    if not cliente_nombre:
        return
        
    cliente_nombre = cliente_nombre.strip().lower()
    
    cliente = next((c for c in clientes if cliente_nombre in c["Nombre"].lower()), None)
    
    if cliente:
        detalles = f"Nombre: {cliente['Nombre']}\n"
        detalles += f"Dirección: {cliente['Dirección']}\n"
        detalles += f"Teléfono: {cliente['Teléfono']}\n"
        detalles += f"Total Compras: ${cliente['Total Compras']:.2f}\n"
        detalles += f"Abono: ${cliente['Abono']:.2f}\n"
        detalles += f"Deuda: ${cliente['Deuda']:.2f}\n"
        detalles += f"Fecha de Ingreso: {cliente['Fecha Ingreso']}\n"
        
        if cliente.get("Artículos"):
            detalles += "\nArtículos Comprados:\n"
            for art in cliente["Artículos"]:
                estado = "Por Pedir" if art.get("Por Pedir", False) else "Entregado"
                detalles += f"  - {art['Nombre']} (x{art['Cantidad']}) - Estado: {estado}\n"
        
        messagebox.showinfo("Detalles del Cliente", detalles)
    else:
        messagebox.showerror("Error", "Cliente no encontrado.")


def eliminar_cliente(id_cliente):
    """Elimina un cliente de la lista por su ID."""
    global clientes
    clientes = [c for c in clientes if c["id"] != id_cliente]

    guardar_datos(ARCHIVO_CLIENTES, clientes)
    messagebox.showinfo("Éxito", f"Cliente con ID {id_cliente} eliminado correctamente.")
    ver_clientes()


def buscar_y_quitar_articulo():
    """Muestra una ventana para gestionar los artículos por pedir de un cliente."""
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

                for stock_articulo in almacen:
                    if stock_articulo.get("Nombre", "").lower() == articulo["Nombre"].lower():
                        stock_actual = stock_articulo.get("Stock", 0)
                        cantidad_solicitada = articulo.get("Cantidad", 0)
                        stock_articulo["Stock"] = max(0, stock_actual - cantidad_solicitada)

                        if "Historial" not in stock_articulo:
                            stock_articulo["Historial"] = []
                        stock_articulo["Historial"].append({
                            "Cliente": cliente.get("Nombre", ""),
                            "Cantidad": cantidad_solicitada,
                            "Fecha": articulo["FechaEntrega"],
                            "Precio": articulo.get("Precio", articulo.get("Total", 0) / max(articulo.get("Cantidad", 1), 1))
                        })
                        break

                if "Compras" not in cliente:
                    cliente["Compras"] = []
                cliente["Compras"].append({
                    "Nombre": articulo["Nombre"],
                    "Cantidad": articulo["Cantidad"],
                    "Precio": articulo.get("Precio", articulo.get("Total", 0) / max(articulo.get("Cantidad", 1), 1)),
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
    """Muestra el estado de los artículos pendientes y entregados de un cliente."""
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

# """MENU ARTICULOS"""
def menu_articulos():
    """Muestra la pantalla del menú de artículos."""
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)
    
    ttk.Label(frame, text="Menú Artículos", font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Button(frame, text="Ingresar Artículo", command=ingresar_articulo_almacen, bootstyle="primary", width=30).pack(pady=5)
    ttk.Button(frame, text="Ver Almacén", command=ver_almacen, bootstyle="info", width=30).pack(pady=5)
    ttk.Button(frame, text="Ajustar Artículo", command=ajustar_stock_almacen, bootstyle="success", width=30).pack(pady=5)
    ttk.Button(frame, text="Regresar al Menú", command=menu_principal, bootstyle="secondary", width=30).pack(pady=5)

def ingresar_articulo_almacen():
    """Muestra el formulario para ingresar un nuevo artículo al almacén."""
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)
    
    ttk.Label(frame, text="Ingresar Artículo al Almacén", font=("Arial", 14, "bold")).pack(pady=10)

    ttk.Label(frame, text="Nombre del Artículo").pack()
    nombre_articulo = ttk.Entry(frame)
    nombre_articulo.pack()

    ttk.Label(frame, text="Stock").pack()
    stock_articulo = ttk.Entry(frame)
    stock_articulo.pack()

    ttk.Label(frame, text="Precio de Compra").pack()
    precio_compra_articulo = ttk.Entry(frame)
    precio_compra_articulo.pack()

    ttk.Label(frame, text="Precio Público").pack()
    precio_publico_articulo = ttk.Entry(frame)
    precio_publico_articulo.pack()

    def guardar_articulo():
        nombre = nombre_articulo.get().strip()
        try:
            stock = int(stock_articulo.get())
            precio_compra = float(precio_compra_articulo.get())
            precio_publico = float(precio_publico_articulo.get())
        except ValueError:
            messagebox.showwarning("Advertencia", "El Stock y los Precios deben ser números.")
            return
        
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre es obligatorio.")
            return

        nuevo_articulo = {
            "id": len(almacen) + 1,
            "Nombre": nombre,
            "Stock": stock,
            "Precio Compra": precio_compra,
            "Precio Público": precio_publico,
            "Historial": []
        }
        almacen.append(nuevo_articulo)
        guardar_datos(ALMACEN_JSON, almacen)
        messagebox.showinfo("Éxito", f"Artículo '{nombre}' registrado en el almacén.")
        ver_almacen()

    ttk.Button(frame, text="Guardar Artículo", command=guardar_articulo, bootstyle="success").pack(pady=10)
    ttk.Button(frame, text="Cancelar", command=menu_articulos, bootstyle="danger").pack(pady=5)

def ver_almacen():
    """Muestra la lista de artículos disponibles en el almacén."""
    limpiar_pantalla()
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
    
    ttk.Label(frame_resultados, text="Inventario del Almacén", font=("Arial", 14, "bold")).pack(pady=10)
    
    if not almacen:
        ttk.Label(frame_resultados, text="No hay artículos en el almacén.").pack(pady=10)
    else:
        for articulo in almacen:
            # CORRECCIÓN: Se usa .get() para evitar el error KeyError si la clave no existe en un artículo.
            # Esto es útil si el archivo JSON se creó con una versión anterior del código.
            articulo_id = articulo.get('id', 'N/A')
            nombre = articulo.get('Nombre', 'N/A')
            stock = articulo.get('Stock', 'N/A')

            ttk.Label(
                frame_resultados,
                text=f"ID: {articulo_id} - Nombre: {nombre} - Stock: {stock}"
            ).pack(pady=2)

    # Crea un frame para los botones para que estén separados y se limpien correctamente.
    frame_botones = ttk.Frame(root)
    frame_botones.pack(pady=10)
    ttk.Button(frame_botones, text="Regresar al Menú", command=menu_articulos, bootstyle="secondary").pack()

def ajustar_stock_almacen():
    """Permite seleccionar un artículo para modificarlo."""
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Seleccionar Artículo a Modificar", font=("Arial", 14, "bold")).pack(pady=10)

    seleccion_articulo = tk.StringVar()
    articulo_menu = ttk.Combobox(frame, textvariable=seleccion_articulo, values=[item['Nombre'] for item in almacen], width=40)
    articulo_menu.pack(pady=10)

    def aceptar_articulo():
        nombre = seleccion_articulo.get()
        if not nombre:
            messagebox.showwarning("Advertencia", "Debe seleccionar un artículo.")
            return

        for articulo in almacen:
            if articulo["Nombre"] == nombre:
                ventana_modificar_articulo(articulo)
                return

        messagebox.showerror("Error", "Artículo no encontrado.")

    ttk.Button(frame, text="Aceptar", command=aceptar_articulo, bootstyle="success").pack(pady=5)
    ttk.Button(frame, text="Cancelar", command=menu_articulos, bootstyle="danger").pack(pady=5)


def ventana_modificar_articulo(articulo):
    """Abre una ventana para modificar un artículo en específico."""
    top = tk.Toplevel(root)
    top.title(f"Modificar Artículo: {articulo['Nombre']}")
    top.geometry("400x400")

    ttk.Label(top, text=f"Artículo seleccionado: {articulo['Nombre']}", font=("Arial", 12, "bold")).pack(pady=10)

    ttk.Label(top, text="Seleccione qué desea modificar:").pack(pady=5)
    opcion = tk.StringVar()
    opciones = ["Nombre", "Stock", "Precio Compra", "Precio Público"]
    combo_opcion = ttk.Combobox(top, textvariable=opcion, values=opciones, width=30)
    combo_opcion.pack(pady=5)

    ttk.Label(top, text="Nuevo valor:").pack(pady=5)
    entrada_valor = ttk.Entry(top, width=30)
    entrada_valor.pack(pady=5)

    def guardar_cambio():
        campo = opcion.get()
        valor = entrada_valor.get().strip()

        if not campo:
            messagebox.showwarning("Advertencia", "Debe seleccionar una opción de modificación.")
            return
        if not valor:
            messagebox.showwarning("Advertencia", "Debe ingresar un valor.")
            return

        try:
            if campo == "Stock":
                # Validar que el valor es número y mayor o igual a 0
                nuevo_stock = int(valor)
                if nuevo_stock < 0:
                    messagebox.showwarning("Advertencia", "El stock no puede ser negativo.")
                    return
                articulo["Stock"] = nuevo_stock

            elif campo == "Precio Compra":
                articulo["Precio Compra"] = float(valor)

            elif campo == "Precio Público":
                articulo["Precio Público"] = float(valor)

            elif campo == "Nombre":
                articulo["Nombre"] = valor

        except ValueError:
            messagebox.showerror("Error", f"El valor ingresado para {campo} no es válido.")
            return

        # Guardar en JSON
        guardar_datos(ALMACEN_JSON, almacen)

        # 🔥 Confirmar y refrescar valores
        messagebox.showinfo("Éxito", f"{campo} actualizado correctamente.\n"
                                     f"Nuevo valor: {articulo[campo] if campo != 'Nombre' else articulo['Nombre']}")

        top.destroy()
        respuesta = messagebox.askyesno("Continuar", "¿Desea modificar otro artículo?")
        if respuesta:
            ajustar_stock_almacen()
        else:
            menu_articulos()

    ttk.Button(top, text="Aceptar", command=guardar_cambio, bootstyle="success").pack(pady=10)
    ttk.Button(top, text="Cancelar", command=lambda: [top.destroy(), menu_articulos()], bootstyle="danger").pack(pady=5)


def ver_almacen():
    """Muestra la lista de artículos disponibles en el almacén (siempre actualizada)."""
    limpiar_pantalla()
    
    frame_contenedor = ttk.Frame(root)
    frame_contenedor.pack(fill="both", expand=True, pady=10)

    lienzo = tk.Canvas(frame_contenedor)
    scrollbar = ttk.Scrollbar(frame_contenedor, orient="vertical", command=lienzo.yview)
    frame_resultados = ttk.Frame(lienzo)

    # Configurar el scroll
    frame_resultados.bind("<Configure>", lambda e: lienzo.configure(scrollregion=lienzo.bbox("all")))
    lienzo.create_window((0, 0), window=frame_resultados, anchor="nw")
    lienzo.configure(yscrollcommand=scrollbar.set)

    lienzo.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Título
    ttk.Label(frame_resultados, text="Inventario del Almacén", font=("Arial", 14, "bold")).pack(pady=10)
    
    if not almacen:
        ttk.Label(frame_resultados, text="No hay artículos en el almacén.").pack(pady=10)
    else:
        for articulo in almacen:
            articulo_id = articulo.get('id', 'N/A')
            nombre = articulo.get('Nombre', 'N/A')
            stock = articulo.get('Stock', 0)
            precio_compra = articulo.get('Precio Compra', 0.0)
            precio_publico = articulo.get('Precio Público', 0.0)

            ttk.Label(
                frame_resultados,
                text=f"ID: {articulo_id} | Nombre: {nombre} | Stock: {stock} | "
                     f"Compra: {precio_compra} | Público: {precio_publico}"
            ).pack(pady=2, anchor="w")

    # Botón regresar
    frame_botones = ttk.Frame(root)
    frame_botones.pack(pady=10)
    ttk.Button(frame_botones, text="Regresar al Menú", command=menu_articulos, bootstyle="secondary").pack()

        
# --- GESTIÓN DE PROVEEDORES ---
def menu_proveedores():
    """Muestra la pantalla del menú de proveedores."""
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Menú Proveedores", font=("Arial", 14, "bold")).pack(pady=10)
    ttk.Button(frame, text="Ingresar Proveedor", command=ingresar_proveedor, bootstyle="primary", width=30).pack(pady=5)
    ttk.Button(frame, text="Ver Proveedores", command=ver_proveedores, bootstyle="info", width=30).pack(pady=5)
    ttk.Button(frame, text="Regresar al Menú", command=menu_principal, bootstyle="secondary", width=30).pack(pady=5)

def ingresar_proveedor():
    """
    Muestra el formulario para ingresar un nuevo proveedor y sus artículos.
    """
    global entrada_nombre_proveedor, entrada_telefono_proveedor, articulos_proveedor
    limpiar_pantalla()
    frame = ttk.Frame(root)
    frame.pack(pady=20)

    ttk.Label(frame, text="Ingresar Nuevo Proveedor", font=("Arial", 14, "bold")).pack(pady=10)

    entrada_nombre_proveedor = ttk.Entry(frame)
    entrada_nombre_proveedor.pack()
    ttk.Label(frame, text="Nombre del Proveedor").pack()

    entrada_telefono_proveedor = ttk.Entry(frame)
    entrada_telefono_proveedor.pack()
    ttk.Label(frame, text="Teléfono del Proveedor").pack()

    articulos_proveedor = []

    def agregar_y_mostrar_articulos():
        ventana_articulo = Toplevel(root)
        ventana_articulo.title("Agregar Artículo a Proveedor")
        ventana_articulo.geometry("350x300")
        
        ttk.Label(ventana_articulo, text="Nombre del Artículo").pack(pady=5)
        entrada_nombre_articulo = ttk.Entry(ventana_articulo)
        entrada_nombre_articulo.pack(pady=5)

        ttk.Label(ventana_articulo, text="Cantidad de Artículos").pack(pady=5)
        entrada_cantidad = ttk.Entry(ventana_articulo)
        entrada_cantidad.pack(pady=5)
        
        ttk.Label(ventana_articulo, text="Precio de Proveedor").pack(pady=5)
        entrada_precio_proveedor = ttk.Entry(ventana_articulo)
        entrada_precio_proveedor.pack(pady=5)

        ttk.Label(ventana_articulo, text="Precio Público").pack(pady=5)
        entrada_precio_publico = ttk.Entry(ventana_articulo)
        entrada_precio_publico.pack(pady=5)

        def guardar_articulo_temp():
            nombre_articulo = entrada_nombre_articulo.get().strip()
            try:
                cantidad = int(entrada_cantidad.get())
                precio_proveedor = float(entrada_precio_proveedor.get())
                precio_publico = float(entrada_precio_publico.get())
                if not all([nombre_articulo, cantidad >= 0, precio_proveedor >= 0, precio_publico >= 0]):
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Advertencia", "Por favor, ingrese datos válidos en todos los campos.")
                return

            articulo = {
                "Nombre": nombre_articulo,
                "Cantidad": cantidad,
                "Precio Proveedor": precio_proveedor,
                "Precio Público": precio_publico
            }
            articulos_proveedor.append(articulo)
            ventana_articulo.destroy()
            
            if messagebox.askyesno("Agregar Artículo", "¿Desea agregar otro artículo?"):
                agregar_y_mostrar_articulos()

        ttk.Button(ventana_articulo, text="Guardar Artículo", command=guardar_articulo_temp, bootstyle="success").pack(pady=10)
        ttk.Button(ventana_articulo, text="Cancelar", command=ventana_articulo.destroy, bootstyle="danger").pack(pady=5)

    ttk.Button(frame, text="Agregar Artículo", command=agregar_y_mostrar_articulos, bootstyle="primary").pack(pady=10)
    ttk.Button(frame, text="Guardar Proveedor", command=guardar_proveedor, bootstyle="success").pack(pady=5)
    ttk.Button(frame, text="Cancelar", command=menu_proveedores, bootstyle="danger").pack(pady=5)


def guardar_proveedor():
    """
    Guarda el proveedor y sus artículos en el archivo JSON y actualiza el almacén.
    """
    global entrada_nombre_proveedor, entrada_telefono_proveedor, articulos_proveedor, proveedores, almacen
    
    nombre_proveedor = entrada_nombre_proveedor.get().strip()
    telefono_proveedor = entrada_telefono_proveedor.get().strip()
    
    if not nombre_proveedor or not telefono_proveedor or not articulos_proveedor:
        messagebox.showwarning("Advertencia", "Debe ingresar el nombre, teléfono y al menos un artículo para el proveedor.")
        return

    total_adeudo = sum(art["Cantidad"] * art["Precio Proveedor"] for art in articulos_proveedor)
    
    max_id = 0
    if proveedores:
        max_id = max(p.get("id", 0) for p in proveedores)
    nuevo_id = max_id + 1

    nuevo_proveedor = {
        "id": nuevo_id,
        "Nombre": nombre_proveedor,
        "Teléfono": telefono_proveedor,
        "Artículos Ingresados": articulos_proveedor,
        "Adeudo Total": total_adeudo,
        "Fecha Ingreso": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Abonos": [] # Lista vacía para futuros abonos
    }

    proveedores.append(nuevo_proveedor)
    guardar_datos(ARCHIVO_PROVEEDORES, proveedores)

    # Actualizar stock del almacén con los nuevos artículos
    for art in articulos_proveedor:
        articulo_existente = next((item for item in almacen if item.get("Nombre") == art["Nombre"]), None)
        if articulo_existente:
            articulo_existente["Stock"] += art["Cantidad"]
            articulo_existente["Precio Público"] = art["Precio Público"]
            articulo_existente["Precio Compra"] = art["Precio Proveedor"]
        else:
            almacen.append({
                "id": len(almacen) + 1,
                "Nombre": art["Nombre"],
                "Stock": art["Cantidad"],
                "Precio Público": art["Precio Público"],
                "Precio Compra": art["Precio Proveedor"]
            })
    guardar_datos(ALMACEN_JSON, almacen)
    
    messagebox.showinfo("Éxito", f"Proveedor '{nombre_proveedor}' ingresado correctamente. El total a deber es: ${total_adeudo:.2f}")
    menu_proveedores()


def ver_proveedores():
    """
    Muestra una ventana para buscar y ver detalles de proveedores.
    """
    global proveedores

    ventana = Toplevel(root)
    ventana.title("Ver y Buscar Proveedores")
    ventana.geometry("700x550")

    frame_principal = ttk.Frame(ventana, padding=20)
    frame_principal.pack(fill="both", expand=True)

    frame_busqueda = ttk.LabelFrame(frame_principal, text="Buscar Proveedor", padding=10)
    frame_busqueda.pack(fill="x", pady=(0, 10))

    search_var = StringVar()
    entry_search = ttk.Entry(frame_busqueda, textvariable=search_var, width=50)
    entry_search.pack(side="left", fill="x", expand=True, padx=(0, 10))

    def filtrar_proveedores(event=None):
        query = search_var.get().strip().lower()
        tree.delete(*tree.get_children())

        if not query:
            resultados = proveedores
        else:
            resultados = [p for p in proveedores if query in p["Nombre"].lower() or any(query in parte for parte in p["Nombre"].lower().split())]

        if not resultados:
            messagebox.showinfo("Búsqueda", "No se encontraron proveedores con ese nombre.")
            return

        for p in resultados:
            item_id = p.get("id")
            tree.insert('', 'end', iid=item_id, values=(
                p.get("Nombre", "N/A"),
                p.get("Teléfono", "N/A"),
                f"${p.get('Adeudo Total', 0):.2f}"
            ))

    entry_search.bind("<Return>", filtrar_proveedores)
    ttk.Button(frame_busqueda, text="Buscar", command=filtrar_proveedores, bootstyle="primary").pack(side="left", padx=5)
    ttk.Button(frame_busqueda, text="Mostrar Todos", command=lambda: [search_var.set(""), filtrar_proveedores()], bootstyle="info").pack(side="left", padx=5)

    frame_lista = ttk.LabelFrame(frame_principal, text="Lista de Proveedores", padding=10)
    frame_lista.pack(fill="both", expand=True, pady=10)

    columns = ("Nombre", "Teléfono", "Adeudo")
    tree = ttk.Treeview(frame_lista, columns=columns, show="headings")
    tree.heading("Nombre", text="Nombre del Proveedor")
    tree.heading("Teléfono", text="Teléfono")
    tree.heading("Adeudo", text="Adeudo")

    tree.column("Nombre", width=250, anchor='center')
    tree.column("Teléfono", width=150, anchor='center')
    tree.column("Adeudo", width=120, anchor='center')

    scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)

    def on_select(event):
        try:
            item_id = tree.selection()[0]
            proveedor_encontrado = next((p for p in proveedores if str(p.get("id")) == str(item_id)), None)
            if proveedor_encontrado:
                mostrar_detalles_proveedor(proveedor_encontrado)
        except IndexError:
            pass

    tree.bind("<<TreeviewSelect>>", on_select)

    ttk.Button(frame_principal, text="Regresar a Menú", command=ventana.destroy, bootstyle="secondary").pack(pady=10)
    
    filtrar_proveedores()

def mostrar_detalles_proveedor(proveedor):
    """
    Muestra una ventana con los detalles de un proveedor específico,
    incluyendo abonos y opción para modificar.
    """
    detalles_ventana = Toplevel(root)
    detalles_ventana.title(f"Detalles de {proveedor['Nombre']}")
    detalles_ventana.geometry("650x700")

    frame_principal = ttk.Frame(detalles_ventana, padding=20)
    frame_principal.pack(fill="both", expand=True)

    frame_info = ttk.LabelFrame(frame_principal, text="Información General", padding=10)
    frame_info.pack(fill="x", pady=(0, 10))
    ttk.Label(frame_info, text=f"Nombre: {proveedor['Nombre']}", font=("Arial", 11, "bold")).pack(anchor='w')
    ttk.Label(frame_info, text=f"Teléfono: {proveedor['Teléfono']}", font=("Arial", 11)).pack(anchor='w')
    adeudo_label = ttk.Label(frame_info, text=f"Adeudo Total: ${proveedor['Adeudo Total']:.2f}", font=("Arial", 11, "bold"))
    adeudo_label.pack(anchor='w')

    frame_abono = ttk.Frame(frame_info)
    frame_abono.pack(fill='x', pady=5)
    ttk.Label(frame_abono, text="Monto a abonar:", font=("Arial", 10)).pack(side='left', padx=5)
    entrada_abono = ttk.Entry(frame_abono)
    entrada_abono.pack(side='left', fill='x', expand=True, padx=5)

    def registrar_abono():
        try:
            monto = float(entrada_abono.get())
            if monto <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese un monto válido mayor que cero.")
            return
        
        if monto > proveedor["Adeudo Total"]:
            messagebox.showwarning("Advertencia", "El monto del abono no puede ser mayor que el adeudo total.")
            return

        proveedor["Adeudo Total"] -= monto
        
        if "Abonos" not in proveedor:
            proveedor["Abonos"] = []
            
        nuevo_abono = {
            "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Monto": monto,
            "Adeudo Restante": proveedor["Adeudo Total"]
        }
        proveedor["Abonos"].append(nuevo_abono)
        
        guardar_datos(ARCHIVO_PROVEEDORES, proveedores)
        
        adeudo_label.config(text=f"Adeudo Total: ${proveedor['Adeudo Total']:.2f}")
        entrada_abono.delete(0, 'end')
        
        messagebox.showinfo("Éxito", "Abono registrado correctamente.")
        
        # Actualizar la lista de abonos
        tree_abonos.delete(*tree_abonos.get_children())
        for abono in proveedor.get("Abonos", []):
            tree_abonos.insert('', 'end', values=(
                abono.get("Fecha", "N/A"),
                f"${abono.get('Monto', 0):.2f}",
                f"${abono.get('Adeudo Restante', 0):.2f}"
            ))


    ttk.Button(frame_abono, text="Abonar", command=registrar_abono, bootstyle="success").pack(side='left', padx=5)


    frame_articulos = ttk.LabelFrame(frame_principal, text="Artículos Ingresados", padding=10)
    frame_articulos.pack(fill="both", expand=True, pady=10)
    columns_art = ("Nombre", "Cantidad", "P. Proveedor", "P. Público")
    tree_articulos = ttk.Treeview(frame_articulos, columns=columns_art, show="headings")
    tree_articulos.heading("Nombre", text="Nombre")
    tree_articulos.heading("Cantidad", text="Cant.")
    tree_articulos.heading("P. Proveedor", text="P. Proveedor")
    tree_articulos.heading("P. Público", text="P. Público")
    for articulo in proveedor.get("Artículos Ingresados", []):
        tree_articulos.insert('', 'end', values=(
            articulo.get("Nombre", "N/A"),
            articulo.get("Cantidad", 0),
            f"${articulo.get('Precio Proveedor', 0):.2f}",
            f"${articulo.get('Precio Público', 0):.2f}"
        ))
    tree_articulos.pack(fill="both", expand=True)


    frame_abonos = ttk.LabelFrame(frame_principal, text="Historial de Abonos (Pagos)", padding=10)
    frame_abonos.pack(fill="both", expand=True, pady=10)
    columns_abono = ("Fecha", "Monto", "Deuda Restante")
    tree_abonos = ttk.Treeview(frame_abonos, columns=columns_abono, show="headings")
    tree_abonos.heading("Fecha", text="Fecha")
    tree_abonos.heading("Monto", text="Monto Abonado")
    tree_abonos.heading("Deuda Restante", text="Deuda Restante")
    for abono in proveedor.get("Abonos", []):
        tree_abonos.insert('', 'end', values=(
            abono.get("Fecha", "N/A"),
            f"${abono.get('Monto', 0):.2f}",
            f"${abono.get('Adeudo Restante', 0):.2f}"
        ))
    tree_abonos.pack(fill="both", expand=True)
    
    frame_botones = ttk.Frame(frame_principal, padding=(0, 10))
    frame_botones.pack(fill="x")

    def abrir_modificar():
        detalles_ventana.destroy()
        modificar_proveedor_form(proveedor)

    def cerrar_y_volver():
        detalles_ventana.destroy()
        ver_proveedores()

    ttk.Button(frame_botones, text="Modificar Datos", command=abrir_modificar, bootstyle="warning").pack(side="left", padx=5, fill='x', expand=True)
    ttk.Button(frame_botones, text="Regresar", command=cerrar_y_volver, bootstyle="secondary").pack(side="right", padx=5, fill='x', expand=True)

def modificar_proveedor_form(proveedor):
    """
    Abre una nueva ventana para modificar los datos de un proveedor y sus artículos.
    """
    global proveedores, almacen
    ventana_modificar = Toplevel(root)
    ventana_modificar.title(f"Modificar Proveedor: {proveedor['Nombre']}")
    ventana_modificar.geometry("800x650")

    frame_principal = ttk.Frame(ventana_modificar, padding=20)
    frame_principal.pack(fill="both", expand=True)

    nombre_var = StringVar(value=proveedor["Nombre"])
    telefono_var = StringVar(value=proveedor["Teléfono"])
    
    frame_proveedor = ttk.LabelFrame(frame_principal, text="Datos del Proveedor", padding=10)
    frame_proveedor.pack(fill='x', pady=10)

    ttk.Label(frame_proveedor, text="Nombre del Proveedor").pack(anchor='w')
    entrada_nombre = ttk.Entry(frame_proveedor, textvariable=nombre_var)
    entrada_nombre.pack(fill='x', pady=5)

    ttk.Label(frame_proveedor, text="Teléfono del Proveedor").pack(anchor='w')
    entrada_telefono = ttk.Entry(frame_proveedor, textvariable=telefono_var)
    entrada_telefono.pack(fill='x', pady=5)
    
    frame_articulos = ttk.LabelFrame(frame_principal, text="Artículos Ingresados (Doble clic para editar)", padding=10)
    frame_articulos.pack(fill="both", expand=True, pady=10)

    columns = ("Nombre", "Cantidad", "Precio Proveedor", "Precio Público")
    tree_articulos = ttk.Treeview(frame_articulos, columns=columns, show="headings")
    tree_articulos.heading("Nombre", text="Nombre")
    tree_articulos.heading("Cantidad", text="Cant.")
    tree_articulos.heading("Precio Proveedor", text="P. Proveedor")
    tree_articulos.heading("Precio Público", text="P. Público")

    tree_articulos.column("Nombre", width=200)
    tree_articulos.column("Cantidad", width=80)
    tree_articulos.column("Precio Proveedor", width=120)
    tree_articulos.column("Precio Público", width=120)

    for i, articulo in enumerate(proveedor.get("Artículos Ingresados", [])):
        tree_articulos.insert('', 'end', iid=i, values=(
            articulo.get("Nombre", "N/A"),
            articulo.get("Cantidad", 0),
            articulo.get("Precio Proveedor", 0),
            articulo.get("Precio Público", 0)
        ))
    tree_articulos.pack(fill="both", expand=True)

    def editar_celda(event):
        item_id = tree_articulos.focus()
        if not item_id:
            return

        columna = tree_articulos.identify_column(event.x)
        col_index = int(columna.replace("#", "")) - 1
        x, y, ancho, alto = tree_articulos.bbox(item_id, columna)
        valor_actual = tree_articulos.item(item_id, "values")[col_index]

        entry_edit = ttk.Entry(tree_articulos)
        entry_edit.place(x=x, y=y, width=ancho, height=alto)
        entry_edit.insert(0, valor_actual)
        entry_edit.focus()

        def guardar_edicion(event=None):
            nuevo_valor = entry_edit.get()
            valores = list(tree_articulos.item(item_id, "values"))
            valores[col_index] = nuevo_valor
            tree_articulos.item(item_id, values=valores)
            entry_edit.destroy()

        entry_edit.bind("<Return>", guardar_edicion)
        entry_edit.bind("<FocusOut>", lambda e: entry_edit.destroy())

    def eliminar_articulo():
        selected_items = tree_articulos.selection()
        if not selected_items:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para eliminar.")
            return
        
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar el artículo seleccionado?"):
            for item in selected_items:
                tree_articulos.delete(item)
            messagebox.showinfo("Éxito", "Artículo eliminado de la lista. Guarde los cambios para confirmar.")

    def agregar_articulo_a_modificar():
        ventana_articulo = Toplevel(ventana_modificar)
        ventana_articulo.title("Agregar Artículo a Proveedor")
        ventana_articulo.geometry("350x300")
        
        ttk.Label(ventana_articulo, text="Nombre del Artículo").pack(pady=5)
        entrada_nombre_articulo = ttk.Entry(ventana_articulo)
        entrada_nombre_articulo.pack(pady=5)

        ttk.Label(ventana_articulo, text="Cantidad de Artículos").pack(pady=5)
        entrada_cantidad = ttk.Entry(ventana_articulo)
        entrada_cantidad.pack(pady=5)
        
        ttk.Label(ventana_articulo, text="Precio de Proveedor").pack(pady=5)
        entrada_precio_proveedor = ttk.Entry(ventana_articulo)
        entrada_precio_proveedor.pack(pady=5)

        ttk.Label(ventana_articulo, text="Precio Público").pack(pady=5)
        entrada_precio_publico = ttk.Entry(ventana_articulo)
        entrada_precio_publico.pack(pady=5)

        def guardar_articulo_temp():
            nombre_articulo = entrada_nombre_articulo.get().strip()
            try:
                cantidad = int(entrada_cantidad.get())
                precio_proveedor = float(entrada_precio_proveedor.get())
                precio_publico = float(entrada_precio_publico.get())
                if not all([nombre_articulo, cantidad >= 0, precio_proveedor >= 0, precio_publico >= 0]):
                    raise ValueError
            except ValueError:
                messagebox.showwarning("Advertencia", "Por favor, ingrese datos válidos en todos los campos.")
                return

            tree_articulos.insert('', 'end', values=(nombre_articulo, cantidad, precio_proveedor, precio_publico))
            ventana_articulo.destroy()
        
        ttk.Button(ventana_articulo, text="Guardar Artículo", command=guardar_articulo_temp, bootstyle="success").pack(pady=10)
        ttk.Button(ventana_articulo, text="Cancelar", command=ventana_articulo.destroy, bootstyle="danger").pack(pady=5)

    tree_articulos.bind("<Double-1>", editar_celda)

    def guardar_cambios():
        global proveedores, almacen
        
        nombre_nuevo = nombre_var.get().strip()
        telefono_nuevo = telefono_var.get().strip()
        if not nombre_nuevo or not telefono_nuevo:
            messagebox.showerror("Error", "El nombre y el teléfono son obligatorios.")
            return

        proveedor_original = next((p for p in proveedores if p.get("id") == proveedor.get("id")), None)
        if not proveedor_original:
            messagebox.showerror("Error", "No se encontró el proveedor original.")
            return

        proveedor_original["Nombre"] = nombre_nuevo
        proveedor_original["Teléfono"] = telefono_nuevo

        articulos_modificados = []
        adeudo_total_nuevo = 0.0

        for item_id in tree_articulos.get_children():
            values = tree_articulos.item(item_id, 'values')
            try:
                nombre_articulo = str(values[0]).strip()
                cantidad_nueva = int(values[1])
                precio_proveedor_val = float(values[2])
                precio_publico_val = float(values[3])

                if not nombre_articulo:
                    messagebox.showerror("Error", "El nombre del artículo no puede estar vacío.")
                    return

                articulo_modificado = {
                    "Nombre": nombre_articulo,
                    "Cantidad": cantidad_nueva,
                    "Precio Proveedor": precio_proveedor_val,
                    "Precio Público": precio_publico_val
                }
                articulos_modificados.append(articulo_modificado)
                
                adeudo_total_nuevo += cantidad_nueva * precio_proveedor_val
                
                # Sincronizar con almacén
                articulo_en_almacen = next((item for item in almacen if item.get("Nombre") == nombre_articulo), None)
                if articulo_en_almacen:
                    articulo_en_almacen["Stock"] = cantidad_nueva
                    articulo_en_almacen["Precio Público"] = precio_publico_val
                    articulo_en_almacen["Precio Compra"] = precio_proveedor_val
                else:
                    almacen.append({
                        "id": len(almacen) + 1,
                        "Nombre": nombre_articulo,
                        "Stock": cantidad_nueva,
                        "Precio Público": precio_publico_val,
                        "Precio Compra": precio_proveedor_val
                    })

            except (ValueError, IndexError):
                messagebox.showerror("Error", f"Revise los datos de la fila con el artículo '{values[0]}'. Algunos valores son inválidos.")
                return

        proveedor_original["Artículos Ingresados"] = articulos_modificados
        abonos_hechos = sum(a['Monto'] for a in proveedor_original.get("Abonos", []))
        proveedor_original["Adeudo Total"] = adeudo_total_nuevo - abonos_hechos
        
        guardar_datos(ARCHIVO_PROVEEDORES, proveedores)
        guardar_datos(ALMACEN_JSON, almacen)

        messagebox.showinfo("Éxito", "Proveedor modificado correctamente.")
        ventana_modificar.destroy()
        ver_proveedores()

    frame_botones = ttk.Frame(frame_principal)
    frame_botones.pack(fill="x", pady=10)
    ttk.Button(frame_botones, text="Añadir Artículo", bootstyle="info",
               command=agregar_articulo_a_modificar).pack(side="left", padx=5)
    ttk.Button(frame_botones, text="Guardar Cambios", bootstyle="success", command=guardar_cambios).pack(side="right", padx=5)
    ttk.Button(frame_botones, text="Eliminar Artículo", bootstyle="danger", command=eliminar_articulo).pack(side="right", padx=5)
    frame_botones = ttk.Frame(frame_principal)
    frame_botones.pack(fill="x", pady=10)
    ttk.Button(frame_botones, text="Eliminar Artículo", bootstyle="danger", command=eliminar_articulo).pack(side="left", padx=5)
    ttk.Button(frame_botones, text="Guardar Cambios", bootstyle="success", command=guardar_cambios).pack(side="right", padx=5)
    ttk.Button(frame_botones, text="Cancelar", bootstyle="secondary", command=ventana_modificar.destroy).pack(side="right", padx=5)
    
def exportar_excel():
    """Llama a la función de exportación de Excel con un nombre genérico."""
    exportar_excel_basico()


# Iniciar la aplicación
if __name__ == "__main__":
    proveedores = cargar_datos(ARCHIVO_PROVEEDORES)
    almacen = cargar_datos(ALMACEN_JSON)
    clientes = cargar_datos(ARCHIVO_CLIENTES)
    ventas = cargar_datos(VENTAS_JSON)
    menu_principal()
    root.mainloop()