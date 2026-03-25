import csv
import datetime

class InventarioExterno:
    """
    Representa el sistema de inventario preexistente de la empresa.
    Encapsula toda la interacción con el archivo CSV.
    """
    def __init__(self, archivo_csv="inventario_sistema.csv"):
        self.archivo = archivo_csv

    def consultar_detalles(self, codigo):
        """Busca un producto por código en el sistema externo."""
        try:
            with open(self.archivo, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['codigo']) == codigo:
                        return {
                            "codigo": int(row['codigo']),
                            "descripcion": row['descripcion'],
                            "precio": float(row['precio']),
                            "stock": int(row['stock'])
                        }
        except FileNotFoundError:
            return None
        return None

    def actualizar_stock(self, codigo, cantidad):
        """
        Actualiza la disponibilidad en el CSV. 
        Cumple con el requerimiento de descontar stock al armar el pedido.
        """
        filas = []
        actualizado = False
        
        try:
            with open(self.archivo, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames
                for row in reader:
                    if int(row['codigo']) == codigo:
                        stock_actual = int(row['stock'])
                        if stock_actual >= cantidad:
                            row['stock'] = str(stock_actual - cantidad)
                            actualizado = True
                    filas.append(row)
            
            if actualizado:
                with open(self.archivo, mode='w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(filas)
        except FileNotFoundError:
            return False
            
        return actualizado

class Producto:
    """Modelo de datos para los productos del catálogo."""
    def __init__(self, codigo, descripcion, precio, stock):
        self.codigo = codigo
        self.descripcion = descripcion
        self.precio = precio
        self.cantidad_disponible = stock

class Cliente:
    """Representa al usuario que interactúa con el sistema de TeleVentas."""
    def __init__(self, id_cliente, nombre, email):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.email = email

    def presentar_queja(self, motivo, gerente):
        """Crea una queja y la remite inmediatamente al gerente."""
        nueva_queja = Queja(self.nombre, motivo)
        nueva_queja.remitir_gerente(gerente)

class OrdenCompra:
    """Gestiona el conjunto de productos y el estado del pago."""
    def __init__(self, numero, cliente):
        self.numero = numero
        self.cliente = cliente
        self.fecha = datetime.datetime.now()
        self.items = []
        self.tipo_pago = "Tarjeta de Crédito"  # Restricción de Negocio
        self.estado = "Pendiente"

    def agregar_item(self, producto, cantidad):
        """Agrega productos a la orden antes de ser procesada."""
        self.items.append({
            "producto": producto,
            "cantidad": cantidad
        })

    def calcular_total(self):
        """Aplica el modelo matemático de sumatoria."""
        return sum(item["producto"].precio * item["cantidad"] for item in self.items)

class AgenteDeposito:
    """Encargado de las operaciones de bodega: armado y empaquetado."""
    def armar_pedido(self, orden, inventario_externo):
        """
        Consulta y actualiza el stock en el sistema externo 
        para confirmar el empaquetado.
        """
        for item in orden.items:
            codigo = item["producto"].codigo
            cantidad = item["cantidad"]
            
            if not inventario_externo.actualizar_stock(codigo, cantidad):
                return False
        
        orden.estado = "Empaquetado"
        return True

class Logistica:
    """Gestiona la delegación de la entrega a terceros."""
    def __init__(self, empresa_transporte):
        self.empresa_transporte = empresa_transporte

    def delegar_entrega(self, orden):
        """Asigna la orden a una empresa de transporte."""
        orden.estado = "Enviado"
        return f"Orden {orden.numero} delegada a {self.empresa_transporte}."

class Queja:
    """Modelo para la gestión de reclamaciones de clientes."""
    def __init__(self, cliente_nombre, motivo):
        self.cliente = cliente_nombre
        self.motivo = motivo
        self.fecha = datetime.datetime.now()

    def remitir_gerente(self, gerente):
        """Cumple con el flujo de negocio de remisión inmediata."""
        gerente.recibir_queja(self)

class GerenteRelaciones:
    """Actor que recibe y procesa las quejas del sistema."""
    def recibir_queja(self, queja):
        """Maneja la recepción de quejas remitidas."""
        print(f"NOTIFICACIÓN GERENCIA: Queja de {queja.cliente} por '{queja.motivo}' recibida.")