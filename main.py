# Librerías
import json
import os
import unicodedata
from openpyxl import Workbook  # Para generar el archivo Excel

# Mostrar la ruta donde se guardará el archivo# Mostrar la ruta donde se guardará el archivo
print(f"El archivo será guardado en: {os.getcwd()}")

# Funciones utilitarias
def load_data(file_name):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: El archivo {file_name} contiene datos inválidos.")
    return []

def save_data(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def normalize_string(s):
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8').replace(' ', '').upper()

# Archivos donde se almacenan los datos
DATA_FILE = 'clients.json'
ARTICLES_FILE = 'articulos.json'

# Funciones utilitarias
def load_data(file_name):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: El archivo {file_name} contiene datos inválidos.")
    return []

def save_data(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def normalize_string(s):
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode('utf-8').replace(' ', '').upper()

# Inicializar datos
clients = load_data(DATA_FILE)
articles = load_data(ARTICLES_FILE)

def initialize_articles():
    if not articles:
        articles.append({'codigo': 'A01', 'nombre': 'BOMBA DE AGUA', 'precio': 550.0})
        save_data(ARTICLES_FILE, articles)
        print('Artículos iniciales creados correctamente.')

initialize_articles()

# Exportar datos a Excel
def export_to_excel():
    print("Generando archivo Excel...")
    
    # Crear libro y hojas
    wb = Workbook()
    ws_clients = wb.active
    ws_clients.title = "Clientes y Ventas"
    ws_articles = wb.create_sheet(title="Artículos")

    # Agregar datos de clientes
    ws_clients.append(["UID", "Nombre Completo", "Teléfono", "Artículos", "Precio Total", "Saldo Pendiente", "Abonos"])
    for client in clients:
        abonos = ", ".join(map(str, client['abonos']))
        articulos = ", ".join(a['nombre'] for a in client['articulos'])
        ws_clients.append([
            client['uid'], client['nombre_completo'], client['telefono'], 
            articulos, client['precio_total'], client['saldo_pendiente'], abonos
        ])

    # Agregar datos de artículos
    ws_articles.append(["Código", "Nombre", "Precio"])
    for article in articles:
        ws_articles.append([article['codigo'], article['nombre'], article['precio']])

    # Guardar el archivo
    file_name = "exportacion_fome_ventas.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)
    wb.save(file_path)

    print(f"Archivo Excel generado correctamente: {file_path}")

# Gestión de artículos
def list_articles():
    print('Código | Artículo         | Precio')
    print('-' * 60)
    for article in articles:
        print(f"{article['codigo']:6} | {article['nombre'][:15]:15} | {article['precio']:6.2f}")

def add_article():
    print('Agregar un nuevo artículo:')
    codigo = f"A{len(articles) + 1:03d}"
    nombre = input('Nombre del artículo: ').strip().upper()
    while True:
        try:
            precio = float(input('Precio del artículo: ').strip())
            if precio <= 0:
                print("El precio debe ser un número positivo.")
                continue
            break
        except ValueError:
            print("Por favor, ingrese un número válido para el precio.")
    articles.append({'codigo': codigo, 'nombre': nombre, 'precio': precio})
    save_data(ARTICLES_FILE, articles)
    print(f"Artículo '{nombre}' agregado correctamente con el código '{codigo}' y precio {precio}.")

def delete_article():
    print('Eliminar un artículo:')
    list_articles()
    codigo = input('Ingrese el código del artículo que desea eliminar: ').strip().upper()
    article = next((a for a in articles if a['codigo'] == codigo), None)
    if article:
        articles.remove(article)
        save_data(ARTICLES_FILE, articles)
        print(f"Artículo con código '{codigo}' eliminado correctamente.")
    else:
        print(f"No se encontró el artículo con código '{codigo}'.")

def manage_articles():
    while True:
        print('[1] Listar artículos')
        print('[2] Agregar artículo')
        print('[3] Eliminar artículo')
        print('[0] Regresar al menú principal')
        choice = input('Elige una opción: ').strip()
        if choice == '1':
            list_articles()
        elif choice == '2':
            add_article()
        elif choice == '3':
            delete_article()
        elif choice == '0':
            break
        else:
            print('Opción no válida. Intenta de nuevo.')

# Gestión de clientes
def manage_clients():
    while True:
        print('[1] Registrar cliente')
        print('[2] Buscar cliente')
        print('[3] Eliminar cliente')
        print('[4] Agregar abono a cliente')
        print('[5] Ver clientes que han liquidado')
        print('[6] Exportar a Excel')
        print('[0] Regresar al menú principal')
        choice = input('Elige una opción: ').strip()

        if choice == '1':
            create_client()
        elif choice == '2':
            search_client()
        elif choice == '3':
            delete_client()
        elif choice == '4':
            add_abono()
        elif choice == '5':
            view_paid_clients()
        elif choice == '6':
            export_to_excel()
        elif choice == '0':
            break
        else:
            print('Opción no válida. Intenta de nuevo.')
# Función para listar clientes pagados
def view_paid_clients():
    print('CLIENTES QUE HAN LIQUIDADO SUS DEUDAS')
    print('-' * 60)

    paid_clients = [client for client in clients if client['saldo_pendiente'] <= 0]

    if not paid_clients:
        print("No hay clientes que hayan liquidado sus deudas.")
        return

    for client in paid_clients:
        total_abonos = sum(client['abonos'])
        print(f"Nombre: {client['nombre_completo']}")
        print(f"Teléfono: {client['telefono']}")
        print(f"Total de artículos: {len(client['articulos'])}")
        print(f"Total de abonos: {total_abonos:.2f}")
        print(f"Precio total de los artículos: {client['precio_total']:.2f}")
        print('-' * 60)

    print("Se ha mostrado la lista de clientes que no deben dinero.")

# Funciones para la gestión de clientes
def create_client():
    print('Registrar un nuevo cliente:')
    nombre_completo = input('Nombre completo: ').strip().upper()
    direccion = input('Dirección: ').strip().upper()

    while True:
        telefono = input('Teléfono (10 dígitos): ').strip()
        if telefono.isdigit() and len(telefono) == 10:
            break
        else:
            print('El teléfono debe tener 10 dígitos. Intenta de nuevo.')

    cliente_articulos = []
    while True:
        list_articles()
        while True:
            articulo_codigo = normalize_string(input('Ingrese el código del artículo: ').strip())
            articulo = next((a for a in articles if normalize_string(a['codigo']) == articulo_codigo), None)
            if not articulo:
                print('El código del artículo no existe. Intente de nuevo.')
            else:
                break

        precio = articulo['precio']
        cliente_articulos.append({'codigo': articulo_codigo, 'nombre': articulo['nombre'], 'precio': precio})

        another = input('¿Deseas agregar otro artículo? (S/N): ').strip().upper()
        if another != 'S':
            break

    total_precio = sum(item['precio'] for item in cliente_articulos)

    client = {
        'uid': len(clients) + 1,
        'nombre_completo': nombre_completo,
        'direccion': direccion,
        'telefono': telefono,
        'articulos': cliente_articulos,
        'precio_total': total_precio,
        'abonos': [],
        'saldo_pendiente': total_precio
    }
    clients.append(client)
    save_data(DATA_FILE, clients)
    print(f"Cliente '{nombre_completo}' registrado correctamente con {len(cliente_articulos)} artículo(s).")


def search_client():
    nombre_cliente = normalize_string(input('Nombre del cliente a buscar: '))
    matching_clients = [c for c in clients if normalize_string(c['nombre_completo']).startswith(nombre_cliente)]

    if not matching_clients:
        print(f"No se encontraron clientes con el nombre '{nombre_cliente}'.")
    else:
        print(f"Se encontraron {len(matching_clients)} cliente(s) con el nombre '{nombre_cliente}':")
        for client in matching_clients:
            print(f"UID: {client['uid']}, Nombre completo: {client['nombre_completo']}, Teléfono: {client['telefono']}, "
                  f"Artículos: {', '.join(item['nombre'] for item in client['articulos'])}, "
                  f"Precio total: {client['precio_total']}, Saldo pendiente: {client['saldo_pendiente']}")

def delete_client():
    nombre_cliente = normalize_string(input('Nombre del cliente a eliminar: '))
    global clients
    client = next((c for c in clients if normalize_string(c['nombre_completo']) == nombre_cliente), None)

    if not client:
        print(f"Cliente '{nombre_cliente}' no encontrado.")
        return

    clients = [c for c in clients if normalize_string(c['nombre_completo']) != nombre_cliente]
    save_data(DATA_FILE, clients)
    print(f"Cliente '{client['nombre_completo']}' eliminado correctamente.")

def add_abono():
    nombre_cliente = normalize_string(input('Nombre del cliente: '))
    client = next((c for c in clients if normalize_string(c['nombre_completo']) == nombre_cliente), None)

    if not client:
        print(f"Cliente '{nombre_cliente}' no encontrado.")
        return

    while True:
        try:
            abono = float(input(f"Ingrese el abono para {client['nombre_completo']}: ").strip())
            if abono <= 0:
                print("El abono debe ser un monto positivo.")
                continue
            break
        except ValueError:
            print("Por favor, ingrese un número válido para el abono.")

    client['abonos'].append(abono)
    client['saldo_pendiente'] -= abono
    save_data(DATA_FILE, clients)
    print(f"Abono de {abono} registrado correctamente. Saldo pendiente: {client['saldo_pendiente']}.")


# Gestión de clientes
def view_client_balances():
    if not clients:
        print("No hay clientes registrados.")
        return

    print('BALANCES DE CLIENTES')
    print('-' * 60)
    total_abonos = 0
    total_saldo_pendiente = 0
    for client in clients:
        total_abonos += sum(client['abonos'])
        total_saldo_pendiente += client['saldo_pendiente']
        print(f"Nombre: {client['nombre_completo']}")
        print(f"Total a pagar: {client['precio_total']}")
        print(f"Abonos realizados: {sum(client['abonos'])}")
        print(f"Saldo pendiente: {client['saldo_pendiente']}")
        print('-' * 60)

    print(f"TOTAL ABONOS: {total_abonos:.2f}")
    print(f"TOTAL SALDO PENDIENTE: {total_saldo_pendiente:.2f}")

def view_total_articles_sold():
    if not clients:
        print("No hay clientes registrados.")
        return

    total_sales = {}
    total_vendido = 0
    total_abonos = 0
    total_saldo_pendiente = 0

    for client in clients:
        total_abonos += sum(client['abonos'])
        total_saldo_pendiente += client['saldo_pendiente']
        for article in client['articulos']:
            codigo = article['codigo']
            if codigo not in total_sales:
                total_sales[codigo] = {'nombre': article['nombre'], 'cantidad': 0, 'total_precio': 0.0}
            total_sales[codigo]['cantidad'] += 1
            total_sales[codigo]['total_precio'] += article['precio']
            total_vendido += article['precio']

    print('TOTAL DE ARTÍCULOS VENDIDOS')
    print('-' * 60)
    print('Código | Artículo          | Cantidad | Total vendido')
    print('-' * 60)
    for codigo, data in total_sales.items():
        print(f"{codigo:6} | {data['nombre'][:15]:15} | {data['cantidad']:8} | {data['total_precio']:12.2f}")

    print('-' * 60)
    print(f"TOTAL VENDIDO: {total_vendido:.2f}")
    print(f"TOTAL ABONADO: {total_abonos:.2f}")
    print(f"TOTAL PENDIENTE: {total_saldo_pendiente:.2f}")

# Menú principal
def main():
    while True:
        print('BIENVENIDO A FOME-VENTAS')
        print('¿QUE ARAS EL DIA DE HOY?')
        print('[C] Cliente')
        print('[A] Administrar artículos')
        print('[B] Ver balances de clientes')
        print('[T] Ver total de artículos vendidos')
        print('[E] Salir')
        choice = input('Elige una opción: ').strip().upper()
        if choice == 'C':
            manage_clients()
        elif choice == 'A':
            manage_articles()
        elif choice == 'B':
            view_client_balances()
        elif choice == 'T':
            view_total_articles_sold()
        elif choice == 'E':
            print('Gracias por utilizar FOME-VENTAS. ¡Hasta luego!')
            break
        else:
            print('Opción no válida. Intenta de nuevo.')

if __name__ == "__main__":
    main()







