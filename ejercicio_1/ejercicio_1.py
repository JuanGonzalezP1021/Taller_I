import csv
import datetime
import os

# Configuración de rutas dinámicas para asegurar que el sistema trabaje dentro de la carpeta del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    """Construye la ruta absoluta para los archivos de datos dentro de la carpeta del ejercicio."""
    return os.path.join(BASE_DIR, filename)

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
        self.__password = password  # Atributo Privado (Encapsulamiento)
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
    FILE = get_path('usuarios.csv')

    @classmethod
    def inicializar(cls):
        """Crea el archivo con datos base solo si no existe físicamente."""
        if not os.path.exists(cls.FILE):
            with open(cls.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['username', 'password', 'rol', 'email', 'suscripcion'])
                writer.writeheader()
                writer.writerows([
                    {'username': 'juan_cliente', 'password': '123', 'rol': 'Cliente', 'email': 'juan@mail.com', 'suscripcion': 'NO'},
                    {'username': 'pedro_agente', 'password': '456', 'rol': 'Agente', 'email': 'pedro@mail.com', 'suscripcion': 'NO'},
                    {'username': 'marta_gerente', 'password': '789', 'rol': 'Gerente', 'email': 'marta@mail.com', 'suscripcion': 'NO'}
                ])

    @classmethod
    def buscar(cls, username):
        if not os.path.exists(cls.FILE): cls.inicializar()
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
    FILE = get_path('inventario_sistema.csv')

    @classmethod
    def inicializar(cls):
        if not os.path.exists(cls.FILE):
            with open(cls.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['codigo', 'descripcion', 'precio', 'stock'])
                writer.writeheader()
                writer.writerows([
                    {'codigo': '101', 'descripcion': 'Televisor 50" UHD', 'precio': '1500.0', 'stock': '10'},
                    {'codigo': '102', 'descripcion': 'Audífonos BT', 'precio': '80.0', 'stock': '50'},
                    {'codigo': '103', 'descripcion': 'Consola Gaming', 'precio': '500.0', 'stock': '5'}
                ])

    def listar_todo(self):
        if not os.path.exists(self.FILE): self.inicializar()
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
    FILE = get_path('pedidos.csv')

    @classmethod
    def inicializar(cls):
        if not os.path.exists(cls.FILE):
            with open(cls.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['id', 'cliente', 'total', 'estado', 'transportadora'])
                writer.writeheader()

    def registrar(self, cliente, total):
        if not os.path.exists(self.FILE): self.inicializar()
        ped_id = datetime.datetime.now().strftime("%S%f")[:4]
        with open(self.FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([ped_id, cliente, total, 'Confirmada', 'N/A'])
        return ped_id

    def listar_todos(self):
        if not os.path.exists(self.FILE): self.inicializar()
        with open(self.FILE, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    def cancelar(self, ped_id, cliente):
        """Solo permite cancelar si el estado no es 'Enviado'."""
        filas, msg, exito = [], "Pedido no encontrado.", False
        with open(self.FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for r in reader:
                if r['id'] == str(ped_id) and r['cliente'] == cliente:
                    if r['estado'] == 'Enviado':
                        msg = "ERROR: El pedido ya fue enviado y no puede cancelarse."
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
    FILE = get_path('quejas.csv')

    @classmethod
    def inicializar(cls):
        if not os.path.exists(cls.FILE):
            with open(cls.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['cliente', 'motivo', 'fecha'])

    def registrar(self, cliente, motivo):
        if not os.path.exists(self.FILE): self.inicializar()
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
        print("2. Suscribirse/Cancelar Suscripción")
        print("3. Comprar Producto (Cargo a Tarjeta)")
        print("4. Cancelar Orden")
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
            cod = input("ID del producto: ")
            prod = repo_inv.consultar(cod)
            if prod:
                pid = repo_ped.registrar(usuario.username, prod['precio'])
                print(f"Orden #{pid} generada. Cargo automático realizado a su TARJETA.")
            else: print("Error: Producto no encontrado.")

        elif op == "4":
            pid = input("ID de la orden: ")
            print(repo_ped.cancelar(pid, usuario.username))

        elif op == "5":
            QuejaRepository().registrar(usuario.username, input("Motivo: "))
            print("Queja remitida al Gerente.")

        elif op == "6": break

def menu_agente(usuario):
    repo_ped = PedidoRepository()
    repo_inv = InventarioRepository()
    while True:
        print(f"\n--- PANEL AGENTE ({usuario.username}) ---")
        print("1. Ver Órdenes Confirmadas")
        print("2. Despachar Pedido (Selección Logística)")
        print("3. Salir")
        op = input("Opción: ")

        if op == "1":
            for p in repo_ped.listar_todos():
                if p['estado'] == 'Confirmada': print(p)

        elif op == "2":
            pid = input("ID del pedido: ")
            print("Seleccione Logística: 1.Servientrega 2.Envia 3.Fedex")
            trans = {"1":"Servientrega", "2":"Envia", "3":"Fedex"}.get(input("Opción: "), "N/A")
            # Actualización de stock basada en el primer producto por simplicidad del ejercicio
            if repo_inv.descontar_stock(101, 1): 
                if repo_ped.despachar(pid, trans):
                    print(f"Pedido {pid} enviado vía {trans}.")
                else: print("No se pudo actualizar el pedido.")
            else: print("Error de stock.")

        elif op == "3": break

def menu_gerente(usuario):
    while True:
        print(f"\n--- PANEL GERENCIAL (SUPER USUARIO: {usuario.username}) ---")
        print("1. Ver Inventario Completo")
        print("2. Ver Historial de Pedidos")
        print("3. Ver Buzón de Quejas")
        print("4. Salir")
        op = input("Opción: ")

        if op == "1":
            with open(InventarioRepository.FILE, 'r', encoding='utf-8') as f: print(f.read())
        elif op == "2":
            with open(PedidoRepository.FILE, 'r', encoding='utf-8') as f: print(f.read())
        elif op == "3":
            if os.path.exists(QuejaRepository.FILE):
                with open(QuejaRepository.FILE, 'r', encoding='utf-8') as f: print(f.read())
        elif op == "4": break

def main():
    try:
        # Los métodos de inicialización solo crearán archivos si NO los detectan en la carpeta
        UsuarioRepository.inicializar()
        InventarioRepository.inicializar()
        PedidoRepository.inicializar()
        QuejaRepository.inicializar()

        print("=== TELEVENTAS LASALLE - SISTEMA INTEGRAL ===")
        user = input("Usuario: ")
        psw = input("Contraseña: ")

        u = UsuarioRepository.buscar(user)
        if u and u.validar_acceso(psw):
            print(f"\nAcceso como: {u.rol}")
            if u.rol == "Cliente": menu_cliente(u)
            elif u.rol == "Agente": menu_agente(u)
            elif u.rol == "Gerente": menu_gerente(u)
        else:
            print("Credenciales inválidas.")
    except Exception as e:
        print(f"Error crítico: {e}")

if __name__ == "__main__":
    main()