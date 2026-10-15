# Práctica 2: Sigue-Líneas (Fórmula 1)

##   Objetivo de la práctica

El objetivo de la práctica es vehículo debe seguir una línea roja central utilizando visión artificial y modificar dinámicamente su velocidad lineal y angular mediante un controlador PID.

##   Decisiones de Diseño y Arquitectura

Módulo de percepción : Procesa la imagen capturada, después transforma la imagen a espacio **HSV**, filtra los dos rangos del espectro rojo y recorta el 40% superior (ROI) para omitir ruido del horizonte. El Set Point se calcula mediante los momentos de la imagen (`cv2.moments`).

PID y aceleracion progresiva: El cálculo del error alimenta un controlador PD. La clave de la estabilidad reside en la **velocidad dinámica**: el motor clava los frenos proporcionalmente a la desviación de la curva, y al salir a la recta, utiliza una **aceleración progresiva** para evitar zigzag en el volante.


##  Implementación del Código

Con este bucle podemos hacer una aceleración progresiva yun freno adaptativo que permite alcanzar velocidades punta de $20.0$ sin perder tracción al salir de curvas cerradas:

```python
    # Lógica de Control Dinámico (PID)
    if linea_detectada:
        # --- Corrección de dirección (Volante / W) ---
        P = KP * error
        D = KD * (error - error_previo)

        error_acumulado += error
        error_acumulado = max(min(error_acumulado, 500), -500)
        I = KI * error_acumulado

        giro_w = P + D + I

        # --- Frenada brusca vs Aceleración suave (Aceleración / V) ---
        penalizacion_curva = abs(error) * 0.7
        v_objetivo = max(V_MIN, V_MAX - penalizacion_curva)

        # Freno de seguridad por si fuera necesario entrar a curva
        if v_objetivo < velocidad_actual:
            velocidad_actual = v_objetivo

        # Aceleración progresiva al salir de curva cerrada (simula tracción real)
        else:
            velocidad_actual = min(v_objetivo, velocidad_actual + PASO_ACELERACION)

        # Actualización a motores
        error_previo = error
        HAL.setV(velocidad_actual)
        HAL.setW(giro_w)

```


##  Problemas Encontrados y Soluciones

Oscilación en Rectas: Al salir de una curva cerrada y enfilar una recta, la velocidad saltaba instantáneamente de 4 a 20. A esa velocidad, la corrección provocaba oscilacimiento, simulando como si fuera pérdida de tracción y querer enderezar el coche constantemente. Solución: Se implementó la variable PASO_ACELERACION = 0.15. El coche frena de golpe al detectar la curva por seguridad, pero acelera gradualmente al salir a la recta, dando tiempo al PID a alinear el chasis perfectamente antes de alcanzar la velocidad máxima.

Inercia : Al rodar a velocidades extremas, la masa del coche empujaba el chasis hacia el exterior de la curva, perdiendo la línea roja.Solución: Se aumentó el multiplicador de frenada (0.7) para anticipar la retención del motor, y se equilibró la relación entre $K_p = 0.007$ y $K_d = 0.01$ para que el volante tire con fuerza hacia el vértice interior y absorba el giro al estabilizarse.

##  Demostración del Funcionamiento

Aquí tenemos 2 de los circuitos comprobados, en mi caso han sido el circuito de Montmeló el cual resultaba tediosa la ultima chicane, y el circuito simple, para el cual no he tenido graves problemas.

Circuito básico : https://youtube.com/shorts/M4zFmRD3ix0

Circuito de Montmeló : https://youtube.com/shorts/-9ygJxXkdy0


## Conclusión de la práctica 

Esta práctica creo que ha sido bastante útil para entender y comprender como funciona un PID, aunque haya sido tedioso probar hasta encontrar los valores que mejor funcionaran, estoy contento con el resultado.
