# Práctica 4: Global Navigation (Taxi)

## 1 Objetivo de la práctica
El objetivo de esta práctica es programar un taxi capaz de planificar rutas globales desde su posición actual hasta cualquier punto de una ciudad marcada por el usuario, utilizando el algoritmo **Gradient Path Planning (GPP)**. 

## 2 Decisiones de Diseño y Arquitectura
La arquitectura se ha diseñado bajo el paradigma de **«Plan como recurso»** mediante una máquina de 3 estados (`ESPERANDO`, `PLANIFICANDO` y `NAVEGANDO`):

 Subcampo de Penalización por Obstáculos (Línea Blanca Antichoque)
El campo revulsivo de los edificios se calcula una única vez al iniciar el programa mediante operaciones matriciales de NumPy. Se genera un margen de seguridad de 3 píxeles (`GROSOR_BORDE = 3`), seguido de un degradado suave hasta 7 píxeles que empuja al vehículo hacia el centro del carril y evita que recorte esquinas.

Onda Expansiva y Descenso de Gradiente
Al recibir un destino mediante `WebGUI.getTargetPose()`, se ejecuta un algoritmo **Wavefront (BFS con cola `deque`)** en vecindad 8 (coste `1.0` ortogonal y $\sqrt{2}$ diagonal) que expande los costes desde la meta revelando progresivamente el mapa en escala de grises invertida mediante `WebGUI.showNumpy()`. Una vez calculado el campo,el piloto consulta los siguientes 5 pasos de máximo descenso (`seguir_gradiente`) y transforma el punto objetivo al marco local del vehículo (`absolute2relative`) para controlar el volante y la velocidad.


## 3 Implementación del Código
Este fragmento muestra el núcleo de la planificación integrada sin mínimos locales y el bucle reactivo a 50Hz
```python
    elif estado == "PLANIFICANDO":
        HAL.setV(0.0)
        HAL.setW(0.0)

        # Expande la onda Wavefront 16 anillos por tick revelando calles y sumando costes
        for _ in range(ANILLOS_POR_TICK):
            if not frontera:
                break
            for _ in range(len(frontera)):
                r, c = frontera.popleft()
                d0 = campo[r, c]
                for dr, dc, coste in VECINOS_8:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < ALTO and 0 <= nc < ANCHO and es_calle[nr, nc]:
                        # Evita movimientos diagonales que atraviesen la esquina de un edificio
                        if dr != 0 and dc != 0 and not (es_calle[r + dr, c] and es_calle[r, c + dc]):
                            continue
                        # Suma distancia + penalización de muros en un solo paso
                        nd = d0 + coste + subcampo_obs[nr, nc]
                        if nd < campo[nr, nc]:
                            campo[nr, nc] = nd
                            frontera.append((nr, nc))

        mostrar_mapa(frontera)
        if not frontera:
            estado = "NAVEGANDO"

    elif estado == "NAVEGANDO":
        if math.hypot(target_world[0] - pose.x, target_world[1] - pose.y) <= DIST_META:
            HAL.setV(0.0)
            HAL.setW(0.0)
            estado = "ESPERANDO"
            print("Se ha alcanzado el destino, seleccione el siguiente")
            continue

        car_r, car_c = buscar_calle(*world_to_grid(pose.x, pose.y), solo_conocidas=True)
        sig_r, sig_c = seguir_gradiente(car_r, car_c)
        wp_x, wp_y = grid_to_world(sig_r, sig_c)

        rel_x, rel_y = absolute2relative(wp_x, wp_y, pose.x, pose.y, pose.yaw)
        error_ang = math.atan2(rel_y, rel_x)

        w = max(-W_MAX, min(W_MAX, KP_W * error_ang))
        v = 0.25 if abs(error_ang) > 1.3 else max(V_MIN, V_MAX - abs(error_ang) * 2.0)

        HAL.setV(v)
        HAL.setW(w)
```

## 4 Problemas Encontrados y Soluciones

 Problema 1: Mínimos locales y bloqueo girando en cruces
**Problema:** Al sumar el subcampo de penalización de paredes despues de calcular la distancia al destino, en calles estrechas o intersecciones se generaban «baches» de potencial donde el gradiente apuntaba a la propia celda del coche, dejándolo dando vueltas sobre sí mismo en el pasillo principal.
**Solución:** Se integró la penalización de las paredes (`subcampo_obs`) directamente dentro de la propagación de costes de la onda (`nd = d0 + coste + subcampo_obs[nr, nc]`) y se sustituyó la ventana cuadrada de búsqueda por un descenso encadenado de 5 pasos (`seguir_gradiente`).

 Problema 2: Alineación de ejes Gazebo-Matriz y tiempo de cómputo
**Problema:** En el mundo `cityLarge` ($500 \times 500\text{ m}$ centrado en `(0, 0)`), los ejes del mundo están orientados con `world_x` hacia las filas y `world_y` hacia las columnas de la imagen de $400 \times 400$ píxeles. Además, iterar celda a celda sobre matrices NumPy en Python puro ralentizaba la planificación inicial.
**Solución:** Se calibró la transformación (`OFFSET_M = 250.0`, `PX_POR_M = 0.8`) con `world_x` mapeado a filas y `world_y` a columnas, y se vectorizó el cálculo de distancias a muros con NumPy junto a una cola `deque` nativa, logrando una planificación fluida y en tiempo real.


## 5 Demostración del Funcionamiento
En el siguiente vídeo se muestra el funcionamiento completo del Taxi y la generación de la onda expansiva :

    https://youtu.be/luOpHLfStPE


## 6 Conclusión
La combinación de un planificador global basado en campos de potencial (GPP) con un controlador reactivo por descenso de gradiente permite resolver la navegación autónoma en entornos urbanos complejos con gran robustez. Separar el cálculo del mapa en una máquina de estados evita sobrecargar los 50 Hz del bucle de control, logrando trayectorias suaves, centradas en el carril y libres de colisiones.