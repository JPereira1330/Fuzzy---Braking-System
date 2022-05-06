import numpy as np
import skfuzzy as fuzzy
from skfuzzy import control
import matplotlib.pyplot as plt

# Cria as variáveis do problema
comida = control.Antecedent(np.arange(0, 11, 1), 'comida')
servico = control.Antecedent(np.arange(0, 11, 1), 'servico')
gorjeta = control.Consequent(np.arange(0, 26, 1), 'gorjeta')

# Cria automaticamente o mapeamento entre valores nítidos e difusos
# usando uma função de pertinência padrão (triângulo)
comida.automf(names=['péssima', 'comível', 'deliciosa'])

# Cria as funções de pertinência usando tipos variados
servico['ruim'] = fuzzy.trimf(servico.universe, [0, 0, 5])
servico['aceitável'] = fuzzy.gaussmf(servico.universe, 5, 2)
servico['excelente'] = fuzzy.gaussmf(servico.universe, 10, 3)

gorjeta['baixa'] = fuzzy.trimf(gorjeta.universe, [0, 0, 13])
gorjeta['média'] = fuzzy.trapmf(gorjeta.universe, [0, 13, 15, 25])
gorjeta['alta'] = fuzzy.trimf(gorjeta.universe, [15, 25, 25])

# Posso ver cada gráfico difuso com a função view
comida.view()
servico.view()
gorjeta.view()

rule1 = control.Rule(servico['excelente'] | comida['deliciosa'], gorjeta['alta'])
rule2 = control.Rule(servico['aceitável'], gorjeta['média'])
rule3 = control.Rule(servico['ruim'] & comida['péssima'], gorjeta['baixa'])

gorjeta_control = control.ControlSystem([rule1, rule2, rule3])
gorjeta_simulador = control.ControlSystemSimulation(gorjeta_control)

# Entrando com alguns valores para qualidade da comida e do serviço
gorjeta_simulador.input['comida'] = 3.5
gorjeta_simulador.input['servico'] = 2.4

# Calculando o resultado
gorjeta_simulador.compute()

print(gorjeta_simulador.output['gorjeta'])

# Mostrando os gráficos fuzzy gerados
comida.view(sim=gorjeta_simulador)
servico.view(sim=gorjeta_simulador)
gorjeta.view(sim=gorjeta_simulador)
plt.show()
