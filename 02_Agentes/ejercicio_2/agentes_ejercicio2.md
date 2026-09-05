# Ejercicio 2 - Agentes

### 1. Asistente Virtual por Voz - Alexa
- **Performance:** Ejecutar correctamente las skills
- **Environment:** Una habitación con o sin ruidos y personas, Parcialmente observable, multi agente.
- **Actuators:** Enceder y apagar micrófono, encender y apagar bocina. encender cámara o apagarla, subir volumen, bajar volumen, enviar alertas al usuario.
- **Sensors:** Cámara, Micrófono y Bocina. Mediante el micrófono escucha los comandos por voz que se le entregan a través del usuario. La bocina sirve como medio para entregar la información o para seguir recibiendo más información del usuario.

Lo clasifiqué como parcialmente observable porque el agente no puede percibir todo su entorno, solo nos escucha y multi agente porque varias personas pueden conversar con el asistente.

### Robot aspirador doméstico

- **Performance:** Limpieza del suelo, algunos aspiran por lo cual la métrica es no detectar polvo en el suelo por donde hayan pasado o en el caso de los que trapean, no detectar liquidos presentes en el suelo. Tiempo de limpieza.
- **Environment:** Habitaciones de casas, edificios, cerrados o no cerrados. Continuo.
- **Actuators:** programar horarios de limpieza, encendido, apagado del dispositivo, recargar algún elemento de limpieza.
- **Sensors:** Cámara para visualizar el piso y detectar manchas o polvo, un sensor de paredes para evitar golpearse, movimiento


Continuo, porque los robots aspiradores dan vueltas por toda la casa hasta lograr su performance.

### Sistema de recomendación de streaming Youtube Premium

- **Performance:** Tiempo de permanencia en la plataforma, horas de escucha de musica categorizadas por gustos.
- **Environment:** Computadora, auto, celular, observable y secuencial
- **Actuators:** Reproducir música, siguiente, anterior canción.
- **Sensors:** Tiempo de escucha de una canción, likes de la canción, número de veces escuchada, búsqueda de la canción o autores.

Puse obserable porque los datos se pueden ver conforme se generan por el usuario y secuencial porque las canciones tienen una continuación al clickar el botón de siguiente


### Vehículo autónomo en ciudad TESLA

- **Performance:** Llegar al destino de manera segura, eficiente, midiendo kilometros, con batería.
- **Environment:** La calle, la ciudad, un entorno totalmente abierto y no predecible y podria ser parcialmente observable dado que la calle es cambiante y llena de autos, así como peatones.  Continuo, parcialmente observable y estocastico
- **Actuators:** Motor de batería, torque, llantas, volante (en caso de conducción manual)
- **Sensors:** Sensor de movimiento, sensor de proximidad, acelerometro, cálculo de kilometros al destino mediante gps.

### Agente de trading algorítmico en bolsa

- **Performance:** Profit, Win rate, sharpe ratio, sortino ratio, DrawDown
- **Environment:** El mercado de valores, redes de computadoras interconectadas, otros usuarios y algoritmos. Es totalmente estocástico, las series de tiempo son aleatorias, y dependiendo del "time frame" puede ser más volátil, también es multiagente, continuo y observable (la información está siempre disponible en segundos y de manera continua), parcialmente observable (cierta información)
- **Actuators:**  Colocar orden de compra, colocar orden de venta, Colocar orden limite de compra o venta, colocar orden stop de compra o venta, colocar trailing stop, colocar stop loss, cierre de operacion por tiempo, cierre de operación por % de salida, cancelar órdenes, obtener precios de mercado, analizar precios de mercado, enviar alertas de precio, enviar alertas de entrada o salida al usuario.
- **Sensors:** Cálculo de volatilidad, Tendencia, Precio de apertura, precio de cierre, obtención de horario de trading, velocidad o momentum del precio.

Estocastico porque la naturaleza de los mercados es aleatoria, observable porque los datos siempre están a disposición de todos los actores del mercado, y parcialmente observable porque ciertos "micro datos" que los actores de mercado más poderosos ven (libro de órdenes, profundidad 1 y 2 que solo instituciones pueden pagar)


### Sistema de diagnóstico médico asistido por IA

- **Performance:** % de acierto en el diagnóstico.
- **Environment:**  Observable, multiagente, estocástico, que serían las personas a analizar.
- **Actuators:** Encendido del sistema, analisis del paciente, análisis de los datos y muestras para el diagnóstico, apagado del sistema, impresión de los datos,  crear diagnóstico.
- **Sensors:** Podría ser información del paciente, de sus estudios de laboratorio, lectura del diagnóstico diferencial.


### Dron de inspección de infraestructura

- **Performance:** Generación de reporte de la infraestructura
- **Environment:** Calles, ambientes abiertos con edidificios o casas, no determinista, observable.
- **Actuators:** Encendido del dron, movimiento a la izquierda, derecha, arriba, abajo, adelante, atrás, encendido del analizador de imágenes, encendido de cámara, visor de cámara, generador de datos de inspección.
- **Sensors:** Cámara, cámara infraroja, análsisi de imágenes en tiempo real, detección de objetos y anomalías.


### Agente jugador de ajedrez

- **Performance:** % partidas ganadas y % de partidas perdidas.
- **Environment:** Un cliente-servidor multiagente con los participantes sea un usuario u otro agente (multiagente), aleatorio no determinista, parcialmente observable (no sabemos las cartas de los demás usuarios ni si son seres humanos pero sabemos que toman decisiones racionales) o incluso podría ser un robot fisico jugador de ajedrez.
- **Actuators:** Descubrir cartas, tomar una carta, pasar turno, ir all in, apostar, abandonar partida.
- **Sensors:** Visualizador de cartas (puede ser texto o imagen), cantidad de monedas o fichas.

