# Práctica 3: Esquiva-Obstáculos (VFF)

## 1. Objetivo de la práctica

El objetivo de esta práctica es implementar un algoritmo de navegación local reactivo basado en **Campos de Fuerza Virtuales (VFF)**. El Fórmula 1 debe de avanzar mientras sortea obstáculos dinámicos y estáticos en la pista, calculando vectores de atracción y repulsión en tiempo real.

## 2. Decisiones de Diseño y Arquitectura

El algoritmo VFF tradicional presenta un problema matemático crítico: cuando la distancia a un obstáculo se acerca a cero, la fuerza repulsiva tiende a infinito, provocando volantazos inestables y el bloqueo del vehículo. 

 Suavizado Vectorial e Inercia
Para lograr una navegación fluida, he implementado dos soluciones matemáticas:
1. **Tope de singularidad:** Se ha añadido una constante al denominador de la fuerza repulsiva (`(dist + 0.2)^2`) para limitar el empuje máximo en distancias cortas.
2. **Filtro Paso Bajo (Inercia):** Las salidas de velocidad y giro pasan por un filtro de memoria (`0.3 * nuevo + 0.7 * anterior`), eliminando los latigazosy haciendo asi que todo sea más suave y progresivo


## 3. Implementación del Código
El procesamiento de los 180 rayos láser y la composición del vector resultante se estructuran en el bucle principal a 50Hz de la siguiente manera:

```python
    # B) VECTOR OBSTÁCULO (Repulsión)
    for i in range(180):
        dist = laser_polar[i][0]
        if 0.1 < dist < 3.5:
            # Tope matemático para evitar que tienda a infinito
            magnitud_fuerza = K_REPULSIVA / ((dist + 0.2) ** 2)
            
            unit_x = laser_xy[i][0] / dist
            unit_y = laser_xy[i][1] / dist
            
            # Amortiguamos el retroceso frontal para priorizar el esquive lateral
            fuerza_obs_x -= unit_x * (magnitud_fuerza * 0.3) 
            fuerza_obs_y -= unit_y * magnitud_fuerza         

    # D) TRADUCCIÓN A MOTORES (Filtro de Inercia)
    angulo_giro = math.atan2(fuerza_total_y, fuerza_total_x)
    giro_w_objetivo = angulo_giro * 1.1 
    velocidad_v_objetiva = max(1.5, VELOCIDAD_CRUCERO - (abs(angulo_giro) * 1.8))
    
    giro_w = (0.3 * giro_w_objetivo) + (0.7 * giro_previo)
    velocidad_v = (0.2 * velocidad_v_objetiva) + (0.8 * vel_previa)

```     

## 4. Problemas Encontrados y Soluciones

- Oscilación en pasillos estrechos
Problema: Al detectar obstáculos simultáneos en ambos laterales, las fuerzas repulsivas se anulaban en el eje Y y se sumaban negativamente en el eje X, jhaciendo que pareciera que el coche temblara y zigzageara.
Solución: Se redujo el multiplicador de choque frontal (0.3 sobre el eje X) para mantener siempre una inercia de avance, y se amplió el radio de detección a 3.5m para que el coche inicie la trazada antes de entrar al cuello de botella.


## 5. Demostración del Funcionamiento

https://youtu.be/Mk_BLuCtVF0

## 6. Conclusión

La combinación de campos de fuerza virtuales amortiguados y filtros de inercia demuestra que el control de un vehículo autónomo requiere adaptar las leyes físicas puras (como el cuadrado inverso) a las limitaciones mecánicas reales. El F1 traza curvas suaves alrededor de los muros sin perder velocidad excesiva, cumpliendo el objetivo de manera eficiente.
