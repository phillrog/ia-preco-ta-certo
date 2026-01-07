import base64
import io
import pandas as pd
from PIL import Image
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

class LangchainGeminiService:
    def __init__(self, api_key: str):
        self.llm = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", google_api_key=api_key)

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
            "Se não encontrar, retorne <p>N/A</p>"
        )
        message = HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ])
        response = self.llm.invoke([message])
        return str(response.content), img_base64

    def comparar_nota_etiquetas(self, df_carrinho, imagem_nota: Image):
        img_base64 = self._converter_img_base64(imagem_nota)
        
        # Prepara a lista
        lista_itens = df_carrinho[['id', 'Produto', 'Preço Prateleira', 'Qtd', 'Unidade']].to_dict(orient='records')
        
        # XML Tagging
        prompt = f"""
        Você é um auditor de preços rigoroso. Sua tarefa é realizar o cruzamento de dados entre os itens da prateleira e o cupom fiscal.

        <contexto_lista_prateleira>
        {lista_itens}
        </contexto_lista_prateleira>

        <instrucoes_auditoria>
        1. ANALISE UNITÁRIA: Processe cada item dentro de <contexto_lista_prateleira> individualmente.
        2. CONFERÊNCIA DE REPETIDOS: Se houver produtos idênticos, valide cada ocorrência separadamente contra o cupom fiscal.
        3. PREÇO EXATO: Compare centavo por centavo. Qualquer divergência gera Status 'ERRO DE PREÇO'.
        4. FORMATAÇÃO DE MOEDA: Use o padrão brasileiro (R$ 0,00) com vírgula para centavos nas descrições.
        5. PADRÃO DE OBSERVAÇÃO: A tag <d> deve seguir rigorosamente este modelo:
        - Se estiver correto: "PRATELEIRA R$ X,XX | CUPOM R$ X,XX - Não houve divergência"
        - Se houver erro: "PRATELEIRA R$ X,XX | CUPOM R$ Y,YY - Divergência de R$ Z,ZZ"
        - Se não encontrar: "Produto não localizado no cupom fiscal"
        </instrucoes_auditoria>

        <formato_saida_esperado>
        Retorne APENAS tags XML:
        <item>
            <n>Nome do Produto</n>
            <s>Status (OK, ERRO DE PREÇO, NÃO ENCONTRADO)</s>
            <d>PRATELEIRA R$ X,XX | CUPOM R$ Y,YY - [Mensagem]</d>
        </item>
        </formato_saida_esperado>
        """

        message = HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ])
        
        response = self.llm.invoke([message])
        return str(response.content)        