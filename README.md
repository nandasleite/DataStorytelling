# Storytelling com Datasets

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B)
![Gemini API](https://img.shields.io/badge/Google%20Gemini-8E75B2)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75)

Este é um aplicativo web interativo construído com Streamlit que utiliza a IA do Google Gemini para analisar, narrar e visualizar a história por trás dos seus dados.

## Funcionalidades

*   **Upload de CSV**: Carregue seus próprios dados ou use o dataset de exemplo integrado.
*   **Análise Inteligente**: A IA analisa estatísticas descritivas e distribuições categóricas para entender o contexto dos seus dados.
*   **Data Storytelling**: Receba uma narrativa clara e concisa sobre os principais insights, escrita para um público não-técnico.
*   **Gráficos Inteligentes**: A IA escolhe e gera automaticamente o gráfico mais relevante para os seus dados usando Plotly.
*   **Interface Amigável**: Configuração simples da chave de API e visualização limpa dos dados.

## Estrutura do Projeto

```text
DataStorytelling/
├── app.py              # Código principal da aplicação Streamlit
├── requirements.txt    # Dependências do projeto
└── README.md           # Documentação
```

## Como Rodar

1.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Execute o aplicativo:**
    ```bash
    streamlit run app.py
    ```

3.  **Configure a Chave da API:**
    *   Ao abrir o aplicativo no navegador, use a barra lateral à esquerda (seção **"1. Sua API"**).
    *   Insira sua chave da API do Google Gemini no campo indicado.
    *   Se não tiver uma chave, siga o link fornecido na interface para criar uma gratuitamente no Google AI Studio.
