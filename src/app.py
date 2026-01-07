import streamlit as st
import re
import base64
import pandas as pd
from PIL import Image
from datetime import datetime
from streamlit_back_camera_input import back_camera_input

from services.langchain_gemini_service import LangchainGeminiService
from utils.utils import carregar_css, formatar_moeda, mensagem_erro_df, carregar_imagem_base64

def main():
    st.set_page_config(page_title="IA Preço Tá Certo ?", layout="wide")
    carregar_css('assets/styles.css')
    
    logo_b64 = carregar_imagem_base64('assets/logo_carrinho.png')
    
    if logo_b64:
        header_html = f"""
            <div id="logo">
                <img src="data:image/png;base64,{logo_b64}">
                <div>
                    <div class="header" style="margin: 0; line-height: 1.2;">IA Preço Tá Certo ?</div>
                    <div class="titulo-projeto" style="margin: 0; line-height: 1.2;">🛒 Assistente de Compras Inteligente</div>
                </div>
            </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
    else:
        # Header com Clamp e Shimmer
        st.markdown('<div class="header">IA Preço Tá Certo ?</div>', unsafe_allow_html=True)
        st.markdown('<div class="titulo-projeto">🛒 Assistente de Compras Inteligente</div>', unsafe_allow_html=True)
      
    if "toast_msg" in st.session_state and st.session_state.toast_msg:
        st.toast(st.session_state.toast_msg["texto"], icon=st.session_state.toast_msg["icon"])
        st.session_state.toast_msg = None 

    with st.sidebar:            
        api_key = st.text_input("Gemini API Key", type="password")
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        st.divider()
        
        disclaimer_html = """
            <div class="disclaimer">
                <strong>⚠️ DISCLAIMER (AVISO DE USO)</strong><br><br>
                ESTA É UMA FERRAMENTA BASEADA EM INTELIGÊNCIA ARTIFICIAL EXPERIMENTAL. 
                AS ANÁLISES FORNECIDAS SÃO SUGESTÕES EDUCATIVAS. O PROCESSAMENTO DE DADOS 
                SEGUE RIGOROSOS FILTROS DE PRIVACIDADE LOCAIS, MAS RECOMENDA-SE QUE O USUÁRIO 
                VALIDE TODAS AS INFORMAÇÕES E CONSULTE AS POLÍTICAS DE PRIVACIDADE DO PROVEDOR (GOOGLE GEMINI).
            </div>
        """
        st.markdown(disclaimer_html, unsafe_allow_html=True)
        

    if not api_key:
        st.info("Informe a chave API na lateral.")
        return

    # Serviço Gemini 
    langchain_gemini_service = LangchainGeminiService(api_key)

    # State Management
    if "lista_dados" not in st.session_state: st.session_state.lista_dados = []
    if "form_data" not in st.session_state: st.session_state.form_data = {"produto": "", "preco": 0.0, "unidade": "un", "img_b64": ""}
    if "zoom_image" not in st.session_state: st.session_state.zoom_image = None

    if st.session_state.zoom_image:
        st.subheader(f"🖼️ Foto: {st.session_state.zoom_image['nome']}")
        st.image(base64.b64decode(st.session_state.zoom_image['b64']), use_container_width=True)
        if st.button("⬅️ Voltar"):
            st.session_state.zoom_image = None
            st.rerun()
        return

    tab1, tab2 = st.tabs(["📸 Adicionar Produto", "📋 Analisar compra"])

    # Área de envio cadastro etiquetas
    with tab1:
        total_atual = sum(item["Subtotal Est."] for item in st.session_state.lista_dados)
                
        header_tab1 = f"""
            <div class="valor-total-flex">
                <div style="text-align: right; min-width: 120px; width: 100%;">
                    <span class="label-carrinho">💰 Total no Carrinho</span><br>
                    <strong class="valor-carrinho">{formatar_moeda(total_atual)}</strong>
                </div>
            </div>
        """
        st.markdown(header_tab1, unsafe_allow_html=True)
        modo = st.radio("Opções de entrada:", ["Câmera de Trás", "Upload manual"], index=1, horizontal=True, key="m_g")
        
        img_etiqueta = back_camera_input(key="c_g") if modo == "Câmera de Trás" else st.file_uploader("Upload", key="u_g")
        
        if img_etiqueta and ("last_g" not in st.session_state or st.session_state.last_g != img_etiqueta):
            with st.spinner("Lendo etiqueta..."):
                res, b64 = langchain_gemini_service.verifica_etiqueta(Image.open(img_etiqueta))
                if "N/A" in res:
                    st.session_state.toast_msg = {"texto": "Não identifiquei o preço.", "icon": "⚠️"}
                else:
                    p = re.search(r'<p>(.*?)</p>', res, re.I|re.S)
                    v = re.search(r'<v>(.*?)</v>', res, re.I|re.S)
                    u = re.search(r'<u>(.*?)</u>', res, re.I|re.S)
                    st.session_state.form_data = {
                        "produto": p.group(1).strip() if p else "",
                        "preco": float(v.group(1).replace('R$', '').replace(',', '.').strip()) if v else 0.0,
                        "unidade": u.group(1).strip().lower() if u else "un",
                        "img_b64": b64
                    }
                    st.session_state.toast_msg = {"texto": "Preço capturado!", "icon": "✨"}
                st.session_state.last_g = img_etiqueta
                st.rerun()

        with st.form("confirm_form", clear_on_submit=True):
            nome_in = st.text_input("Produto", value=st.session_state.form_data["produto"])
            c1, c2, c3 = st.columns([2, 1, 1])
            preco_in = c1.number_input("Preço Prateleira (R$)", value=st.session_state.form_data["preco"], format="%.2f")
            qtd_in = c2.number_input("Qtd", min_value=0.1, value=1.0, step=0.1)
            unid_in = c3.selectbox("Unidade", ["un", "kg", "g", "L", "ml"], index=0)
            
            if st.form_submit_button("✅ Adicionar"):
                if nome_in:
                    agora = datetime.now()
                    st.session_state.lista_dados.append({
                        "id": agora.timestamp(),
                        "timestamp": agora,
                        "Adicionado em": agora.strftime("%d/%m/%Y %H:%M:%S"),
                        "Produto": nome_in, 
                        "Preço Prateleira": preco_in, 
                        "Qtd": qtd_in, 
                        "Unidade": unid_in, 
                        "Subtotal Est.": preco_in * qtd_in,
                        "_img_b64": st.session_state.form_data["img_b64"]
                    })
                    st.session_state.toast_msg = {"texto": f"{nome_in} adicionado a lista!", "icon": "🛒"}
                    st.session_state.form_data = {"produto": "", "preco": 0.0, "unidade": "un", "img_b64": ""}
                    st.rerun()
                            
                    
    # Área de inspeção da nota
    with tab2:
        if st.session_state.lista_dados:
            st.markdown('<div class="sub-header">📋 Itens no Carrinho</div>', unsafe_allow_html=True)
            df = pd.DataFrame(st.session_state.lista_dados).sort_values(by="timestamp", ascending=False)
            df.index = range(1, len(df) + 1)
            
            df_display = df.drop(columns=['_img_b64', 'timestamp']).copy()
            df_display["Preço Prateleira"] = df_display["Preço Prateleira"].apply(formatar_moeda)
            df_display["Subtotal Est."] = df_display["Subtotal Est."].apply(formatar_moeda)
                                                
            # --- CONFIGURAÇÃO DE ESTILO E PROPORÇÕES ---
            estilos_colunas = [
                {'selector': '', 'props': [('width', '100%'), ('border-collapse', 'collapse')]},
                {'selector': 'th', 'props': [('background-color', '#f0f2f6'), ('color', '#31333F'), ('font-weight', 'bold'), ('text-align', 'center'), ('padding', '12px'), ('font-size', 'clamp(0.8rem, 2.5vw, 1rem)')]},
                {'selector': 'td', 'props': [('padding', '12px'), ('border-bottom', '1px solid #e6e9ef'), ('font-size', 'clamp(0.75rem, 2.5vw, 0.95rem)')]},
                
                # Seletores individuais para garantir largura e alinhamento
                {'selector': 'th:nth-child(1), td:nth-child(1)', 'props': [('width', '5%'), ('text-align', 'center')]},
                {'selector': 'th:nth-child(2), td:nth-child(2)', 'props': [('width', '5%'), ('display', 'none')]},
                {'selector': 'th:nth-child(3), td:nth-child(3)', 'props': [('width', '15%'), ('text-align', 'center')]},
                {'selector': 'th:nth-child(4), td:nth-child(4)', 'props': [('width', '35%'), ('text-align', 'left')]},
                {'selector': 'th:nth-child(5), td:nth-child(5)', 'props': [('width', '12%'), ('text-align', 'right')]},
                {'selector': 'th:nth-child(6), td:nth-child(6)', 'props': [('width', '8%'), ('text-align', 'right')]},
                {'selector': 'th:nth-child(7), td:nth-child(7)', 'props': [('width', '8%'), ('text-align', 'center')]},
                {'selector': 'th:nth-child(8), td:nth-child(8)', 'props': [('width', '17%'), ('text-align', 'right')]}
            ]

            # Gerar o HTML com a formatação
            html_tabela = df_display.style.set_table_styles(estilos_colunas)\
                .format({
                    "Qtd": "{:,.3f}".format
                }, decimal=',', thousands='.')\
                .to_html(escape=False)           

            # Exibição
            st.write(f'<div class="table-container-mobile">{html_tabela}</div>', unsafe_allow_html=True)
            
            # Totalizador
            total_html = f"""              
                <div class="valor-total-flex">
                    <div style="text-align: right; min-width: 120px; width: 100%;">
                        <span class="label-carrinho">💰 Total no Carrinho</span><br>
                        <strong class="valor-carrinho">{formatar_moeda(df["Subtotal Est."].sum())}</strong>
                    </div>
                </div>
            """
            st.markdown(total_html, unsafe_allow_html=True)
            
            ver_idx_ajustado = st.selectbox("Visualizar foto do item:", range(len(df)), format_func=lambda x: f"{df.iloc[x]['Produto']} ({df.iloc[x]['Adicionado em']})")
            if st.button("👁️ Ver Foto", use_container_width=True):
                item = df.iloc[ver_idx_ajustado]
                
                # checa se existe imagem antes de mostrar
                if "_img_b64" in item and item["_img_b64"]:
                    st.session_state.zoom_image = {
                        "b64": item["_img_b64"], 
                        "nome": item["Produto"], 
                        "data": item["Adicionado em"]
                    }
                    st.rerun()
                else:
                    st.warning(f"O item '{item['Produto']}' foi adicionado manualmente e não possui imagem.")
            
            st.divider()
            
            # Analise e comparação de Nota Fiscal com etiquetas
            st.markdown('<div class="sub-header">🔍 Conferência de preços</div>', unsafe_allow_html=True)
            
            modo_c = st.radio("Informe a Nota Fiscal:", ["Câmera de Trás", "Upload manual"], index=1, horizontal=True, key="m_c")
            nota_f = back_camera_input(key="c_c") if modo_c == "Câmera de Trás" else st.file_uploader("Upload manual", key="u_c")
            
            if nota_f and ("last_c" not in st.session_state or st.session_state.last_c != nota_f):
                with st.spinner("Comparando..."):
                    xml = langchain_gemini_service.comparar_nota_etiquetas(df, Image.open(nota_f))
                    items = re.findall(r'<item>(.*?)</item>', xml, re.S)
                    res_c = []
                    for it in items:
                        n = re.search(r'<n>(.*?)</n>', it, re.S)
                        s = re.search(r'<s>(.*?)</s>', it, re.S)
                        d = re.search(r'<d>(.*?)</d>', it, re.S)
                        res_c.append({
                            "Produto": n.group(1).strip() if n else "", 
                            "Status": s.group(1).strip() if s else "", 
                            "Observação": d.group(1).strip() if d else ""
                        })
                    st.session_state.res_comp = res_c
                    st.session_state.last_c = nota_f
                    st.session_state.toast_msg = {"texto": "Comparação concluída!", "icon": "📊"}
                    st.rerun()

            if "res_comp" in st.session_state:
                res_df = pd.DataFrame(st.session_state.res_comp)                
                total_ok = len(res_df[res_df['Status'] == 'OK'])
                total_div = len(res_df[res_df['Status'] != 'OK'])

                header_resultado = f"""
                    <div id="resultado">
                        <div class="sub-header" style="margin:0;">🖳 Resultado</div>
                        <div style="display: flex; gap: 15px;">
                            <span style="color: #28a745; font-weight: 900; font-size: clamp(1rem, 4vw, 1.2rem);">
                                OK: {total_ok}
                            </span>
                            <span style="color: #dc3545; font-weight: 900; font-size: clamp(1rem, 4vw, 1.2rem);">
                                Divergência: {total_div}
                            </span>
                        </div>
                    </div>
                """
                st.markdown(header_resultado, unsafe_allow_html=True)

                st.dataframe(
                    res_df.style.map(mensagem_erro_df, subset=['Status']), 
                    use_container_width=True,
                    hide_index=True 
                )

                # Só vai aparecer após analisar
                if st.button("🗑️ Limpar", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()
        else:
            st.info("Carrinho vazio.")

if __name__ == "__main__":
    main()