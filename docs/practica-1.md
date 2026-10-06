# Práctica 1: Aspiradora Autónoma (Vacuum Cleaner)

## 1 - Objetivo de la práctica
El objetivo de esta práctica es implementar un algoritmo que provoque la limpieza del mayor porcentaje de suelo posible en una aspiradora autónoma. Lo principal es utilizar una máquina de estados y no se puede utilizar sleep.

## 2 - Decisiones de Diseño y Arquitectura
Para evitar patrones repetidos he diseñado un autómata de 4 estados. 

::: info Control Reactivo Basado en Reloj Interno
Para cumplir la restricción de no usar `sleep()`, el control de tiempos se evalúa en cada iteración restando la marca de tiempo inicial (`time.time()`) a la marca actual. Así se siguen leyendo los sensores a la frecuencia indicada 50HZ.
:::

Las transiciones que he utilizado son:

* **ESPIRAL:** Abre el radio progresivamente incrementando la velocidad lineal de forma constante hasta que cambie al siguiente estado.
* **AVANZANDO:** Introduce un factor estocástico. Para evitar que el robot se quede haciendo espirales infinitas en el mismo lugar, al alcanzar el radio maximo de espiral, cambia al estado AVANZANDO para cruzar la sala en línea recta.
* **RETROCEDIENDO:** Al detectar un obstáculo frontal a menos de una determinada distancia, da un retroceso de 0.6s para ganar espacio de maniobra.
* **GIRANDO:** Calcula un ángulo aleatorio y pivota utilizando la odometría (`yaw`).Los ángulos se normalizan al rango `[-pi, pi]` mediante `math.atan2()`.


## 3 - Implementación del Código
Este es el bucle principal de control, donde se aprecia la gestión reactiva de los estados y el uso de los sensores laterales para detectar si el robot se encuentra en un pasillo (evitando así generar espirales inútiles):

```python
    #evasion por priodridad
    if distancia_frente < DIST_MIN and estado_actual not in (RETROCEDIENDO, GIRANDO):
        cambiar_estado(RETROCEDIENDO)

    # lógica de la maquina de estados
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
                t_inicio_estado = ahora   # Es un pasillo: sigue avanzando
```


## 4. Problemas Encontrados y Soluciones

::: Problema 1: Bucle Infinito en Espiral
Al fijar un tope de seguridad para la velocidad lineal de la espiral, el robot no aumentaba su radio y pasaba constantemente por el mismo trazo que habia hecho anteriormente
**Solución:** Cambiar la máquina de estados para forzar que cambie de estado a AVANZANDO al llegar a la Vmáx establecida en la espiral. 
:::

:::  Problema 2: Choques por falta de visión
Al leer únicamente el láser central (índice 90), el laser indicaba que no habia nada pero el cuerpo del robot era más ancho y se chocaba con las esquinas, las patas de la mesa, las sillas...
**Solución:** Aumenté la distancia mínima de frenado y ajusté ligeramente las velocidades de avance y retroceso, haciendo así que la inercia desapareciese y no provocara choques.
:::

## 5. Demostración del Funcionamiento

Aquí se puede observar el comportamiento del autómata, el cual cuanto más tiempo dejemos, más espacio recorrerá, tras hacer varias pruebas, más o menos tarda lo mismo en recorrer un 60%, pero a partir de aqui el tiempo se dispara en relación a lo que va añadiendo de limpieza.

https://youtu.be/dUT-wFiOArk

## 📈 6. Conclusión
La mezcla de reactividad y aleatoriedad ha demostrado ser muy eficiente, aunque no perfecta.
Sin tantas restricciones, seguramente hubiera sido posible realizar un mayor porcentaje de limpieza en un tiempo menor, pero tras muchas pruebas y cambios, considero que el trabajo realizado ha sido un éxito.

