import streamlit as st
import re
import base64
import pandas as pd
from PIL import Image
from datetime import datetime
from streamlit_back_camera_input import back_camera_input

from services.langchain_gemini_service import LangchainGeminiService
from utils.utils import carregar_css, formatar_moeda, mensagem_erro_df, carregar_imagem_base64, gerar_pdf_direto

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
        st.markdown(f'<div class="sub-header">🖼️ {st.session_state.zoom_image['nome']}</div>', unsafe_allow_html=True)
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
            with st.spinner("Analisando... Por favor aguarde!"):
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
            
            df_base = pd.DataFrame(st.session_state.lista_dados).sort_values(by="timestamp", ascending=False)
            df_base.insert(0, "#", range(1, len(df_base) + 1))
            
            df_exibicao = df_base.drop(columns=['_img_b64', 'timestamp']).copy()
            df_exibicao["Remover"] = False

            df_editado = st.data_editor(
                df_exibicao,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": None,
                    "#": st.column_config.NumberColumn("Item", width="small"),
                    "Produto": st.column_config.TextColumn("Produto", width="large"),
                    "Preço Prateleira": st.column_config.NumberColumn("Preço", format="R$ %.2f"),
                    "Subtotal Est.": st.column_config.NumberColumn("Subtotal", format="R$ %.2f"),
                    "Qtd": st.column_config.NumberColumn("Qtd", format="%.3f"),
                    "Remover": st.column_config.CheckboxColumn("Excluir?", default=False),
                },
                disabled=["#", "Produto", "Preço Prateleira", "Qtd", "Unidade", "Subtotal Est.", "Adicionado em"],
                key="tabela_carrinho"
            )

            itens_para_excluir = df_editado[df_editado["Remover"] == True]
            
            if not itens_para_excluir.empty:
                if st.button(f"🗑️ Confirmar Remoção ({len(itens_para_excluir)})", use_container_width=True, type="primary"):
                    ids_remover = itens_para_excluir["id"].tolist()
                    st.session_state.lista_dados = [item for item in st.session_state.lista_dados if item["id"] not in ids_remover]
                    st.session_state.toast_msg = {"texto": "Item removido!", "icon": "🛒"}
                    st.rerun()

            total_valor = sum(item["Subtotal Est."] for item in st.session_state.lista_dados)
            total_html = f"""              
                <div class="valor-total-flex">
                    <div style="text-align: right; min-width: 120px; width: 100%;">
                        <span class="label-carrinho">💰 Total no Carrinho</span><br>
                        <strong class="valor-carrinho">{formatar_moeda(total_valor)}</strong>
                    </div>
                </div>
            """
            st.markdown(total_html, unsafe_allow_html=True)
            
            df_atualizado = pd.DataFrame(st.session_state.lista_dados).sort_values(by="timestamp", ascending=False)
            
            ver_idx_ajustado = st.selectbox(
                "Visualizar foto do item:", 
                range(len(df_atualizado)), 
                format_func=lambda x: f"{df_atualizado.iloc[x]['Produto']} ({df_atualizado.iloc[x]['Adicionado em']})"
            )
            
            if st.button("👁️ Ver Foto", use_container_width=True):
                item = df_atualizado.iloc[ver_idx_ajustado]
                if "_img_b64" in item and item["_img_b64"]:
                    st.session_state.zoom_image = {
                        "b64": item["_img_b64"], 
                        "nome": item["Produto"], 
                        "data": item["Adicionado em"]
                    }
                    st.rerun()
                else:
                    st.warning(f"O item '{item['Produto']}' não possui imagem.")
            
            st.divider()
            
            # Analise e comparação de Nota Fiscal com etiquetas
            st.markdown('<div class="sub-header">🔍 Conferência de preços</div>', unsafe_allow_html=True)
            
            modo_c = st.radio("Informe a Nota Fiscal:", ["Câmera de Trás", "Upload manual"], index=1, horizontal=True, key="m_c")
            nota_f = back_camera_input(key="c_c") if modo_c == "Câmera de Trás" else st.file_uploader("Upload manual", key="u_c")
            
            if nota_f and ("last_c" not in st.session_state or st.session_state.last_c != nota_f):
                with st.spinner("Comparando... Por favor aguarde!"):
                    # Para exportação
                    img_cupom_b64 = langchain_gemini_service._converter_img_base64(Image.open(nota_f))
                    st.session_state.img_cupom_b64 = img_cupom_b64
                    
                    st.session_state.total_cupom_lido = 0.0
                    df_para_comparar = pd.DataFrame(st.session_state.lista_dados)
                    
                    xml = langchain_gemini_service.comparar_nota_etiquetas(df_para_comparar, Image.open(nota_f))
                    match_total = re.search(r'<total_nota>(.*?)</total_nota>', xml, re.S)
                    if match_total:
                        try:
                            txt_total = match_total.group(1).upper().replace('R$', '').replace(' ', '')
                            txt_total = txt_total.replace('.', '').replace(',', '.')
                            st.session_state.total_cupom_lido = float(txt_total)
                        except:
                            st.session_state.total_cupom_lido = 0.0
                            
                    items = re.findall(r'<item>(.*?)</item>', xml, re.S)
                    res_c = []
                    for it in items:
                        n = re.search(r'<n>(.*?)</n>', it, re.S)
                        s = re.search(r'<s>(.*?)</s>', it, re.S)
                        d = re.search(r'<d>(.*?)</d>', it, re.S)
                        
                        status_texto = s.group(1).strip().upper() if s else "NÃO ENCONTRADO"
                        
                        res_c.append({
                            "Produto": n.group(1).strip() if n else "", 
                            "Status": status_texto, 
                            "Observação": d.group(1).strip() if d else ""
                        })
                    
                    st.session_state.res_comp = res_c
                    st.session_state.last_c = nota_f
                    st.session_state.toast_msg = {"texto": "Conferência concluída!", "icon": "📊"}
                    st.rerun()

            if "res_comp" in st.session_state:
                res_df = pd.DataFrame(st.session_state.res_comp)                
                total_ok = len(res_df[res_df['Status'] == 'OK'])
                total_div = len(res_df[res_df['Status'] != 'OK'])
                
                def colorir_status(val):
                    if val == 'OK':
                        return 'background-color: #d4edda; color: #155724; font-weight: bold;'
                    else:
                        return 'background-color: #f8d7da; color: #721c24; font-weight: bold;'

                header_resultado = f"""
                    <div id="resultado">
                        <div class="sub-header" style="margin:0;">🖳 Resultado</div>
                        <div style="display: flex; gap: 15px;">
                            <span style="color: #28a745; font-weight: 900; font-size: clamp(1rem, 4vw, 1.2rem);">
                               ✅ OK: {total_ok}
                            </span>
                            <span style="color: #dc3545; font-weight: 900; font-size: clamp(1rem, 4vw, 1.2rem);">
                               ❌ Divergência: {total_div}
                            </span>
                        </div>
                    </div>
                """
                st.markdown(header_resultado, unsafe_allow_html=True)

                df_estilizado = res_df.style.map(colorir_status, subset=['Status'])
                
                st.dataframe(
                    df_estilizado,
                    use_container_width=True,
                    hide_index=True 
                )
                
                total_carrinho = sum(item["Subtotal Est."] for item in st.session_state.lista_dados)
                               
                total_cupom = st.session_state.get("total_cupom_lido", 0.0) 

                st.markdown('<div class="sub-header">⚖️ Validação de Totais</div>', unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                c1.metric("Soma do Carrinho", formatar_moeda(total_carrinho))
                c2.metric("Total no Cupom", formatar_moeda(total_cupom), 
                          delta=formatar_moeda(total_cupom - total_carrinho), 
                          delta_color="inverse")

                diferenca = abs(total_carrinho - total_cupom)
                
                if diferenca < 0.01:
                    st.success("✅ **Os totais coincidem perfeitamente!**")
                    st.balloons()
                else:
                    st.error(f"⚠️ **Divergência no Valor Total:** Há uma diferença de {formatar_moeda(diferenca)} entre o carrinho e o cupom.")
                    st.warning("""
                        **Possíveis causas:**
                        * Taxas de serviço ou embalagem não computadas.
                        * Descontos aplicados no fechamento do cupom.
                        * Erro na leitura de algum item específico pela IA.
                    """)

                st.divider()
                
                st.markdown('<div class="sub-header">📄 Exportar para .pdf</div>', unsafe_allow_html=True)
                
                # Prepara o arquivo
                pdf_bytes = gerar_pdf_direto(
                    st.session_state.lista_dados, 
                    total_carrinho, 
                    total_cupom,
                    st.session_state.get("img_cupom_b64", "")
                )
                
                st.download_button(
                    label="📥 Baixar Relatório PDF",
                    data=pdf_bytes,
                    file_name=f"relatorio_compra_{datetime.now().strftime('%d%m%Y_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                if st.button("🗑️ Limpar", use_container_width=True):
                    st.session_state.clear()
                    st.rerun()
        else:
            st.info("Carrinho vazio.")

if __name__ == "__main__":
    main()