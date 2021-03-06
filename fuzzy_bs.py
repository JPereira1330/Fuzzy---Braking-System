import sys
import math
import numpy as np
import skfuzzy as fuzzy
from skfuzzy import control
import matplotlib.pyplot as plt

def print_Green(skk): print("\033[92m {}\033[00m" .format(skk))
def print_Red(skk): print("\033[91m {}\033[00m" .format(skk))

def print_pista(tempo:int, speed:int, distance:int, distance_total:int, dist_freio:float):
    count = -1
    
    emoji = 'ð'
    if distance <= 0:
        emoji = 'ðª¦'
        distance = 1

    speed = round(speed)
    distance = round(distance)

    print(f"{tempo}s | {distance}m | {speed}km/s \t ",end="")
    while count < distance_total:
        count = count + 1
        
        if count == 0:
            print("ð§",end="")
            continue

        if count < distance:
            print("\033[92mâ\033[00m",end="")
            continue

        if count == distance:
            print(f"{emoji}",end="")
            continue

        print("\033[91mâ\033[00m",end="")

    print(f" | P Freio {dist_freio:.3f}")

def print_result(msg:bool, turno:int, speed:float, distance:float):
    print(f" ")

    if msg:
        print_Green(f" \t SUCESSO AO FREAR ")
    else:
        print_Red(f" \t CARRO COLIDIU :/ ")

    print(f" - Velocidade final: {speed} km/h")
    print(f" - Distancia final: {distance} m")
    print(f" - Tempo final: {turno} s \n")
    return True

def verifica_final(turno:int, speed:float, distance:float):

    if turno >= 50:
        print_result(False, turno, speed, distance)
        return True

    if distance == 0.0:
        print_result(True, turno, speed, distance)
        return True

    if distance < 0.0:
        print_result(False, turno, speed, distance)
        return True

    if speed == 0:
        print_result(True, turno, speed, distance)
        return True

    return False

