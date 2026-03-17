classDiagram
    class Producto {
        -int codigo
        -string descripcion
        -float precio
        -int stockActual
        +actualizarStock(cantidad)
        +obtenerInfo() string
    }

    class Cliente {
        -string cedula
        -string nombre
        -string telefono
        +consultarCatalogo(catalogo)
        +realizarPedido(listaProductos)
    }

    class Pedido {
        -int numeroPedido
        -date fecha
        -float total
        -string estado
        +confirmarPago(metodo)
        +verificarDisponibilidad()
        +cancelar()
    }

    class InventarioExterno {
        <<interface>>
        +consultarExistencias(codigo)
        +descontarProducto(codigo, cantidad)
    }

    class Logistica {
        -string empresaTransporte
        -string guiaSeguimiento
        +despacharPedido(pedido)
        +calcularFechaEntrega()
    }

    class Queja {
        -int idQueja
        -string motivo
        -string estado
        +registrar()
        +asignarAsesor()
    }

    Cliente "1" -- "*" Pedido : genera
    Pedido "*" -- "*" Producto : incluye
    Pedido ..> InventarioExterno : consulta
    Pedido "1" -- "1" Logistica : se entrega via
    Cliente "1" -- "*" Queja : interpone