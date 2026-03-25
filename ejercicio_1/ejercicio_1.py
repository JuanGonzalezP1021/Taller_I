import csv
import datetime

# --- CAPA DE PERSISTENCIA (REPOSITORIOS) ---

class PedidoRepository:
    def __init__(self, archivo="pedidos.csv"):
        self.archivo = archivo

    def registrar_pedido(self, numero, cliente, total):
        with open(self.archivo, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Estado inicial: Pendiente | Transportadora: N/A
            writer.writerow([numero, cliente, total, "Pendiente", "N/A"])

    def obtener_pendientes(self):
        pendientes = []
        with open(self.archivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['estado'] == "Pendiente":
                    pendientes.append(row)
        return pendientes

    def despachar_pedido(self, numero_pedido, empresa_transporte):
        filas = []
        actualizado = False
        with open(self.archivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['numero'] == str(numero_pedido):
                    row['estado'] = "Enviado"
                    row['transportadora'] = empresa_transporte
                    actualizado = True
                filas.append(row)
        
        if actualizado:
            with open(self.archivo, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(filas)
        return actualizado

# --- CLASES DE LÓGICA (TUS CLASES ORIGINALES) ---

class InventarioExterno:
    def __init__(self, archivo_csv="inventario_sistema.csv"):
        self.archivo = archivo_csv

    def consultar_detalles(self, codigo):
        try:
            with open(self.archivo, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['codigo']) == codigo:
                        return row
        except FileNotFoundError: return None
        return None

    def actualizar_stock(self, codigo, cantidad):
        filas, actualizado = [], False
        with open(self.archivo, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if int(row['codigo']) == codigo:
                    stock_act = int(row['stock'])
                    if stock_act >= cantidad:
                        row['stock'] = str(stock_act - cantidad)
                        actualizado = True
                filas.append(row)
        if actualizado:
            with open(self.archivo, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader(); writer.writerows(filas)
        return actualizado

class Cliente:
    def __init__(self, nombre):
        self.nombre = nombre

    def presentar_queja(self, motivo):
        with open('quejas.csv', mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([self.nombre, motivo, datetime.datetime.now()])
        print("Queja enviada al Gerente de Relaciones.")

# --- MAIN CON 3 ROLES Y MENÚS ---

if __name__ == "__main__":
    # Simulación de login simple para el video
    print("=== TELEVENTAS LASALLE - LOGIN ===")
    user = input("Usuario: ")
    psw = input("Password: ")
    
    # Roles: 'Cliente', 'Agente', 'Gerente'
    # (Para el video, asume que 'juan' es Cliente, 'pedro' es Agente, 'marta' es Gerente)
    rol = ""
    if user == "juan": rol = "Cliente"
    elif user == "pedro": rol = "Agente"
    elif user == "marta": rol = "Gerente"

    if not rol:
        print("Usuario no reconocido.")
    else:
        repo_pedidos = PedidoRepository()
        inv = InventarioExterno()

        if rol == "Cliente":
            print(f"\n--- MENÚ CLIENTE ({user}) ---")
            print("1. Realizar Compra\n2. Registrar Queja")
            op = input("Seleccione: ")
            if op == "1":
                cod = int(input("ID Producto: "))
                item = inv.consultar_detalles(cod)
                if item:
                    # Modelo matemático: T = p * q
                    total = float(item['precio'])
                    repo_pedidos.registrar_pedido(1001, user, total)
                    print(f"Pedido #1001 generado por ${total}. Estado: Pendiente.")
                else: print("Producto no encontrado.")
            elif op == "2":
                msg = input("Motivo de queja: ")
                Cliente(user).presentar_queja(msg)

        elif rol == "Agente":
            print(f"\n--- MENÚ BODEGA ({user}) ---")
            pendientes = repo_pedidos.obtener_pendientes()
            if pendientes:
                print("Pedidos para armar:")
                for p in pendientes:
                    print(f"ID: {p['numero']} | Cliente: {p['cliente']} | Total: {p['total']}")
                
                id_despacho = input("\nIngrese ID para armar y despachar: ")
                # Requerimiento: Seleccionar empresa de transporte
                empresa = input("Seleccione Empresa de Transporte (Servientrega/Fedex): ")
                
                # Descontar stock (Requerimiento 3.2)
                if inv.actualizar_stock(101, 1): # Ejemplo con prod 101
                    repo_pedidos.despachar_pedido(id_despacho, empresa)
                    print(f"Pedido {id_despacho} empaquetado y enviado vía {empresa}.")
            else:
                print("No hay pedidos pendientes.")

        elif rol == "Gerente":
            print(f"\n--- PANEL GERENCIAL ---")
            print("1. Ver Historial de Quejas\n2. Ver Todos los Pedidos")
            # Aquí podrías leer los CSVs correspondientes
            print("Mostrando reportes de trazabilidad...")