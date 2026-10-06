import WebGUI
import HAL
import Frequency
import math
import random
import time

#PARÁMETROS AJUSTADOS UNA Y OTRA VEZ

DIST_MIN = 0.3            # distancia limite para retroceder
V_AVANCE = 0.4            # velocidad en línea recta
V_RETROCESO = -0.4        # velocidad marcha atrás
T_RETROCESO = 0.6         # duración de marcha atras
W_GIRO = 1.0              # velocidad angular al girar 
TOL_ANGULAR = 0.15        # error angular aceptado al terminar el giro 

V_ESPIRAL_INI = 0.1       # velocidad inicial de la espiral
V_ESPIRAL_MAX = 0.5       # velocidad final de la espiral
INC_ESPIRAL = 0.0005      # incremento de velocidad por cada vuelta
W_ESPIRAL = 0.7           # velocidad angular de la espiral

T_AVANCE_MIN = 8.0        # avanzar dura entre un maximo y un minimo
T_AVANCE_MAX = 15.0
T_GIRO_MAX = 4.0          # si un giro tarda mas, se aborta

DIST_LATERAL_ESPIRAL = 1.0  # si hay una pared a menos de esto a un lado, no se hace espiral

# STADOS

ESPIRAL = "ESPIRAL"
AVANZANDO = "AVANZANDO"
RETROCEDIENDO = "RETROCEDIENDO"
GIRANDO = "GIRANDO"

# variables de memoria

estado_actual = ESPIRAL
velocidad_espiral = V_ESPIRAL_INI
t_inicio_estado = time.time()   # momento en que se entró al estado actual
duracion_avance = 0.0
angulo_objetivo = 0.0
direccion_giro = 1


def normalizar(angulo):
    """
    Convierte cualquier ángulo para que siempre esté dentro del rango [-pi, pi]. SI no hicieramos esto, el robot podría perder el control de la orientación.
    """

    return math.atan2(math.sin(angulo), math.cos(angulo))


def obtener_distancia_frontal():
    """
    Lee estrictamente el láser central indice 90 cumpliendo las indicaciones. Si falla, devuelve el valor 10 para que no retroceda al vacio.
    
    """
    datos_laser = HAL.getLaserData()
    if datos_laser and len(datos_laser.values) > 0:
        return datos_laser.values[90]
    return 10.0


def hay_espacio_abierto():
    """
    Comprueba los láseres de los extremos (0-15 derecha y 165-180 izquierda).
    Devuelve True si tiene más de 1 metro a los lados. Si esta en una habitacion hace espiral, si esta en un pasillo avanza.
    
    """
    datos_laser = HAL.getLaserData()
    if datos_laser and len(datos_laser.values) >= 180:
        lado_a = min(datos_laser.values[0:15])
        lado_b = min(datos_laser.values[165:180])
        return min(lado_a, lado_b) > DIST_LATERAL_ESPIRAL
    return True


def cambiar_estado(nuevo):
    """
    Transicion de la maquina de estados
    Aplica el cambio y resetea el reloj interno (t_inicio_estado) asi se controlan los tiempos del nuevo estado sin pausas es decir de manera reactiva
    """
    global estado_actual, t_inicio_estado, duracion_avance, velocidad_espiral
    
    estado_actual = nuevo
    t_inicio_estado = time.time()
    
    # Declaramos comportamientos especificos para determinados estados.

    if nuevo == AVANZANDO:
        duracion_avance = random.uniform(T_AVANCE_MIN, T_AVANCE_MAX)
    elif nuevo == ESPIRAL:
        velocidad_espiral = V_ESPIRAL_INI


def nuevo_objetivo_giro(yaw, minimo, maximo):
    """
    Calcula hacia dónde tiene que mirar el robot tras detectar un obstáculo.
    Genera un giro aleatorio (entre angulo max y min) y NORMALIZA el resultado conla funcion que hemos creado antes.
    """
    global angulo_objetivo, direccion_giro
    direccion_giro = random.choice([-1, 1])
    angulo_objetivo = normalizar(yaw + random.uniform(minimo, maximo) * direccion_giro)


print("Iniciando autómata aspirador avanzado...")

# Bucle principal:

while True:
    Frequency.tick(50) # Reactividad recomendada 50HZ

    # 1. Lectura de sensores y tiempo real
    distancia_frente = obtener_distancia_frontal()
    yaw_actual = HAL.getPose3d().yaw
    ahora = time.time()

    # 2. Evasion de obstaculos por prioridad
    # Si detecta peligro frontal, fuerza el retroceso. 
    # Se ignora intencionadamente si ya está retrocediendo o girando para evitar bloqueos.
    if distancia_frente < DIST_MIN and estado_actual not in (RETROCEDIENDO, GIRANDO):
        cambiar_estado(RETROCEDIENDO)

    # 3 FUncionamiento maquina de estados

    if estado_actual == ESPIRAL:

        # Abre el radio de la espiral de manera progresiva
        if velocidad_espiral < V_ESPIRAL_MAX:
            velocidad_espiral += INC_ESPIRAL
            HAL.setV(velocidad_espiral)
            HAL.setW(W_ESPIRAL)
        else:
            # Si llega al limite se cambia a avanzar para ir a explorar otra habitación
            cambiar_estado(AVANZANDO)

    elif estado_actual == AVANZANDO:
        # Rapidez en linea recta sin obstáculos
        HAL.setV(V_AVANCE)
        HAL.setW(0.0)
        
        # Check de si ha avanzado 
        if ahora - t_inicio_estado > duracion_avance:
            if hay_espacio_abierto():
                # Si está en una zona amplia, comienza la espiral
                cambiar_estado(ESPIRAL)
            else:
                # Si está en un pasillo estrecho, reinicia el timer y sigue buscando salida
                t_inicio_estado = ahora   

    elif estado_actual == RETROCEDIENDO:
        # Se separa del obstáculo
        HAL.setV(V_RETROCESO)
        HAL.setW(0.0)
        
        # Uso del reloj interno en lugar de time.sleep(0.6)
        if ahora - t_inicio_estado > T_RETROCESO:
            nuevo_objetivo_giro(yaw_actual, 1.5, 2.8)
            cambiar_estado(GIRANDO)

    elif estado_actual == GIRANDO:
        # Rota sobre su eje central hacia el objetivo calculado
        HAL.setV(0.0)
        HAL.setW(W_GIRO * direccion_giro)

        # Diferencia matemática entre su orientación actual y la deseada
        error = abs(normalizar(angulo_objetivo - yaw_actual))

        # Si lleva demasiado tiempo intentando girar y no puede
        if ahora - t_inicio_estado > T_GIRO_MAX:
            cambiar_estado(RETROCEDIENDO)

        # Giro completado exitosamente 
        elif error < TOL_ANGULAR:
            
            # Comprueba si tras girar sigue teniendo un obstáculo cerca
            if distancia_frente < DIST_MIN + 0.1:
                # Calcula un nuevo giro pequeño y reinicia el reloj sin salir del estado
                nuevo_objetivo_giro(yaw_actual, 0.8, 1.5)
                t_inicio_estado = ahora   
            
            # Si el frente está libre, decide inteligentemente su próximo movimiento
            elif hay_espacio_abierto():

                # Aleatoriedad entre avanzar recto o hacer una espiral
                cambiar_estado(random.choice([ESPIRAL, AVANZANDO]))
            else:
                # Si está arrinconado avanza ahcia delante
                cambiar_estado(AVANZANDO)