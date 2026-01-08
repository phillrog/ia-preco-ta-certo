import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
from streamlit_back_camera_input import back_camera_input
from utils.utils import formatar_moeda, gerar_pdf_direto
from controllers.processador_ia import processar_resposta

def render_tab_analisar(service, adicionar_log_fn):
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
                "Preço Prateleira": st.column_config.NumberColumn("Preço", format="R$ %.2f"),
                "Subtotal Est.": st.column_config.NumberColumn("Subtotal", format="R$ %.2f"),
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
                adicionar_log_fn(f"Removidos {len(ids_remover)} itens.")
                st.session_state.toast_msg = {"texto": "Item removido!", "icon": "🛒"}
                st.rerun()

        total_valor = sum(item["Subtotal Est."] for item in st.session_state.lista_dados)
        st.markdown(f'<div class="valor-total-flex"><div style="text-align: right; width: 100%;"><span class="label-carrinho">💰 Total no Carrinho</span><br><strong class="valor-carrinho">{formatar_moeda(total_valor)}</strong></div></div>', unsafe_allow_html=True)
        
        df_atualizado = pd.DataFrame(st.session_state.lista_dados).sort_values(by="timestamp", ascending=False)
        ver_idx = st.selectbox("Visualizar foto do item:", range(len(df_atualizado)), format_func=lambda x: f"{df_atualizado.iloc[x]['Produto']} ({df_atualizado.iloc[x]['Adicionado em']})")
        
        if st.button("👁️ Ver Foto", use_container_width=True):
            item = df_atualizado.iloc[ver_idx]
            if "_img_b64" in item and item["_img_b64"]:
                st.session_state.zoom_image = {"b64": item["_img_b64"], "nome": item["Produto"], "data": item["Adicionado em"]}
                st.rerun()

        st.divider()
        st.markdown('<div class="sub-header">🔍 Conferência de preços</div>', unsafe_allow_html=True)
        modo_c = st.radio("Informe a Nota Fiscal:", ["Câmera de Trás", "Upload manual"], index=1, horizontal=True, key="m_c")
        nota_f = back_camera_input(key="c_c") if modo_c == "Câmera de Trás" else st.file_uploader("Upload manual", key="u_c")
        
        if nota_f and ("last_c" not in st.session_state or st.session_state.last_c != nota_f):
            adicionar_log_fn("ANÁLISE: Enviando lista de etiquetas e foto do cupom para IA.", "ai_in")
            with st.spinner("Comparando..."):
                try:
                    img_cupom_b64 = service._converter_img_base64(Image.open(nota_f))
                    st.session_state.img_cupom_b64 = img_cupom_b64
                    xml = service.comparar_nota_etiquetas(pd.DataFrame(st.session_state.lista_dados), Image.open(nota_f))
                    adicionar_log_fn(f"RESPOSTA ANÁLISE (XML): {xml}", "ai_out")
                    
                    total_lido, res_c = processar_resposta(xml)
                    st.session_state.total_cupom_lido = total_lido
                    st.session_state.res_comp = res_c
                    st.session_state.last_c = nota_f
                    st.session_state.toast_msg = {"texto": "Conferência concluída!", "icon": "📊"}
                    st.rerun()
                except Exception as e:
                    adicionar_log_fn(f"ERRO COMPARAÇÂO: {str(e)}", "error")

        if "res_comp" in st.session_state:
            _render_resultado_comparacao(total_valor)
    else:
        st.info("Carrinho vazio.")

def _render_resultado_comparacao(total_carrinho):
    res_df = pd.DataFrame(st.session_state.res_comp)
    total_ok = len(res_df[res_df['Status'] == 'OK'])
    total_div = len(res_df[res_df['Status'] != 'OK'])
    
    st.markdown(f"""<div id="resultado"><div class="sub-header" style="margin:0;">🖳 Resultado</div>
        <div style="display: flex; gap: 15px;">
            <span style="color: #28a745; font-weight: 900;">✅ OK: {total_ok}</span>
            <span style="color: #dc3545; font-weight: 900;">❌ Divergência: {total_div}</span>
        </div></div>""", unsafe_allow_html=True)

    st.dataframe(res_df.style.map(lambda v: 'background-color: #d4edda;' if v == 'OK' else 'background-color: #f8d7da;', subset=['Status']), use_container_width=True, hide_index=True)
    
    total_cupom = st.session_state.get("total_cupom_lido", 0.0)
    st.markdown('<div class="sub-header">⚖️ Validação de Totais</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Soma do Carrinho", formatar_moeda(total_carrinho))
    c2.metric("Total no Cupom", formatar_moeda(total_cupom), delta=formatar_moeda(total_cupom - total_carrinho), delta_color="inverse")

    if abs(total_carrinho - total_cupom) < 0.01:
        st.success("✅ **Os totais coincidem!**")
        st.balloons()
    else:
        st.error(f"⚠️ **Divergência:** Diferença de {formatar_moeda(abs(total_carrinho - total_cupom))}")

    st.divider()
    pdf_bytes = gerar_pdf_direto(st.session_state.lista_dados, total_carrinho, total_cupom, st.session_state.get("img_cupom_b64", ""))
    st.download_button(label="📥 Baixar Relatório PDF", data=pdf_bytes, file_name=f"ia_ta_certo_relatorio_compra_{datetime.now().strftime('%d%m%Y')}.pdf", mime="application/pdf", use_container_width=True)