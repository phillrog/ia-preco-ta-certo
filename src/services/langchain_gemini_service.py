import base64
import io
import pandas as pd
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class LangchainGeminiService:
    def __init__(self, api_key: str, log_callback=None):
        self.llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", google_api_key=api_key)
        self.log_callback = log_callback

    def _enviar_log(self, mensagem, tipo="info"):
        """Método interno para disparar o callback de log se ele existir"""
        if self.log_callback:
            self.log_callback(mensagem, tipo)

    def _converter_img_base64(self, image: Image):
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def verifica_etiqueta(self, image: Image):
        img_base64 = self._converter_img_base64(image)
        prompt = (
            "Analise esta etiqueta de preço. Retorne APENAS: "
            "<p>Nome do Produto + Peso/Unidade</p> <v>Preço</v> <u>Unidade (kg, un, g)</u>. "
            "<v>Preço (ex: 14,99)</v> "
            "<ve>Preço por extenso (ex: quatorze reais e noventa e nove centavos)</ve> "
            "<u>Unidade (kg, un, g)</u>. "
            "Se não encontrar, retorne <p>N/A</p>"
        )
        
        # Enviando Prompt
        self._enviar_log(f"PROMPT ETIQUETA: {prompt}", "ai_in")

        message = HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ])
        
        response = self.llm.invoke([message])
        resposta_texto = str(response.content)

        # Recebendo Resposta
        self._enviar_log(f"RESPOSTA ETIQUETA: {resposta_texto}", "ai_out")
        
        return resposta_texto, img_base64

    def comparar_nota_etiquetas(self, df_carrinho, imagem_nota: Image):
        img_base64 = self._converter_img_base64(imagem_nota)
        
        # Prepara a lista
        lista_itens = df_carrinho[['id', 'Produto', 'Preço Prateleira', 'Qtd', 'Unidade']].to_dict(orient='records')
        
        # XML Tagging
        prompt = f"""
        Você é um AUDITOR DE PREÇOS RIGOROSO. Sua missão é cruzar os dados da prateleira com o cupom fiscal.

        <contexto_lista_prateleira>
        {lista_itens}
        </contexto_lista_prateleira>

        <instrucoes_auditoria>
        ### PRIORIDADE DE ANÁLISE
        1. ANALISE UNITÁRIA: Processe cada item dentro de <contexto_lista_prateleira> individualmente.
        2. CONFERÊNCIA DE REPETIDOS: Se houver produtos idênticos, valide cada ocorrência separadamente contra o cupom fiscal.
        
        ### REGRAS DE PREÇO E OFERTA
        3. PREÇO DE VAREJO FINAL: Extraia o preço unitário para o consumidor comum.
        4. FOCO NA OFERTA GERAL: Se houver um preço 'DE/POR', pegue o 'POR' (valor promocional vigente para todos).
        5. IGNORAR FIDELIDADE E CLUBES: Ignore preços que exijam condições especiais, como 'PREÇO EXCLUSIVO CARTÃO DA LOJA', 'SÓ PARA CLIENTE MAIS' ou 'CLUBE DE FIDELIDADE'. Pegue sempre o preço de prateleira para o público geral.
        6. IGNORAR ATACADO: Ignore preços do tipo 'Leve 3 Pague 2' ou 'A partir de X unidades'.
        
        ### CRITÉRIOS DE STATUS
        7. PREÇO EXATO: Compare centavo por centavo. Qualquer divergência gera Status 'ERRO DE PREÇO'.
        8. PREÇO EXATO: Compare centavo por centavo com o cupom fiscal. Diferenças geram Status 'ERRO DE PREÇO'.

        ### FORMATAÇÃO DA RESPOSTA
        9. FORMATAÇÃO DE MOEDA: Use o padrão brasileiro (R$ 0,00) com vírgula para centavos nas descrições.
        10. PADRÃO DE TEXTO: Retorne nomes e observações em letras MAIÚSCULAS (UPPERCASE).
        11. PADRÃO DE OBSERVAÇÃO: A tag <d> deve seguir rigorosamente este modelo:
           - Se estiver correto: "PRATELEIRA R$ X,XX | CUPOM R$ X,XX - NÃO HOUVE DIVERGÊNCIA"
           - Se houver erro: "PRATELEIRA R$ X,XX | CUPOM R$ Y,YY - DIVERGÊNCIA DE R$ Z,ZZ"
           - Se não encontrar: "PRODUTO NÃO LOCALIZADO NO CUPOM FISCAL"
        </instrucoes_auditoria>
        12. TOTAL POR EXTENSO: Adicione a tag <te> contendo o valor de <total_nota> por extenso (ex: VINTE REAIS E CINQUENTA CENTAVOS).

        <formato_saida_esperado>
        Retorne a resposta estritamente no formato XML abaixo. 
        Não adicione texto antes ou depois do XML:

        <resultado>
            <itens>
                <item>
                    <n>NOME DO PRODUTO</n>
                    <s>STATUS (Use apenas: OK, ERRO DE PREÇO ou NÃO ENCONTRADO)</s>
                    <d>PRATELEIRA R$ X,XX | CUPOM R$ Y,YY - [MENSAGEM]</d>
                </item>
            </itens>
            <total_nota>VALOR_TOTAL_PAGO_NO_CUPOM</total_nota>
            <te>VALOR POR EXTENSO AQUI</te>
        </resultado>
        </formato_saida_esperado>
        """

        self._enviar_log(f"PROMPT AUDITORIA ENVIADO (Contexto + Instruções): {prompt}", "ai_in")

        message = HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ])
        
        response = self.llm.invoke([message])
        resposta_texto = str(response.content)

        self._enviar_log(f"XML RECEBIDO: {resposta_texto}", "ai_out")
        
        return resposta_texto