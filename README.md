# Tradutor de Datasets 📊

Este é um aplicativo web simples construído com Streamlit que utiliza a IA do Google Gemini para analisar e contar a história por trás dos seus dados.

## Funcionalidades

*   **Upload de CSV**: Carregue seus próprios dados ou use o dataset de exemplo.
*   **Visualização**: Veja as primeiras linhas do seu dataset.
*   **Análise Inteligente**: A IA analisa as estatísticas descritivas dos dados.
*   **Data Storytelling**: Receba uma narrativa clara e concisa sobre os principais insights.

## Como Rodar

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure a Chave da API:**
    *   Crie uma pasta chamada `.streamlit` na raiz do projeto.
    *   Dentro dela, crie um arquivo chamado `secrets.toml`.
    *   Adicione sua chave da API do Google Gemini no arquivo:
        ```toml
        GOOGLE_API_KEY = "SUA_CHAVE_API_AQUI"
        ```

3.  **Execute o aplicativo:**
    ```bash
    streamlit run app.py
    ```
