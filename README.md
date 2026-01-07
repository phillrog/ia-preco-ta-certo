# **IA Preço Tá Certo?**

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

## 📊 Estrutura do Projeto
-----------------------

Plaintext

```
├── assets/
│   └── styles.css          # Estilização visual (Clamp e Shimmer)
├── services/
│   └── gemini_service.py   # Integração com a API do Gemini
├── utils/
│   └── utils.py            # Funções de formatação e ajuda
└── app.py                  # Arquivo principal do Streamlit
```

## 🛠️ Tecnologias Utilizadas

-   **Linguagem:** Python 3.12.7
-   **Interface:** [Streamlit](https://streamlit.io/)
-   **IA:** [Google Gemini API](https://ai.google.dev/) (via LangChain)
-   **Processamento de Dados:** Pandas
-   **Estilização:** CSS


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


# Prompts
Análise da etiqueta
``` Analise esta etiqueta de preço. Retorne APENAS: 
    <p>Nome do Produto + Peso/Unidade</p> <v>Preço</v> <u>Unidade (kg, un, g)</u>. 
    Se não encontrar, retorne <p>N/A</p>
```            

Comparação com cupom fiscal
```
Minha lista da prateleira (VALORES CORRETOS): {lista_texto}
            Analise da NOTA FISCAL anexo e compare com a minha lista. REGRAS:
            1. Compare o valor unitário (ou por kg) de cada item.
            2. Se o valor na NOTA FISCAL for MAIOR que o valor na PRATELEIRA, Status = 'ERRADO'.
            3. Se o valor no NOTA FISCAL for IGUAL ou MENOR que na PRATELEIRA, Status = 'OK'.
            4. Na Observação, coloque SEMPRE: 'PRATELEIRA: R$ X | NOTA FISCAL: R$ Y'.
            Retorne APENAS tags: <item><n>Nome</n><s>Status</s><d>Observação</d></item>
```

# Resultado