import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression

# 1. Configuração do visual no estilo Gamer
st.set_page_config(page_title="Gamer Fatigue Level", page_icon="🎮")

st.title("🎮 Predictor de Cansaço Gamer")
st.write(
    "Descubra em qual nível seu **HP/Stamina** vai estar depois de algumas horas de gameplay!"
)

# 2. DataFrame de treino com os dados fornecidos
gamer = pd.DataFrame(
    {"horas_jogo": [1, 2, 4, 6, 8, 10], "cansaco": [1, 2, 3, 5, 8, 10]}
)

# Separando X (funcionalidade) e y (alvo)
X = gamer[["horas_jogo"]]
y = gamer["cansaco"]

# 3. Treinando o modelo de Regressão Linear
modelo = LinearRegression()
modelo.fit(X, y)

# 4. Interface Gráfica Interativa
st.subheader("⏱️ Quantas horas você pretende jogar hoje?")
horas = st.slider("Selecione o tempo de gameplay (horas):", 0, 16, 5)

# Previsão
horas_arr = np.array([[horas]])
cansaco_previsto = modelo.predict(horas_arr)[0]

# Garantir que não dê valor negativo nem passe muito dos limites da tela
cansaco_final = max(0.0, float(cansaco_previsto))

# 5. Exibição do Resultado Dinâmico
st.markdown("---")
st.metric(
    label="⚡ Nível de Cansaço Estimado (0 a 10)",
    value=f"{cansaco_final:.1f} / 10",
)

# Feedback visual gamer de acordo com o nível
if cansaco_final <= 3.0:
  st.success("🟢 **Modo Easy:** Stamina no máximo! Dá para encarar mais umas partidas.")
elif cansaco_final <= 7.0:
  st.warning(
      "🟡 **Modo Medium:** Cuidado! A mira pode começar a tremer e o tempo de reação vai cair."
  )
else:
  st.error(
      "🔴 **Modo Hard / Critical HP:** Hora de salvar o jogo, tomar uma água e ir descansar!"
  )