def calc_fuzzy(speed:float, distance:float):
    
    # Criando input / ouput
    decisao     = control.Consequent(np.arange(0, 101, 1), 'decisao')
    distancia   = control.Antecedent(np.arange(0, 321, 1), 'distancia')
    velocidade  = control.Antecedent(np.arange(0, 111, 1), 'velocidade' )

    # Configurando VELOCIDADE
    velocidade['mdevagar']  = fuzzy.trapmf(velocidade.universe, [0,   0,  15,  25])
    velocidade['devagar']   = fuzzy.trapmf(velocidade.universe, [20, 30,  40,  50])
    velocidade['medio']     = fuzzy.trapmf(velocidade.universe, [40, 50,  60,  70])
    velocidade['rapido']    = fuzzy.trapmf(velocidade.universe, [60, 70,  80,  90])
    velocidade['mrapido']   = fuzzy.trapmf(velocidade.universe, [85, 90, 110, 110])

    # Configurando DISTANCIA
    distancia['mcurta']     = fuzzy.trapmf(distancia.universe, [0,     0,  30,  40])
    distancia['curta']      = fuzzy.trapmf(distancia.universe, [15,   30,  50,  70])
    distancia['media']      = fuzzy.trapmf(distancia.universe, [50,   70, 110, 130])
    distancia['longa']      = fuzzy.trapmf(distancia.universe, [110, 150, 180, 220])
    distancia['mlonga']     = fuzzy.trapmf(distancia.universe, [200, 220, 320, 320])

    # Configurando DECISAO
    decisao['nfreio']       = fuzzy.trimf(decisao.universe,  [ 0,     0,       3        ])
    decisao['mpouco']       = fuzzy.trapmf(decisao.universe, [ 0,     3,      10,     20])
    decisao['pouco']        = fuzzy.trapmf(decisao.universe, [10,    20,      30,     40])
    decisao['media']        = fuzzy.trapmf(decisao.universe, [35,    40,      60,     65])
    decisao['alta']         = fuzzy.trapmf(decisao.universe, [55,    65,      75,     80])
    decisao['malta']        = fuzzy.trapmf(decisao.universe, [75,    80,      95,    100])
    decisao['tfreio']       = fuzzy.trimf(decisao.universe,  [98,   100,     100        ])

    # Regras - Distancia muito curta
    rule11 = control.Rule(distancia['mcurta'] & velocidade['mdevagar'],  decisao['media'])
    rule12 = control.Rule(distancia['mcurta'] & velocidade['devagar'],   decisao['alta'])
    rule13 = control.Rule(distancia['mcurta'] & velocidade['medio'],     decisao['alta'])
    rule14 = control.Rule(distancia['mcurta'] & velocidade['rapido'],    decisao['tfreio'])
    rule15 = control.Rule(distancia['mcurta'] & velocidade['mrapido'],   decisao['tfreio'])

    # Regras - Distancia curta
    rule21 = control.Rule(distancia['curta'] & velocidade['mdevagar'],  decisao['pouco'])
    rule22 = control.Rule(distancia['curta'] & velocidade['devagar'],   decisao['media'])
    rule23 = control.Rule(distancia['curta'] & velocidade['medio'],     decisao['media'])
    rule24 = control.Rule(distancia['curta'] & velocidade['rapido'],    decisao['malta'])
    rule25 = control.Rule(distancia['curta'] & velocidade['mrapido'],   decisao['tfreio'])

    # Regras - Distancia media
    rule31 = control.Rule(distancia['media'] & velocidade['mdevagar'],  decisao['mpouco'])
    rule32 = control.Rule(distancia['media'] & velocidade['devagar'],   decisao['pouco'])
    rule33 = control.Rule(distancia['media'] & velocidade['medio'],     decisao['pouco'])
    rule34 = control.Rule(distancia['media'] & velocidade['rapido'],    decisao['alta'])
    rule35 = control.Rule(distancia['media'] & velocidade['mrapido'],   decisao['malta'])

    # Regras - Distancia alta
    rule41 = control.Rule(distancia['longa'] & velocidade['mdevagar'],  decisao['nfreio'])
    rule42 = control.Rule(distancia['longa'] & velocidade['devagar'],   decisao['mpouco'])
    rule43 = control.Rule(distancia['longa'] & velocidade['medio'],     decisao['mpouco'])
    rule44 = control.Rule(distancia['longa'] & velocidade['rapido'],    decisao['media'])
    rule45 = control.Rule(distancia['longa'] & velocidade['mrapido'],   decisao['alta'])

    # Regras - Distancia muito alta
    rule51 = control.Rule(distancia['mlonga'] & velocidade['mdevagar'],  decisao['nfreio'])
    rule52 = control.Rule(distancia['mlonga'] & velocidade['devagar'],   decisao['nfreio'])
    rule53 = control.Rule(distancia['mlonga'] & velocidade['medio'],     decisao['nfreio'])
    rule54 = control.Rule(distancia['mlonga'] & velocidade['rapido'],    decisao['pouco'])
    rule55 = control.Rule(distancia['mlonga'] & velocidade['mrapido'],   decisao['media'])

    decisao_control = control.ControlSystem(    \
    [rule11, rule12, rule13, rule14, rule15, \
    rule21, rule22, rule23, rule24, rule25, \
    rule31, rule32, rule33, rule34, rule35, \
    rule41, rule42, rule43, rule44, rule45, \
    rule51, rule52, rule53, rule54, rule55])

    decisao_simulador   = control.ControlSystemSimulation(decisao_control)

    # Entrando com alguns valores para qualidade da comida e do serviÃ§o
    decisao_simulador.input['velocidade']   = speed
    decisao_simulador.input['distancia']    = distance

    # Calculando o resultado
    decisao_simulador.compute()

    return decisao_simulador.output['decisao']

def calc_controller(turno:int, speed:float, distance:float):
    global last_distance

    # Verifica se o carro freiou
    if verifica_final(turno, speed, distance):
        return True

    # Convertendo
    tempo = 1                   # Tempo fixo em 1 segundo
    speed_ms = speed / 3.6      # Convertendo KM para ms

    # Calculando pressao do freio
    dif_freio = calc_fuzzy(speed, distance)

    # Calculando velocidade
    speed_ms = speed_ms - (dif_freio/100 * 6.25)   # 6.25 Ã© a representacao dos outros atritos
    if speed_ms <= 0:
        speed_ms = 0

    # Calculando distancia
    distance = distance - speed_ms

    # Convertendo
    speed = speed_ms * 3.6         # Convertendo ms para KM

    turno = turno + 1
    #print(f"[CALC] Turno: {turno} | Velocidade: {speed:.3f} | Distancia: {distance:.3f} | Pressao Freio: {dif_freio:.3f}")
    print_pista(turno, speed, distance, 100, dif_freio)
    return calc_controller(turno, speed, distance)

def main():

    # Verifica se os argumentos foram passados
    if len(sys.argv) < 3:
        print(f"Falta argumentos de velocidade(km/h) e distancia (M)");
        return False

    # Capturando dados de inicializacao
    speed = float(sys.argv[1])         # velocidade em Km/h
    distance = float(sys.argv[2])      # distancia ate parar

    return calc_controller(0, speed, distance)

main()
exit()