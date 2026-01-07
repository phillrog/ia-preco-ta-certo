import streamlit as st
import os
import base64

def carregar_css(caminho_relativo):
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))     
    caminho_ajustado = caminho_relativo.lstrip('/')
    caminho_final = os.path.join(diretorio_atual, '..', caminho_ajustado)
    
    try:
        with open(caminho_final, "r", encoding="utf-8") as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Arquivo não encontrado em: {caminho_final}")

def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def mensagem_erro_df(val):
    color = 'red' if val == 'ERRADO' else 'black'
    return f'color: {color}'

def carregar_imagem_base64(caminho_relativo):
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_ajustado = caminho_relativo.lstrip('/')
    caminho_final = os.path.join(diretorio_atual, '..', caminho_ajustado)
    
    try:
        with open(caminho_final, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None