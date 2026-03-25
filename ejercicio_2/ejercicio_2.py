import csv
import datetime
import os
from abc import ABC, abstractmethod

# Configuración de rutas dinámicas para evitar errores de carpeta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(filename):
    """Retorna la ruta absoluta del archivo dentro de la carpeta del ejercicio."""
    return os.path.join(BASE_DIR, filename)

# =============================================================================
# 1. CAPA DE SEGURIDAD (ENCAPSULAMIENTO)
# =============================================================================

class UsuarioMuseo:
    def __init__(self, username, password, rol):
        self.username = username
        self.__password = password  # Atributo Privado (Encapsulamiento)
        self.rol = rol

    def validar_password(self, psw):
        """Valida la contraseña sin exponer el atributo privado."""
        return self.__password == psw

class AuthRepository:
    FILE = get_path('usuarios_museo.csv')

    @classmethod
    def inicializar(cls):
        """Crea el archivo de usuarios si no existe."""
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
        """Valida credenciales contra el archivo CSV."""
        if not os.path.exists(cls.FILE):
            cls.inicializar()
        try:
            with open(cls.FILE, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f):
                    u = UsuarioMuseo(row['username'], row['password'], row['rol'])
                    if u.username == user and u.validar_password(psw):
                        return u
        except Exception as e:
            print(f"Error en autenticación: {e}")
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

class ObjetoOtro(ObraDeArte):
    def __init__(self, id, titulo, autor, valor, f_ent, descripcion, estado):
        super().__init__(id, titulo, autor, valor, f_ent, estado)
        self.descripcion = descripcion

# =============================================================================
# 3. REPOSITORIOS DE NEGOCIO (BACK-END)
# =============================================================================

