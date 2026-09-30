import cv2
import numpy as np
import pyautogui
import streamlit as st
from PIL import Image
from ultralytics import YOLO

# Configurações de segurança e otimização do PyAutoGUI
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.001

# Tamanho da tela principal do sistema
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

# Configuração do Streamlit
st.set_page_config(
    page_title="Controle do Mouse com as Mãos",
    page_icon="🖐️",
    layout="wide"
)

st.title("🖐️ Controle do Ponteiro do Mouse via Movimento da Mão")
st.write("Mova seu pulso/mão na câmera para controlar o ponteiro do mouse em tempo real.")

# Carregamento do modelo YOLO Pose Nano
@st.cache_resource
def load_pose_model():
    return YOLO("yolov8n-pose.pt")

model = load_pose_model()

# Sidebar de Parâmetros
st.sidebar.header("Configurações do Controle")
control_active = st.sidebar.checkbox("Ativar Controle do Mouse", value=False)
smooth_factor = st.sidebar.slider("Fator de Suavização (Smoothing)", 0.1, 0.9, 0.5, 0.05)
camera_idx = st.sidebar.number_input("Índice da Câmera", value=0, step=1)

# Variáveis globais para suavização exponencial
prev_x, prev_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

# Espaço de exibição de vídeo no Streamlit
frame_placeholder = st.empty()

if st.button("Iniciar Câmera"):
    cap = cv2.VideoCapture(camera_idx)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.error("Erro ao acessar a câmera.")
            break

        # Inverte o frame horizontalmente (efeito espelho) para intuição no movimento
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Realiza inferência de Pose com YOLOv8
        results = model.predict(source=frame, conf=0.5, device="cpu", verbose=False)
        annotated_frame = results[0].plot()

        # Verifica se alguma pessoa/pose foi detectada
        if len(results[0].keypoints) > 0 and results[0].keypoints.xy.numel() > 0:
            keypoints = results[0].keypoints.xy[0].cpu().numpy()

            # Keypoints de pulso/mão no COCO Pose: 9 (Pulso Esquerdo) ou 10 (Pulso Direito)
            wrist_right = keypoints[10] if len(keypoints) > 10 else None
            wrist_left = keypoints[9] if len(keypoints) > 9 else None

            # Seleciona o pulso detectado com maior visibilidade
            target_pt = None
            if wrist_right is not None and wrist_right[0] > 0 and wrist_right[1] > 0:
                target_pt = wrist_right
            elif wrist_left is not None and wrist_left[0] > 0 and wrist_left[1] > 0:
                target_pt = wrist_left

            if target_pt is not None:
                hand_x, hand_y = target_pt[0], target_pt[1]

                # Desenha destaque na mão rastreada
                cv2.circle(annotated_frame, (int(hand_x), int(hand_y)), 12, (0, 255, 0), -1)

                if control_active:
                    # Mapeia coordenadas do frame para a resolução da tela
                    target_x = np.interp(hand_x, [w * 0.1, w * 0.9], [0, SCREEN_WIDTH])
                    target_y = np.interp(hand_y, [h * 0.1, h * 0.9], [0, SCREEN_HEIGHT])

                    # Aplicação da Média Móvel Exponencial (EMA) para suavização
                    curr_x = prev_x + smooth_factor * (target_x - prev_x)
                    curr_y = prev_y + smooth_factor * (target_y - prev_y)

                    # Move o ponteiro do mouse
                    pyautogui.moveTo(int(curr_x), int(curr_y))

                    # Atualiza os valores anteriores
                    prev_x, prev_y = curr_x, curr_y

        # Exibe o frame atualizado na interface do Streamlit
        frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

    cap.release()