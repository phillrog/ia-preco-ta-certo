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

    def comparar_nota_etiquetas(self, df_items: pd.DataFrame, imagem_nota: Image):
        img_base64 = self._converter_img_base64(imagem_nota)
        # Limpa o DataFrame
        cols_to_drop = [c for c in ['_img_b64', 'timestamp'] if c in df_items.columns]
        lista_texto = df_items.drop(columns=cols_to_drop).to_string(index=False)
        
        prompt = (
            f"Minha lista da prateleira (VALORES CORRETOS):\n{lista_texto}\n\n"
            "Analise da NOTA FISCAL anexo e compare com a minha lista. REGRAS:\n"
            "1. Compare o valor unitário (ou por kg) de cada item.\n"
            "2. Se o valor na NOTA FISCAL for MAIOR que o valor na PRATELEIRA, Status = 'ERRADO'.\n"
            "3. Se o valor no NOTA FISCAL for IGUAL ou MENOR que na PRATELEIRA, Status = 'OK'.\n"
            "4. Na Observação, coloque SEMPRE: 'PRATELEIRA: R$ X | NOTA FISCAL: R$ Y'.\n"
            "Retorne APENAS tags XML: <item><n>Nome</n><s>Status</s><d>Observação</d></item>"
        )
        message = HumanMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
        ])
        response = self.llm.invoke([message])
        return str(response.content)