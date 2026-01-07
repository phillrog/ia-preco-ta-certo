import streamlit as st
import os
import base64
from datetime import datetime
from fpdf import FPDF
import io

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

def gerar_pdf_direto(lista_dados, total_carrinho, total_cupom, img_cupom_b64):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Cabeçalho
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 14, "IA IA Preço Tá Certo ?", ln=True, align="C")
    pdf.cell(190, 10, "Relatório de Compra", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(190, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="C")
    pdf.ln(5)

    # Resumo
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, " Resumo", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(190, 8, f" Total Estimado (Carrinho): {formatar_moeda(total_carrinho)}", ln=True)
    pdf.cell(190, 8, f" Total Pago (Cupom): {formatar_moeda(total_cupom)}", ln=True)
    
    dif = total_cupom - total_carrinho
    pdf.set_text_color(200, 0, 0) if dif > 0 else pdf.set_text_color(0, 150, 0)
    pdf.cell(190, 8, f" Divergência: {formatar_moeda(dif)}", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)

    # Itens e Fotos
    pdf.set_font("Arial", "B", 12)
    pdf.cell(190, 10, " Itens", ln=True, fill=True)
    pdf.ln(2)

    for item in lista_dados:
        # Nome do Item
        pdf.set_font("Arial", "B", 10)
        pdf.cell(190, 6, f"Produto: {item['Produto']}", ln=True)
        pdf.set_font("Arial", "", 9)
        pdf.cell(190, 5, f"Data: {item['Adicionado em']} | Preço: {formatar_moeda(item['Preço Prateleira'])}", ln=True)
        
        # Imagem da Etiqueta
        if item.get("_img_b64"):
            img_data = base64.b64decode(item["_img_b64"])
            img_file = io.BytesIO(img_data)
            pdf.image(img_file, w=50) 
            pdf.ln(2)
        
        pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Linha divisória
        pdf.ln(2)

    # Cupom fiscal
    if img_cupom_b64:
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)
        pdf.cell(190, 10, " Foto do Cupom Fiscal", ln=True, align="C")
        img_cupom_data = base64.b64decode(img_cupom_b64)
        img_cupom_file = io.BytesIO(img_cupom_data)
        pdf.image(img_cupom_file, x=10, w=180)

    return bytes(pdf.output())