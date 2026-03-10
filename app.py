import streamlit as st
import pandas as pd
import google.genai as genai
from google.api_core import exceptions
import re
import json
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(page_title="Storytelling com Datasets")
st.set_page_config(layout="wide")

# --- Barra Lateral para Configuração e Upload ---
with st.sidebar:
    st.header("1. Sua API")
    st.markdown("Para usar este app, você precisa de uma chave de API do Google Gemini.")

    api_key_usuario = st.text_input(
        "Insira sua API Key",
        type="password",
        help="A chave não será salva e é usada apenas para esta sessão."
    )

    st.info(
        """
        **Como obter sua chave:**
        1. Acesse o [Google AI Studio](https://aistudio.google.com/app/apikey).
        2. Faça login com sua conta Google.
        3. Clique em **"Create API key"**.
        4. Copie a chave e cole no campo acima.
        """
    )

    st.header("2. Seus Dados")
    # Upload do arquivo
    uploaded_file = st.file_uploader("Escolha um arquivo CSV", type="csv")

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.caption("Feito com ❤️ por Fernanda Silva")

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

def gerar_codigo_grafico(resumo_inteligente, api_key):
    """
    Gera código Python para criar um gráfico Plotly com base no resumo dos dados.
    """
    if not api_key:
        return None

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Analise este resumo dos dados: {resumo_inteligente}.
        
        Sua tarefa é criar um código Python usando a biblioteca `plotly.express` (alias `px`) para gerar o gráfico mais relevante e interessante possível com base nesses dados.
        
        **Regras Estritas:**
        1. O dataframe já está carregado na variável `df`. NÃO crie dados de exemplo.
        2. Use `plotly.express` como `px`.
        3. O código deve criar uma figura e atribuí-la à variável `fig`.
        4. NÃO use `fig.show()`.
        5. Retorne APENAS o código Python puro. NÃO use blocos de markdown (```python), NÃO coloque comentários explicativos antes ou depois. Apenas o código executável.
        6. Trate possíveis erros de tipos de dados (ex: converta colunas de data se necessário, mas prefira usar as colunas como estão se possível).
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        # Limpeza extra para garantir que só temos código
        codigo = response.text.replace("```python", "").replace("```", "").strip()
        return codigo

    except Exception as e:
        st.error(f"Erro ao gerar código do gráfico: {e}")
        return None

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

st.divider()

if df is not None:

    st.subheader("Visualização do dataset")
    st.dataframe(df.head())

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        if st.button(" Gerar História dos Dados"):
            if not api_key_usuario:
                st.warning("⚠️ Por favor, insira sua chave de API na barra lateral para continuar.")
            else:
                with st.spinner("Criando resumo inteligente e gerando a narrativa..."):
                    resumo = criar_resumo_inteligente(df, nome_arquivo)
                    historia = gerar_historia_dados(resumo, api_key_usuario)

                    st.subheader("A História por Trás dos Números")
                    st.write(historia)
    
    with col2:
        if st.button("Gerar Gráfico Inteligente"):
            if not api_key_usuario:
                st.warning("⚠️ Por favor, insira sua chave de API na barra lateral para continuar.")
            else:
                with st.spinner("A IA está escolhendo o melhor gráfico para seus dados..."):
                    resumo = criar_resumo_inteligente(df, nome_arquivo)
                    codigo_grafico = gerar_codigo_grafico(resumo, api_key_usuario)
                    
                    if codigo_grafico:
                        try:
                            # Ambiente local para execução segura
                            local_env = {'df': df, 'px': px}
                            exec(codigo_grafico, {}, local_env)
                            
                            if 'fig' in local_env:
                                st.subheader("Gráfico Sugerido pela IA")
                                st.plotly_chart(local_env['fig'], use_container_width=True)
                                with st.expander("Ver código gerado"):
                                    st.code(codigo_grafico, language='python')
                            else:
                                st.error("O código gerado não criou a variável 'fig'.")
                        except Exception as e:
                            st.error(f"Erro ao executar o código do gráfico: {e}")
                            with st.expander("Ver código que falhou"):
                                st.code(codigo_grafico, language='python')
