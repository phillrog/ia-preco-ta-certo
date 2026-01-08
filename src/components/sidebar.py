import streamlit as st
from datetime import datetime

def adicionar_log(mensagem, tipo="info"):
    icon = "ℹ️" if tipo == "info" else "❌"
    if tipo == "ai_in": icon = "📤"
    if tipo == "ai_out": icon = "📥"
    hora = datetime.now().strftime("%H:%M:%S")
    if "logs" not in st.session_state:
        st.session_state.logs = []
    st.session_state.logs.append(f"[{hora}] {icon} {mensagem}")

def renderizar_sidebar():
    with st.sidebar:                    
        st.markdown('<div class="sub-header">⚙️ Configurações</div>', unsafe_allow_html=True)
        api_key = st.text_input("Gemini API Key", type="password")
        if st.button("🗑️ Limpar", use_container_width=True, key="btn_clear_sidebar"):
            adicionar_log("Sistema reiniciado pelo usuário.")
            st.session_state.clear()
            st.rerun()
       
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
        
        st.divider()
        st.subheader("🪵 Logs & Tráfego de IA")
        log_container = st.container(height=350)
        with log_container:
            if "logs" in st.session_state and st.session_state.logs:
                for log in reversed(st.session_state.logs):
                    st.caption(log)
            else:
                st.caption("Aguardando atividades...")
        return api_key