# tfg-protocolos-comunicacion
Diseño de un sistema adaptable para comunicación eficiente entre un vehículo no tripulado y una estación en tierra.

El sistema de comunicaciones consta de tres archivos: la librería ("protocolos_comunicacion.py"), que tiene la información necesaria para que funcionen las conexiones por WiFi, Bluetooth y el puerto serie; el servidor ("servidor.py"), que preferentemente irá en el vehículo no tripulado, ya que no se requiere la intervención del usuario para su funcionamiento y el cliente ("cliente.py"), que haría de estación en tierra y sería el encargado de gestionar las conexiones e interactuar con el servidor para que este responda.
