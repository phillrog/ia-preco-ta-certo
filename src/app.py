import streamlit as st
import base64
from services.langchain_gemini_service import LangchainGeminiService
from utils.utils import carregar_css, carregar_imagem_base64
from components.sidebar import renderizar_sidebar, adicionar_log
from components.tab_adicionar import render_tab_adicionar
from components.tab_analisar import render_tab_analisar
from services.voz_edge_service import VozEdgeService

def main():
    st.set_page_config(page_title="IA Preço Tá Certo ?", layout="wide")
    carregar_css('assets/styles.css')
    
    # Inicializa o serviço de voz no session_state para persistência
    if "voz_service" not in st.session_state:
        st.session_state.voz_service = VozEdgeService()

    logo_b64 = carregar_imagem_base64('assets/logo_carrinho.png')
    if logo_b64:
        header_html = f"""<div id="logo"><img src="data:image/png;base64,{logo_b64}"><div>
                    <div class="header" style="margin: 0; line-height: 1.2;">IA Preço Tá Certo ?</div>
                    <div class="titulo-projeto" style="margin: 0; line-height: 1.2;">🛒 Assistente de Compras Inteligente</div>
                </div></div>"""
        st.markdown(header_html, unsafe_allow_html=True)
    else:
        st.markdown('<div class="header">IA Preço Tá Certo ?</div>', unsafe_allow_html=True)
        st.markdown('<div class="titulo-projeto">🛒 Assistente de Compras Inteligente</div>', unsafe_allow_html=True)
      
    if "toast_msg" in st.session_state and st.session_state.toast_msg:
        st.toast(st.session_state.toast_msg["texto"], icon=st.session_state.toast_msg["icon"])
        st.session_state.toast_msg = None 

    api_key = renderizar_sidebar()
    if not api_key:
        st.info("Informe a chave API na lateral.")
        return

    langchain_gemini_service = LangchainGeminiService(api_key, log_callback=adicionar_log)

    # State Management
    if "lista_dados" not in st.session_state: st.session_state.lista_dados = []
    if "form_data" not in st.session_state: st.session_state.form_data = {"produto": "", "preco": 0.0, "unidade": "un", "img_b64": ""}
    if "zoom_image" not in st.session_state: st.session_state.zoom_image = None
    if "logs" not in st.session_state: st.session_state.logs = []

    if st.session_state.zoom_image:
        st.markdown(f'<div class="sub-header">🖼️ {st.session_state.zoom_image["nome"]}</div>', unsafe_allow_html=True)
        st.image(base64.b64decode(st.session_state.zoom_image['b64']), use_container_width=True)
        if st.button("⬅️ Voltar"):
            st.session_state.zoom_image = None
            st.rerun()
        return

    tab1, tab2 = st.tabs(["📸 Adicionar Item", "📋 Analisar compra"])

    with tab1:
        # Passando o serviço de voz para a aba
        render_tab_adicionar(langchain_gemini_service, st.session_state.voz_service, adicionar_log)

    with tab2:
        render_tab_analisar(langchain_gemini_service, st.session_state.voz_service, adicionar_log)

if __name__ == "__main__":
    main()