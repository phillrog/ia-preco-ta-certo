<img width="644" height="194" alt="Captura de tela 2026-01-07 160850" src="https://github.com/user-attachments/assets/e96a763d-276e-4cd4-b282-62a893511624" />


O **IA Preço Tá Certo?** é um assistente de compras inteligente que utiliza o poder multimodal do Google Gemini para ajudar você a acompanhar sua compra em tempo real. A ferramenta interpreta fotos de etiquetas para extrair descrições e valores, consolidando tudo em uma lista que mostra o valor aproximado a pagar. Além de organizar seus gastos, o assistente atua na conferência final: se ele encontrar algo estranho ou divergente entre os preços anotados e o cupom fiscal, ele irá te mostrar imediatamente para que você possa conferir.

# ⚠️ Disclaimer (Aviso de Uso)
Esta é uma ferramenta baseada em Inteligência Artificial Experimental. As análises fornecidas são sugestões educativas. O processamento de dados segue rigorosos filtros de privacidade locais, mas recomenda-se que o usuário valide todas as informações e consulte as políticas de privacidade do provedor (Google Gemini).

### **Como funciona ?** 
O usuário tira fotos das etiquetas nas prateleiras. A IA (Google Gemini) extrai automaticamente o nome do produto, o preço e a unidade (opcional) ou informa digitando manualmente os dados. Ao mesmo tempo o app organiza uma lista em tempo real com os itens adicionados, calculando subtotais e o total estimado da compra, exibindo tudo em uma tabela organizada e responsiva. 
Ao final, o usuário fotografa o cupom fiscal. A IA compara os preços registrados no caixa com os preços capturados nas etiquetas, alertando sobre qualquer divergência de valores.

## ✨ Funcionalidades

-   📸 **OCR de Etiquetas:** Captura automática de preços e nomes de produtos via câmera.
-   📋 **Carrinho Inteligente:** Gerenciamento de itens com cálculo automático de subtotais e totais.
-   🔍 **Conferência Automatizada:** Comparação inteligente entre os preços das etiquetas e o cupom fiscal emitido.
-   🖼️ **Histórico Visual:** Armazenamento temporário das fotos das etiquetas para conferência manual, se necessário.
-   📱 **Interface Responsiva:** Tabela de itens otimizada para visualização em dispositivos móveis.
-   🗎  **Registro de Atividade (Logs & Tráfego de IA):** Captura e exibição dos logs de execução.
-   💾 **Exportação de Relatório PDF:** Exporte para o formato .pdf toda a compra efetuada no assistente.

## 📊 Estrutura do Projeto
-----------------------

Plaintext

```
src/
├── assets/
│   ├── logo_carrinho.png       # logo
│   └── styles.css              # CSS (Shimmer, UI Responsiva)
├── components/
│   ├── sidebar.py              # Configurações, Disclaimer e Logs
│   ├── tab_adicionar.py        # Extrai dados das etiqueta ou preenche os dados
│   └── tab_analisar.py         # Vizualiza os itens e analisa a compra
├── controllers/
│   └── processador_ia.py       # Lógica de extração de dados (Regex e parsing de XML)
├── services/
│   └── langchain_gemini_service.py # Comunicação com a API Gemini e processamento de imagem
├── utils/
│   └── utils.py                # Utilitários (formatador de moeda, Base64 e gerador de PDF)
├── requirements.txt            # Lista de dependências (Streamlit, LangChain, FPDF, etc.)
└── app.py                      # Orquestrador principal e gerenciamento de estado (Session State)
```

## 🛠️ Tecnologias Utilizadas

-   **Linguagem:** Python 3.12.7
-   **Interface:** [Streamlit](https://streamlit.io/)
-   **IA:** [Google Gemini API](https://ai.google.dev/) (via LangChain)
-   **Processamento de Dados:** Pandas
-   **Estilização:** CSS

## 📚 Bibliotecas Utilizadas

-   **[Streamlit](https://streamlit.io/):** Framework principal para a criação da interface web reativa.
-   **[LangChain Google GenAI](https://python.langchain.com/docs/integrations/chat/google_generative_ai/):** Orquestração das chamadas ao modelo **Gemini 3 Flash**, permitindo o processamento multimodal (texto + imagem).
-   **[Pandas](https://pandas.pydata.org/):** Estruturação e manipulação da lista de compras em DataFrames para cálculos precisos.
-   **[Pillow (PIL)](https://www.google.com/search?q=https://python-pillow.org/):** Processamento e conversão de imagens capturadas pela câmera ou upload.
-   **[Streamlit Back Camera Input](https://www.google.com/search?q=https://github.com/m-v-p-a/streamlit-back-camera-input):** Componente especializado para acesso direto à câmera traseira em dispositivos móveis.
-   **[FPDF2](https://py-pdf.github.io/fpdf2/):** Geração dinâmica de relatórios em PDF para exportação dos resultados da auditoria.

## 🚀 Como rodar o projeto

Siga os passos abaixo para configurar o ambiente e executar a aplicação localmente:

### 1. Criar o Ambiente Virtual
Isso garante que as bibliotecas do projeto não conflitem com outras no seu computador.
```bash
python -m venv .venv
```

### 2. Ativar o Ambiente Virtual

No Windows:

```bash
.\.venv\Scripts\activate
```

No Linux/Mac:

```bash
source .venv/bin/activate
```

### 3. Instalar as Dependências
Instale todas as bibliotecas necessárias listadas no arquivo requirements.txt.

```bash
pip install -r requirements.txt
```

### 4. Executar a Aplicação
Inicie o servidor do Streamlit para abrir a interface no seu navegador.

```bash
python -m streamlit run app.py
```

### 5.  Insira sua **Google API Key** no menu lateral e comece a exploração!

A aplicação utiliza o modelo **Gemini 3 Flash (Preview)**. Para obter sua chave gratuita, siga estes passos:

1.  Acesse o [Google AI Studio](https://aistudio.google.com/).

2.  Faça login com sua conta Google.

3.  No menu lateral, clique em **"Get API key"**.

4.  Clique no botão **"Create API key in new project"**.

5.  Copie a chave gerada e cole-a no campo correspondente na barra lateral da aplicação.
Obs: Cuidado com os limites


# Exemplo dos prompts executados
Análise da etiqueta
``` 
    Analise esta etiqueta de preço. Retorne APENAS: 
    <p>Nome do Produto + Peso/Unidade</p> 
    <v>Preço</v> 
    <u>Unidade (kg, un, g)</u>. 
    Se não encontrar, retorne <p>N/A</p>
```   

Obs: O retorno virá uma resposta com tags como um XML contendo os dados encontrados.

Comparação com a nota fiscal
```
Você é um AUDITOR DE PREÇOS RIGOROSO. Sua missão é cruzar os dados da prateleira com o cupom fiscal.

    <contexto_lista_prateleira>
    [{'id': 1767832259.035672, 'Produto': 'APONTADOR DUPLO HC', 'Preço Prateleira': 14.99, 'Qtd': 1.0, 'Unidade': 'un'}]
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
    </resultado>
    </formato_saida_esperado>
```

Obs: O retorno virá uma resposta com tags como um XML contendo os dados encontrados.

---

# Resultado
