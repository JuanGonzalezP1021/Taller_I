import csv
import datetime
import os
from abc import ABC, abstractmethod

# =============================================================================
# 1. CAPA DE SEGURIDAD (ENCAPSULAMIENTO)
# =============================================================================

class UsuarioMuseo:
    def __init__(self, username, password, rol):
        self.username = username
        self.__password = password  # Encapsulamiento
        self.rol = rol

    def validar_password(self, psw):
        return self.__password == psw

class AuthRepository:
    FILE = 'usuarios_museo.csv'

    @classmethod
    def inicializar(cls):
        if not os.path.exists(cls.FILE):
            with open(cls.FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['username', 'password', 'rol'])
                writer.writeheader()
                writer.writerows([
                    {'username': 'rodrigo_dir', 'password': '789', 'rol': 'Director'},
                    {'username': 'ana_rest', 'password': '456', 'rol': 'Restaurador'},
                    {'username': 'pepe_cat', 'password': '123', 'rol': 'Encargado'},
                    {'username': 'visitante_1', 'password': '000', 'rol': 'Visitante'}
                ])

    @classmethod
    def login(cls, user, psw):
        with open(cls.FILE, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                u = UsuarioMuseo(row['username'], row['password'], row['rol'])
                if u.username == user and u.validar_password(psw):
                    return u
        return None

# =============================================================================
# 2. MODELO DE DOMINIO (OBRAS DE ARTE)
# =============================================================================

class ObraDeArte(ABC):
    def __init__(self, id, titulo, autor, valor, f_entrada, estado="Expuesta"):
        self.id = id
        self.titulo = titulo
        self.autor = autor
        self.valor = float(valor)
        self.f_entrada = datetime.datetime.strptime(f_entrada, "%Y-%m-%d")
        self.estado = estado

    def necesita_restauracion(self):
        """Regla de negocio: 5 años = 1825 días."""
        delta = datetime.datetime.now() - self.f_entrada
        return delta.days >= 1825

class Cuadro(ObraDeArte):
    def __init__(self, id, titulo, autor, valor, f_ent, tecnica, estilo, estado):
        super().__init__(id, titulo, autor, valor, f_ent, estado)
        self.tecnica = tecnica
        self.estilo = estilo

class Escultura(ObraDeArte):
    def __init__(self, id, titulo, autor, valor, f_ent, material, estilo, estado):
        super().__init__(id, titulo, autor, valor, f_ent, estado)
        self.material = material
        self.estilo = estilo

# =============================================================================
# 3. REPOSITORIOS DE NEGOCIO
# =============================================================================

class MuseoRepository:
    FILE_CAT = 'catalogo_museo.csv'
    FILE_REST = 'restauraciones.csv'

    @classmethod
    def inicializar(cls):
        if not os.path.exists(cls.FILE_CAT):
            with open(cls.FILE_CAT, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=['id','titulo','autor','valor','f_entrada','tipo','detalle','estilo','estado'])
                w.writeheader()
                w.writerow({'id':'1', 'titulo':'La Noche Estrellada', 'autor':'Van Gogh', 'valor':'1000000', 'f_entrada':'2018-01-01', 'tipo':'Cuadro', 'detalle':'Oleo', 'estilo':'Post-impresionismo', 'estado':'Expuesta'})
                w.writerow({'id':'2', 'titulo':'El Pensador', 'autor':'Rodin', 'valor':'500000', 'f_entrada':'2020-05-15', 'tipo':'Escultura', 'detalle':'Bronce', 'estilo':'Moderna', 'estado':'Expuesta'})

    def cargar_todo(self):
        obras = []
        with open(self.FILE_CAT, 'r', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if r['tipo'] == 'Cuadro':
                    obras.append(Cuadro(r['id'], r['titulo'], r['autor'], r['valor'], r['f_entrada'], r['detalle'], r['estilo'], r['estado']))
                else:
                    obras.append(Escultura(r['id'], r['titulo'], r['autor'], r['valor'], r['f_entrada'], r['detalle'], r['estilo'], r['estado']))
        return obras

# =============================================================================
# 4. INTERFAZ DE USUARIO (MAIN)
# =============================================================================

def menu_director(usuario, repo):
    while True:
        print(f"\n--- PANEL DIRECTOR ({usuario.username}) ---")
        print("1. Consultar Valoración Total del Museo")
        print("2. Gestionar Cesiones a Museos Colaboradores")
        print("3. Salir")
        op = input("Opción: ")
        if op == "1":
            total = sum(o.valor for o in repo.cargar_todo())
            print(f"VALORACIÓN TOTAL PATRIMONIAL: ${total}")
        elif op == "3": break

def menu_restaurador(usuario, repo):
    while True:
        print(f"\n--- PANEL RESTAURADOR JEFE ---")
        print("1. Ver Obras que requieren restauración (Alerta 5 años)")
        print("2. Consultar Historial de Restauraciones")
        print("3. Salir")
        op = input("Opción: ")
        if op == "1":
            print("\nObras con mantenimiento preventivo vencido:")
            for o in repo.cargar_todo():
                if o.necesita_restauracion():
                    print(f"ALERTA: {o.titulo} de {o.autor} (Entrada: {o.f_entrada.date()})")
        elif op == "3": break

def menu_visitante(repo):
    print("\n--- MONITOR VESTÍBULO (LISTADO DE OBRAS) ---")
    for o in repo.cargar_todo():
        if o.estado == "Expuesta":
            print(f"SALA 1: {o.titulo} - Autor: {o.autor}")
    input("\nPresione Enter para continuar...")

def main():
    AuthRepository.inicializar()
    MuseoRepository.inicializar()
    
    print("=== SISTEMA MUSEO LASALLE - AUTENTICACIÓN ===")
    user = input("Usuario: ")
    psw = input("Contraseña: ")
    
    u = AuthRepository.login(user, psw)
    if u:
        repo = MuseoRepository()
        if u.rol == "Director": menu_director(u, repo)
        elif u.rol == "Restaurador": menu_restaurador(u, repo)
        elif u.rol == "Visitante": menu_visitante(repo)
    else:
        print("Acceso denegado.")

if __name__ == "__main__":
    main()