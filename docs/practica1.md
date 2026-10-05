# Práctica 1: Aspiradora Autónoma (Vacuum Cleaner)

## 🎯 1. Objetivo de la práctica
El objetivo de esta práctica es implementar el algoritmo de navegación de un robot aspirador de gama baja para que limpie una casa de forma pseudoaleatoria. El requisito fundamental es lograr la mayor cobertura posible utilizando una Máquina de Estados Finita (FSM) **estrictamente reactiva**, sin recurrir a funciones bloqueantes como `sleep()`.

## 🧠 2. Decisiones de Diseño y Arquitectura
Para maximizar la cobertura y evitar patrones repetitivos, he diseñado un autómata de 4 estados. A diferencia de las soluciones convencionales, mi enfoque prescinde totalmente de pausar la ejecución.

::: info Control Reactivo Basado en Reloj Interno
Para cumplir la restricción de no usar `sleep()`, el control de tiempos en los estados de giro y retroceso se evalúa en cada iteración restando la marca de tiempo inicial (`time.time()`) a la marca actual. Esto permite que el robot siga leyendo los sensores a 50Hz reales en todo momento.
:::

Las transiciones clave son:
* **ESPIRAL:** El estado por defecto. Abre el radio progresivamente incrementando la velocidad lineal de forma constante.
* **RETROCEDIENDO:** Al detectar un obstáculo frontal a menos de 0.3m, da un micro-retroceso de 0.25s para ganar espacio de maniobra.
* **GIRANDO:** Calcula un ángulo aleatorio y pivota utilizando la odometría (`yaw`). Para evitar errores de superposición angular, los ángulos se normalizan al rango $[-\pi, \pi]$ mediante `math.atan2()`.
* **AVANZANDO:** Introduce un factor estocástico. Para evitar que el robot se quede haciendo espirales infinitas en la misma habitación, al alcanzar el radio máximo permitido de espiral, el robot transita al estado AVANZANDO para cruzar la sala en línea recta.

## 💻 3. Implementación del Código
Este es el bucle principal de control, donde se aprecia la gestión de estados y el uso de los sensores laterales para evitar la generación de espirales dentro de pasillos estrechos:

```python
    # 2. SISTEMA DE EVASIÓN PRIORITARIA
    if distancia_frente < DIST_MIN and estado_actual not in (RETROCEDIENDO, GIRANDO):
        cambiar_estado(RETROCEDIENDO)

    # 3. LÓGICA DE LA MÁQUINA DE ESTADOS
    if estado_actual == ESPIRAL:
        if velocidad_espiral < V_ESPIRAL_MAX:
            velocidad_espiral += INC_ESPIRAL
            HAL.setV(velocidad_espiral)
            HAL.setW(W_ESPIRAL)
        else:
            cambiar_estado(AVANZANDO)

    elif estado_actual == AVANZANDO:
        HAL.setV(V_AVANCE)
        HAL.setW(0.0)
        if ahora - t_inicio_estado > duracion_avance:
            if hay_espacio_abierto():
                cambiar_estado(ESPIRAL)
            else:
                t_inicio_estado = ahora  

4. Problemas Encontrados y Soluciones

::: warning Problema 1: Bucle Infinito en Espiral
Al fijar un tope de seguridad para la velocidad lineal de la espiral, el robot dejaba de abrir el radio y se quedaba trazando un círculo infinito sobre su propia huella.
Solución: Modifiqué la FSM para que, al alcanzar la velocidad máxima de espiral, el autómata fuerce la transición al estado AVANZANDO, rompiendo el patrón circular y explorando nuevas zonas.
:::

::: warning Problema 2: Choques por "Visión de Túnel"
Al leer únicamente el láser central (índice 90), el robot chocaba con las esquinas al acercarse en diagonal, ya que el rayo pasaba de largo el obstáculo pero la carcasa no.
Solución: En lugar de crear un cono visual (lo cual incumpliría la norma de usar solo un láser), ajusté la física del robot: aumenté la distancia mínima de frenado (0.3m) y reduje ligeramente las velocidades de avance, logrando que la inercia no arrastrase al robot contra las paredes.
:::
🎥 5. Demostración del Funcionamiento
 
https://youtu.be/dUT-wFiOArk


📈 6. Conclusión

El uso de una arquitectura 100% reactiva combinada con un toque de estocasticidad (transiciones aleatorias tras los giros) ha demostrado ser muy eficiente. La adición del detector de pasillos (hay_espacio_abierto()) ha evitado colisiones innecesarias, logrando un porcentaje de limpieza óptimo para ser un robot de gama baja sin mapa previo. 

    # ... [El código continúa con RETROCEDIENDO y GIRANDO] ...