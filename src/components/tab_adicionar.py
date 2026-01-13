import streamlit as st
from PIL import Image
from datetime import datetime
from streamlit_back_camera_input import back_camera_input
from utils.utils import formatar_moeda
from controllers.processador_ia import extrair_dados_etiqueta, valor_por_extenso

def render_tab_adicionar(service, voz_service, adicionar_log_fn):
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
        with st.spinner("Processando... Por favor aguarde!"):
            try:
                res, b64 = service.verifica_etiqueta(Image.open(img_etiqueta))
                adicionar_log_fn(f"RESPOSTA IA: {res}", "ai_out")
                
                if "N/A" in res:
                    st.session_state.toast_msg = {"texto": "Não identifiquei o preço.", "icon": "⚠️"}
                else:
                    p, v, u, v_extenso = extrair_dados_etiqueta(res)
                    
                    produto_nome = p.group(1).strip() if p else "Produto desconhecido"
                    preco_valor = v.group(1).strip() if v else "zero"
                    texto_narra = f"{produto_nome}, {v_extenso}"
                    
                    # Chamada síncrona do áudio
                    audio_b64 = voz_service.gerar_audio_base64(texto_narra)
                    if audio_b64:
                        st.session_state.audio_confirmacao = audio_b64
                    
                    st.session_state.form_data = {
                        "produto": p.group(1).strip() if p else "",
                        "preco": float(v.group(1).replace('R$', '').replace(',', '.').strip()) if v else 0.0,
                        "unidade": u.group(1).strip().lower() if u else "un",
                        "img_b64": b64
                    }
                    st.session_state.toast_msg = {"texto": "Preço capturado!", "icon": "✨"}
                st.session_state.last_g = img_etiqueta
                st.rerun()
            except Exception as e:
                adicionar_log_fn(f"ERRO: {str(e)}", "error")

    # Bloco de Reprodução de Áudio
    if "audio_confirmacao" in st.session_state and st.session_state.audio_confirmacao:
        st.markdown("📣 **Audio disponível**")
        audio_html = f"""
            <audio autoplay="true" controls style="width: 100%; height: 40px;">
                <source src="data:audio/mp3;base64,{st.session_state.audio_confirmacao}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
        st.session_state.audio_confirmacao = None
        del st.session_state.audio_confirmacao
        
    with st.form("confirm_form", clear_on_submit=True):
        nome_in = st.text_input("Produto", value=st.session_state.form_data["produto"])
        c1, c2, c3 = st.columns([2, 1, 1])
        preco_in = c1.number_input("Preço Prateleira (R$)", value=st.session_state.form_data["preco"], format="%.2f")
        qtd_in = c2.number_input("Qtd", min_value=0.1, value=1.0, step=0.1)
        unid_in = c3.selectbox("Unidade", ["un", "kg", "g", "L", "ml"], index=0)
        
        if st.form_submit_button("✅ Adicionar", use_container_width=True):
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
                adicionar_log_fn(f"Carrinho atualizado: +1 {nome_in}")
                st.session_state.toast_msg = {"texto": f"{nome_in} adicionado a lista!", "icon": "🛒"}
                st.session_state.form_data = {"produto": "", "preco": 0.0, "unidade": "un", "img_b64": ""}
                st.rerun()