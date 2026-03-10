import streamlit as st
import pandas as pd
import google.genai as genai
from google.api_core import exceptions
import re
import json

# --- Configuração da Página ---
st.set_page_config(page_title="Tradutor de Datasets")

# --- Barra Lateral para Configuração e Upload ---
with st.sidebar:
    st.header("Configuração")
    st.markdown("Para usar este app, você precisa de uma chave de API do Google Gemini.")
    
    api_key_usuario = st.text_input(
        "Insira sua API Key",
        type="password",
        help="A chave não será salva e é usada apenas para esta sessão."
    )
    
    st.markdown(
        """
        **Como obter sua chave:**
        1. Acesse o [Google AI Studio](https://aistudio.google.com/app/apikey).
        2. Faça login com sua conta Google.
        3. Clique em **"Create API key"**.
        4. Copie a chave e cole no campo acima.
        """
    )
    
    st.divider()
    
    st.header("Dados")
    # Upload do arquivo movido para a sidebar
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

def criar_resumo_inteligente(df, nome_arquivo=None):
    """
    Cria um resumo JSON estruturado e conciso de um DataFrame, otimizado para APIs de LLM.
    """
    resumo = {
        "contexto_geral": {
            "nome_do_arquivo": nome_arquivo,
            "numero_de_linhas": len(df),
            "nomes_das_colunas": df.columns.tolist()
        }
    }

    # Resumo para colunas numéricas
    resumo_numerico = df.describe().to_dict()
    resumo["resumo_numerico"] = resumo_numerico

    # Resumo para colunas categóricas (não-numéricas)
    resumo_categorico = {}
    colunas_categoricas = df.select_dtypes(include=['object', 'category']).columns
    for col in colunas_categoricas:
        top_5_valores = df[col].value_counts().nlargest(5).to_dict()
        resumo_categorico[col] = {
            "valores_unicos_total": df[col].nunique(),
            "top_5_valores_mais_comuns": top_5_valores
        }

    if resumo_categorico:
        resumo["resumo_categorico"] = resumo_categorico

    return json.dumps(resumo, indent=2, ensure_ascii=False)


def gerar_historia_dados(resumo_inteligente, api_key):
    """
    Gera uma história a partir de um resumo inteligente do DataFrame.
    """
    if not api_key:
        return "⚠️ **Erro:** Por favor, insira sua Chave de API na barra lateral para continuar."

    try:
        # Configura o cliente com a chave fornecida pelo usuário
        client = genai.Client(api_key=api_key)

        prompt = f"""
        Atue como um analista de dados sênior e data storyteller.
        Sua tarefa é analisar um resumo estruturado de um conjunto de dados e criar uma narrativa coesa e clara (em até três parágrafos) para um público não-técnico.

        **Resumo Estruturado do Dataset (em formato JSON):**
        {resumo_inteligente}

        **Instruções para a Análise:**
        1.  **Entenda o Contexto:** Use os "nomes_das_colunas" e o "nome_do_arquivo" para inferir o tema geral do dataset. Comece sua análise mencionando sobre o que são os dados (ex: "Estes dados parecem tratar de...").
        2.  **Analise as Colunas Numéricas:** Use o "resumo_numerico" para identificar tendências (média), dispersão (std) e, principalmente, valores extremos (min/max). Traduza o que esses números significam.
        3.  **Analise as Colunas Categóricas:** Se o "resumo_categorico" existir, use-o para entender a distribuição das categorias. Destaque os "top_5_valores_mais_comuns".
        4.  **Conecte os Pontos:** Crie uma história que conecte os insights numéricos e categóricos. Se uma categoria específica tem a maior média em uma métrica, isso é um insight valioso.
        5.  **Linguagem Simples:** Evite jargões técnicos. Explique os conceitos de forma prática.
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except exceptions.ResourceExhausted as e:
        retry_match = re.search(r"retry in (\d+\.?\d*)s", str(e))
        if retry_match:
            wait_time = float(retry_match.group(1))
            return f"⚠️ **Você atingiu o limite de requisições.**\n\nO plano gratuito da API foi excedido. Por favor, aguarde **{wait_time:.0f} segundos**."
        return "⚠️ **Você atingiu o limite de requisições.** Por favor, aguarde um minuto e tente novamente."
    except Exception as e:
        return f"Ocorreu um erro inesperado ao gerar a história: {e}"


# --- Interface Principal ---
st.title("Storytelling com Datasets")
st.write("Faça o upload do seu arquivo CSV na barra lateral para começar.")

df = None
nome_arquivo = None

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        nome_arquivo = uploaded_file.name
    except Exception as e:
        st.error(f"Erro ao ler o arquivo CSV: {e}")
else:
    st.info("👈 Nenhum arquivo carregado. Use a barra lateral para fazer upload ou veja abaixo um exemplo com dados sobre desmatamento.")
    nome_arquivo = "desmatamento_amazonia.csv"
    data_exemplo = {
        'Ano': [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020],
        'Desmatamento_km2': [7000, 6418, 4571, 5891, 5012, 6207, 7893, 6947, 7536, 10129, 10851],
        'Estado': ['PA', 'MT', 'PA', 'AM', 'MT', 'RO', 'PA', 'MT', 'AM', 'PA', 'PA'],
        'Operacoes_Fiscalizacao': [120, 130, 110, 140, 150, 135, 160, 155, 170, 180, 190]
    }
    df = pd.DataFrame(data_exemplo)

if df is not None:
    st.subheader("Visualização das 5 primeiras linhas")
    st.dataframe(df.head())

    if st.button("Gerar História dos Dados"):
        if not api_key_usuario:
            st.warning("⚠️ Por favor, insira sua chave de API na barra lateral para continuar.")
        else:
            with st.spinner("Criando resumo inteligente e gerando a narrativa..."):
                resumo = criar_resumo_inteligente(df, nome_arquivo)
                historia = gerar_historia_dados(resumo, api_key_usuario)

                st.subheader("A História por Trás dos Números")
                st.write(historia)