class MuseoRepository:
    FILE_CAT = get_path('catalogo_museo.csv')
    FILE_REST = get_path('restauraciones.csv')
    FILE_MUSEOS = get_path('museos_colaboradores.csv')

    @classmethod
    def inicializar(cls):
        """Inicializa los archivos de datos si no existen."""
        if not os.path.exists(cls.FILE_CAT):
            with open(cls.FILE_CAT, 'w', newline='', encoding='utf-8') as f:
                w = csv.DictWriter(f, fieldnames=['id','titulo','autor','valor','f_entrada','tipo','detalle','estilo','estado'])
                w.writeheader()
                w.writerow({'id':'1', 'titulo':'La Noche Estrellada', 'autor':'Van Gogh', 'valor':'1000000', 'f_entrada':'2018-01-01', 'tipo':'Cuadro', 'detalle':'Oleo', 'estilo':'Post-impresionismo', 'estado':'Expuesta'})
                w.writerow({'id':'2', 'titulo':'El Pensador', 'autor':'Rodin', 'valor':'500000', 'f_entrada':'2020-05-15', 'tipo':'Escultura', 'detalle':'Bronce', 'estilo':'Moderna', 'estado':'Expuesta'})
        
        if not os.path.exists(cls.FILE_REST):
            with open(cls.FILE_REST, 'w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(['id_obra', 'tipo', 'fecha_inicio', 'fecha_fin'])

    def cargar_todo(self):
        obras = []
        if not os.path.exists(self.FILE_CAT): self.inicializar()
        with open(self.FILE_CAT, 'r', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                if r['tipo'] == 'Cuadro':
                    obras.append(Cuadro(r['id'], r['titulo'], r['autor'], r['valor'], r['f_entrada'], r['detalle'], r['estilo'], r['estado']))
                elif r['tipo'] == 'Escultura':
                    obras.append(Escultura(r['id'], r['titulo'], r['autor'], r['valor'], r['f_entrada'], r['detalle'], r['estilo'], r['estado']))
                else:
                    obras.append(ObjetoOtro(r['id'], r['titulo'], r['autor'], r['valor'], r['f_entrada'], r['detalle'], r['estado']))
        return obras

    def registrar_restauracion(self, id_obra, tipo):
        """Registra una nueva restauración y cambia el estado de la obra."""
        with open(self.FILE_REST, 'a', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow([id_obra, tipo, datetime.date.today(), 'Pendiente'])
        
        # Actualizar estado en catálogo
        obras = self.cargar_todo()
        with open(self.FILE_CAT, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=['id','titulo','autor','valor','f_entrada','tipo','detalle','estilo','estado'])
            w.writeheader()
            for o in obras:
                estado = 'En Restauracion' if o.id == id_obra else o.estado
                # Mapeo de vuelta a dict
                w.writerow({'id':o.id, 'titulo':o.titulo, 'autor':o.autor, 'valor':o.valor, 'f_entrada':o.f_entrada.strftime("%Y-%m-%d"), 'tipo':type(o).__name__, 'detalle':'N/A', 'estilo':'N/A', 'estado':estado})

    def obtener_historial_restauracion(self, id_obra):
        historial = []
        if os.path.exists(self.FILE_REST):
            with open(self.FILE_REST, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    if r['id_obra'] == id_obra: historial.append(r)
        return sorted(historial, key=lambda x: x['fecha_inicio'])

# =============================================================================
# 4. INTERFAZ DE USUARIO (MENÚS)
# =============================================================================

def menu_director(usuario, repo):
    while True:
        print(f"\n--- PANEL DIRECTOR ({usuario.username}) ---")
        print("1. Consultar Valoración Patrimonial Total")
        print("2. Gestionar Listado de Museos Colaboradores")
        print("3. Registrar Importe por Cesión de Obra")
        print("4. Salir")
        op = input("Seleccione: ")
        
        if op == "1":
            total = sum(o.valor for o in repo.cargar_todo())
            print(f"VALORACIÓN TOTAL: ${total:,.2f}")
        elif op == "2":
            if os.path.exists(repo.FILE_MUSEOS):
                with open(repo.FILE_MUSEOS, 'r') as f: print(f.read())
            else: print("No hay museos registrados.")
        elif op == "4": break

def menu_restaurador(usuario, repo):
    while True:
        print(f"\n--- PANEL RESTAURADOR JEFE ---")
        print("1. Obras que requieren restauración (5 años)")
        print("2. Enviar obra a restauración inmediata (Daño)")
        print("3. Consultar historial de una obra (Ordenado)")
        print("4. Salir")
        op = input("Seleccione: ")

        if op == "1":
            for o in repo.cargar_todo():
                if o.necesita_restauracion(): print(f"ALERTA: {o.titulo} (ID: {o.id})")
        
        elif op == "2":
            id_obra = input("ID de la obra dañada: ")
            tipo = input("Tipo de daño/restauración: ")
            repo.registrar_restauracion(id_obra, tipo)
            print("Obra enviada a restauración.")

        elif op == "3":
            id_obra = input("ID de la obra: ")
            hist = repo.obtener_historial_restauracion(id_obra)
            for h in hist: print(h)

        elif op == "4": break

def menu_encargado(usuario, repo):
    print(f"\n--- PANEL ENCARGADO CATÁLOGO ({usuario.username}) ---")
    print("1. Listar obras actuales")
    print("2. Salir")
    op = input("Seleccione: ")
    if op == "1":
        for o in repo.cargar_todo(): print(f"[{o.id}] {o.titulo} - {o.autor}")

def main():
    try:
        AuthRepository.inicializar()
        MuseoRepository.inicializar()
        
        print("=== GESTIÓN MUSEO LASALLE - LOGIN ===")
        user = input("Usuario: ")
        psw = input("Contraseña: ")
        
        u = AuthRepository.login(user, psw)
        if u:
            repo = MuseoRepository()
            print(f"\nAcceso concedido: {u.rol}")
            if u.rol == "Director": menu_director(u, repo)
            elif u.rol == "Restaurador": menu_restaurador(u, repo)
            elif u.rol == "Encargado": menu_encargado(u, repo)
            elif u.rol == "Visitante":
                print("\n--- MONITOR VESTÍBULO ---")
                for o in repo.cargar_todo():
                    if o.estado == "Expuesta": print(f"SALA: {o.titulo} ({o.autor})")
        else:
            print("Acceso denegado.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()