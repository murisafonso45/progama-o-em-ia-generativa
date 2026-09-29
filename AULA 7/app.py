import streamlit as st
import pandas as pd
import plotly.express as px
import re
from collections import Counter

# ---------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Analisador de Frequência de Palavras",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTILIZAÇÃO CSS COMPATÍVEL
# ---------------------------------------------------------
css_customizado = """

"""
st.markdown(css_customizado, unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNÇÃO DE PROCESSAMENTO DE TEXTO
# ---------------------------------------------------------
def processar_texto(texto, ignorar_maiusculas=True, remover_pontuacao=True, min_comprimento=2):
    if not texto.strip():
        return pd.DataFrame()
    
    if ignorar_maiusculas:
        texto = texto.lower()
    
    if remover_pontuacao:
        texto = re.sub(r'[^\w\s]', '', texto)
    
    palavras = texto.split()
    palavras_filtradas = [p for p in palavras if len(p) >= min_comprimento]
    
    contagem = Counter(palavras_filtradas)
    
    df = pd.DataFrame(contagem.items(), columns=['Palavra', 'Frequência'])
    df = df.sort_values(by='Frequência', ascending=False).reset_index(drop=True)
    
    return df

# ---------------------------------------------------------
# CABEÇALHO DA APLICAÇÃO
# ---------------------------------------------------------
st.title("Analisador de Frequência de Palavras")
st.write("Plataforma de inteligência de texto para identificação de padrões em avaliações de clientes.")
st.divider()

# ---------------------------------------------------------
# BARRA LATERAL (CONFIGURAÇÕES E FILTROS)
# ---------------------------------------------------------
st.sidebar.header("⚙️ Configurações de Análise")

ignorar_case = st.sidebar.checkbox("Ignorar Maiúsculas/Minúsculas", value=True)
remover_pont = st.sidebar.checkbox("Remover Pontuação", value=True)
tamanho_minimo = st.sidebar.slider("Tamanho Mínimo da Palavra", min_value=1, max_value=10, value=2)
top_n = st.sidebar.slider("Exibir Top N Palavras", min_value=5, max_value=50, value=10)

# ---------------------------------------------------------
# ÁREA PRINCIPAL
# ---------------------------------------------------------
col_input, col_info = st.columns([2, 1])

with col_input:
    texto_usuario = st.text_area(
        "Insira as avaliações ou texto do cliente abaixo:",
        height=220,
        placeholder="Cole aqui o texto contendo os feedbacks..."
    )

with col_info:
    st.info("""
    **Instruções de Uso:**
    1. Cole o texto a ser analisado na caixa ao lado.
    2. Configure os parâmetros na barra lateral.
    3. Os resultados serão atualizados automaticamente.
    """)

# ---------------------------------------------------------
# EXIBIÇÃO DE RESULTADOS
# ---------------------------------------------------------
if texto_usuario:
    df_resultados = processar_texto(
        texto_usuario, 
        ignorar_maiusculas=ignorar_case, 
        remover_pontuacao=remover_pont, 
        min_comprimento=tamanho_minimo
    )
    
    if not df_resultados.empty:
        st.subheader("📈 Resumo dos Resultados")
        
        total_palavras = df_resultados['Frequência'].sum()
        palavras_unicas = len(df_resultados)
        palavra_mais_comum = df_resultados.iloc[0]['Palavra']
        freq_max = df_resultados.iloc[0]['Frequência']
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Palavras", f"{total_palavras:,}")
        m2.metric("Palavras Únicas", f"{palavras_unicas:,}")
        m3.metric("Mais Frequente", f"'{palavra_mais_comum}' ({freq_max}x)")
        
        col_grafico, col_tabela = st.columns([3, 2])
        df_top = df_resultados.head(top_n)
        
        with col_grafico:
            st.write(f"**Top {top_n} Palavras**")
            fig = px.bar(
                df_top,
                x='Frequência',
                y='Palavra',
                orientation='h',
                text='Frequência',
                color='Frequência',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#F8FAFC'),
                margin=dict(l=20, r=20, t=20, b=20),
                coloraxis_showscale=False
            )
            fig.update_traces(textposition='outside')
            st.plotly_chart(fig, use_container_width=True)
            
        with col_tabela:
            st.write("**Tabela de Frequência**")
            st.dataframe(
                df_resultados,
                column_config={
                    "Palavra": "Palavra",
                    "Frequência": st.column_config.NumberColumn("Frequência", format="%d")
                },
                use_container_width=True,
                height=380
            )
    else:
        st.warning("Nenhuma palavra atende aos critérios selecionados.")