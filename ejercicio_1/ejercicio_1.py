import csv
import datetime
import os

# --- CAPA DE SEGURIDAD Y DATOS ---

class Usuario:
    def __init__(self, username, password, rol, email, suscripcion):
        self.username = username
        self.__password = password # Encapsulamiento
        self.rol = rol
        self.email = email
        self.suscripcion = suscripcion

    def validar_password(self, psw):
        return self.__password == psw

class UsuarioRepository:
    @staticmethod
    def login(user, psw):
        if not os.path.exists('usuarios.csv'): return None
        with open('usuarios.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = Usuario(row['username'], row['password'], row['rol'], row['email'], row['suscripcion'])
                if u.username == user and u.validar_password(psw):
                    return u
        return None

    @staticmethod
    def cambiar_suscripcion(username, estado="SI"):
        filas, ok = [], False
        with open('usuarios.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['username'] == username:
                    row['suscripcion'] = estado
                    ok = True
                filas.append(row)
        if ok:
            with open('usuarios.csv', mode='w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader(); writer.writerows(filas)
        return ok

class PedidoRepository:
    def __init__(self, archivo="pedidos.csv"):
        self.archivo = archivo

    def crear(self, num, cliente, total):
        with open(self.archivo, mode='a', newline='') as f:
            csv.writer(f).writerow([num, cliente, total, "Confirmada", "N/A"])

    def listar(self):
        with open(self.archivo, mode='r') as f: return list(csv.DictReader(f))

    def intentar_cancelar(self, num_pedido):
        """Regla de Negocio: Solo cancela si NO ha sido enviada."""
        filas, mensaje = [], "Orden no encontrada."
        exito = False
        with open(self.archivo, mode='r') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for r in reader:
                if r['numero'] == str(num_pedido):
                    if r['estado'] == "Enviado":
                        mensaje = "Error: El pedido ya fue enviado y no puede cancelarse."
                    else:
                        r['estado'] = "Cancelada"
                        exito = True
                        mensaje = f"Orden {num_pedido} cancelada exitosamente."
                filas.append(r)
        
        if exito:
            with open(self.archivo, mode='w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader(); writer.writerows(filas)
        return exito, mensaje

    def despachar(self, num, transporte):
        filas, ok = [], False
        with open(self.archivo, mode='r') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for r in reader:
                if r['numero'] == str(num) and r['estado'] == "Confirmada":
                    r['estado'], r['transportadora'] = "Enviado", transporte
                    ok = True
                filas.append(r)
        if ok:
            with open(self.archivo, mode='w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader(); writer.writerows(filas)
        return ok

# --- MAIN (FLUJO POR PERFILES) ---

if __name__ == "__main__":
    print("=== TELEVENTAS LASALLE - SISTEMA V1.2 ===")
    u_log, p_log = input("Usuario: "), input("Password: ")
    usuario_act = UsuarioRepository.login(u_log, p_log)

    if not usuario_act:
        print("Credenciales inválidas.")
    else:
        print(f"\nSESIÓN INICIADA: {usuario_act.username} ({usuario_act.rol})")
        repo_ped = PedidoRepository()
        
        while True:
            # --- CLIENTE ---
            if usuario_act.rol == "Cliente":
                print("\n1. Comprar\n2. Gestionar Suscripción\n3. Cancelar Orden\n4. Salir")
                op = input("Opción: ")
                
                if op == "2":
                    print(f"Estado actual: {usuario_act.suscripcion}")
                    sub_op = input("1. Suscribirse\n2. Cancelar Suscripción\nSeleccione: ")
                    nuevo_est = "SI" if sub_op == "1" else "NO"
                    if UsuarioRepository.cambiar_suscripcion(usuario_act.username, nuevo_est):
                        usuario_act.suscripcion = nuevo_est # Actualizar objeto en memoria
                        print(f"Suscripción actualizada a: {nuevo_est}")
                
                elif op == "3":
                    num = input("Número de orden a cancelar: ")
                    ok, msg = repo_ped.intentar_cancelar(num)
                    print(msg)
                
                elif op == "4": break

            # --- AGENTE ---
            elif usuario_act.rol == "Agente":
                print("\n1. Ver Pendientes\n2. Despachar\n3. Salir")
                op = input("Opción: ")
                if op == "2":
                    num = input("ID Pedido: ")
                    trans = input("Transportadora (Servientrega/Envia/Fedex): ")
                    if repo_ped.despachar(num, trans):
                        print("Pedido enviado. Ya no podrá ser cancelado por el cliente.")
                elif op == "3": break
            
            elif usuario_act.rol == "Gerente": break