import csv
import datetime
import os

# =============================================================================
# 1. CAPA DE SEGURIDAD Y MODELADO (ENCAPSULAMIENTO)
# =============================================================================

class Usuario:
    """
    Representa a un usuario del sistema.
    Aplica el principio de Encapsulamiento al proteger la contraseña.
    """
    def __init__(self, username, password, rol, email, suscripcion="NO"):
        self.username = username
        self.__password = password  # Atributo Privado
        self.rol = rol
        self.email = email
        self.suscripcion = suscripcion

    def validar_acceso(self, password_ingresado):
        """Valida si el password ingresado coincide con el privado."""
        return self.__password == password_ingresado

# =============================================================================
# 2. CAPA DE PERSISTENCIA (REPOSITORIOS)
# =============================================================================

class UsuarioRepository:
    """Gestiona el acceso y modificación del archivo usuarios.csv"""
    FILE = 'usuarios.csv'

    @classmethod
    def inicializar(cls):
        if not os.path.exists(cls.FILE):
            with open(cls.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['username', 'password', 'rol', 'email', 'suscripcion'])
                writer.writeheader()
                # Usuarios por defecto para pruebas
                writer.writerow({'username': 'juan_cliente', 'password': '123', 'rol': 'Cliente', 'email': 'juan@mail.com', 'suscripcion': 'NO'})
                writer.writerow({'username': 'pedro_agente', 'password': '456', 'rol': 'Agente', 'email': 'pedro@mail.com', 'suscripcion': 'NO'})
                writer.writerow({'username': 'marta_gerente', 'password': '789', 'rol': 'Gerente', 'email': 'marta@mail.com', 'suscripcion': 'NO'})

    @classmethod
    def buscar(cls, username):
        with open(cls.FILE, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                if row['username'] == username:
                    return Usuario(row['username'], row['password'], row['rol'], row['email'], row['suscripcion'])
        return None

    @classmethod
    def actualizar_suscripcion(cls, username, estado):
        filas, ok = [], False
        with open(cls.FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['username'] == username:
                    row['suscripcion'] = estado
                    ok = True
                filas.append(row)
        if ok:
            with open(cls.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(filas)
        return ok

class InventarioRepository:
    """Gestiona el sistema de stock externo (inventario_sistema.csv)"""
    FILE = 'inventario_sistema.csv'

    @classmethod
    def inicializar(cls):
        if not os.path.exists(cls.FILE):
            with open(cls.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['codigo', 'descripcion', 'precio', 'stock'])
                writer.writeheader()
                writer.writerow({'codigo': '101', 'descripcion': 'Televisor 50"', 'precio': '1500.0', 'stock': '10'})
                writer.writerow({'codigo': '102', 'descripcion': 'Audífonos BT', 'precio': '80.0', 'stock': '50'})
                writer.writerow({'codigo': '103', 'descripcion': 'Consola Gaming', 'precio': '500.0', 'stock': '5'})

    def listar_todo(self):
        with open(self.FILE, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def consultar(self, codigo):
        for prod in self.listar_todo():
            if prod['codigo'] == str(codigo): return prod
        return None

    def descontar_stock(self, codigo, cantidad):
        filas, ok = [], False
        with open(self.FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['codigo'] == str(codigo):
                    stock_act = int(row['stock'])
                    if stock_act >= cantidad:
                        row['stock'] = str(stock_act - cantidad)
                        ok = True
                filas.append(row)
        if ok:
            with open(self.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(filas)
        return ok

class PedidoRepository:
    """Gestiona las órdenes de compra (pedidos.csv)"""
    FILE = 'pedidos.csv'

    @classmethod
    def inicializar(cls):
        if not os.path.exists(cls.FILE):
            with open(cls.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'cliente', 'total', 'estado', 'transportadora'])
                writer.writeheader()

    def registrar(self, cliente, total):
        ped_id = datetime.datetime.now().strftime("%S%f")[:4]
        with open(self.FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([ped_id, cliente, total, 'Confirmada', 'N/A'])
        return ped_id

    def listar_todos(self):
        with open(self.FILE, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def cancelar(self, ped_id, cliente):
        filas, msg, exito = [], "Pedido no encontrado.", False
        with open(self.FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for r in reader:
                if r['id'] == str(ped_id) and r['cliente'] == cliente:
                    if r['estado'] == 'Enviado':
                        msg = "Error: El pedido ya fue enviado y no puede cancelarse."
                    else:
                        r['estado'] = 'Cancelada'
                        exito = True
                        msg = "Pedido cancelado exitosamente."
                filas.append(r)
        if exito:
            with open(self.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader(); writer.writerows(filas)
        return msg

    def despachar(self, ped_id, transportadora):
        filas, ok = [], False
        with open(self.FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for r in reader:
                if r['id'] == str(ped_id) and r['estado'] == 'Confirmada':
                    r['estado'], r['transportadora'] = 'Enviado', transportadora
                    ok = True
                filas.append(r)
        if ok:
            with open(self.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader(); writer.writerows(filas)
        return ok

class QuejaRepository:
    """Gestiona el buzón de quejas (quejas.csv)"""
    FILE = 'quejas.csv'

    @classmethod
    def inicializar(cls):
        if not os.path.exists(cls.FILE):
            with open(cls.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['cliente', 'motivo', 'fecha'])

    def registrar(self, cliente, motivo):
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.FILE, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([cliente, motivo, fecha])

# =============================================================================
# 3. INTERFAZ DE USUARIO (MAIN)
# =============================================================================

def menu_cliente(usuario):
    repo_inv = InventarioRepository()
    repo_ped = PedidoRepository()
    while True:
        print(f"\n--- MENÚ CLIENTE ({usuario.username}) ---")
        print("1. Consultar Catálogo")
        print("2. Suscribirse/Cancelar Suscripción Catálogo")
        print("3. Realizar Orden de Compra (Tarjeta de Crédito)")
        print("4. Cancelar Orden de Compra")
        print("5. Presentar Queja")
        print("6. Salir")
        op = input("Opción: ")

        if op == "1":
            print(f"\n{'ID':<5} | {'DESCRIPCIÓN':<20} | {'PRECIO':<10} | {'STOCK'}")
            for p in repo_inv.listar_todo():
                print(f"{p['codigo']:<5} | {p['descripcion']:<20} | {p['precio']:<10} | {p['stock']}")

        elif op == "2":
            nuevo = "SI" if usuario.suscripcion == "NO" else "NO"
            if UsuarioRepository.actualizar_suscripcion(usuario.username, nuevo):
                usuario.suscripcion = nuevo
                print(f"Suscripción actualizada a: {nuevo}")

        elif op == "3":
            cod = input("ID del producto a comprar: ")
            prod = repo_inv.consultar(cod)
            if prod:
                pid = repo_ped.registrar(usuario.username, prod['precio'])
                print(f"Orden #{pid} generada. El cargo se realizará a su TARJETA registrada.")
            else: print("Error: Producto no encontrado.")

        elif op == "4":
            pid = input("ID de la orden a cancelar: ")
            print(repo_ped.cancelar(pid, usuario.username))

        elif op == "5":
            motivo = input("Motivo de la queja: ")
            QuejaRepository().registrar(usuario.username, motivo)
            print("Queja enviada inmediatamente al Gerente.")

        elif op == "6": break

def menu_agente(usuario):
    repo_ped = PedidoRepository()
    repo_inv = InventarioRepository()
    while True:
        print(f"\n--- MENÚ AGENTE ({usuario.username}) ---")
        print("1. Listar Órdenes Confirmadas")
        print("2. Despachar Pedido (Logística)")
        print("3. Salir")
        op = input("Opción: ")

        if op == "1":
            for p in repo_ped.listar_todos():
                if p['estado'] == 'Confirmada': print(p)

        elif op == "2":
            pid = input("ID del pedido para armar: ")
            transporte = {"1":"Servientrega", "2":"Envia", "3":"Fedex"}.get(input("Transportadora (1.Servientrega, 2.Envia, 3.Fedex): "), "N/A")
            # En un sistema real, aquí buscaríamos el producto asociado al pedido para descontar stock
            if repo_inv.descontar_stock(101, 1): # Simulación lógica de descuento
                if repo_ped.despachar(pid, transporte):
                    print(f"Pedido #{pid} empaquetado y enviado vía {transporte}.")
                else: print("Error al actualizar pedido.")
            else: print("Error: Stock insuficiente.")

        elif op == "3": break

def menu_gerente(usuario):
    while True:
        print(f"\n--- PANEL SUPER USUARIO (GERENTE: {usuario.username}) ---")
        print("1. Ver Inventario Completo")
        print("2. Ver Historial Logístico de Pedidos")
        print("3. Ver Buzón de Quejas")
        print("4. Salir")
        op = input("Opción: ")

        if op == "1":
            with open('inventario_sistema.csv', 'r') as f: print(f.read())
        elif op == "2":
            with open('pedidos.csv', 'r') as f: print(f.read())
        elif op == "3":
            with open('quejas.csv', 'r') as f: print(f.read())
        elif op == "4": break

def main():
    # Inicializar base de datos CSV
    UsuarioRepository.inicializar()
    InventarioRepository.inicializar()
    PedidoRepository.inicializar()
    QuejaRepository.inicializar()

    print("=== TELEVENTAS LASALLE - SISTEMA INTEGRAL ===")
    user = input("Usuario: ")
    psw = input("Contraseña: ")

    usuario = UsuarioRepository.buscar(user)
    if usuario and usuario.validar_acceso(psw):
        if usuario.rol == "Cliente": menu_cliente(usuario)
        elif usuario.rol == "Agente": menu_agente(usuario)
        elif usuario.rol == "Gerente": menu_gerente(usuario)
    else:
        print("Credenciales inválidas.")

if __name__ == "__main__":
    main()