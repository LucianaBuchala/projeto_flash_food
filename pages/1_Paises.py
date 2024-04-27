#==============================
# importação de bibliotecas
#==============================
import pandas as pd
import plotly.express as px
import folium
import inflection
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import folium

#==============================
# funções
#==============================

def gerar_grafico ( col, op, titulo_eixo_y):
    df_grafico = df2.loc[:, [col, 'country_name']].groupby('country_name').agg( {col: op} ) .reset_index()
    df_grafico.columns = ['pais', col]
    df_grafico = df_grafico.sort_values (col, ascending=False)
    fig = px.bar(df_grafico, x='pais', y=col, labels = { 'pais': 'Países', col: titulo_eixo_y}, text_auto=True)
    return fig


COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
    }
def country_name(country_id):
    return COUNTRIES[country_id]

def create_price_type(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}
def color_name(color_code):
    return COLORS[color_code]

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df


def limpar_dados ( df2 ):
    """ essa função faz as seguintes limpezas no dataframe:

        1. remoção das linhas com dados ausentes
        2. exclusão de duplicidades
        3. colunas renameadas
        4. inclusão e limpeza de colunas

        Input: Dataframe
        Output: Dataframe
    """

    # excluir linhas sem informação
    #df2.dropna(subset=['Cuisines'], inplace=True)
    df2.dropna(inplace=True)
    
    # excluir linhas duplicadas
    df2.drop_duplicates(inplace=True)
    
    # renomeando as colunas
    df2 = rename_columns(df2)
    
    # considerar somente 1 tipo de culinária para cada restaurante
    df2["cuisines"] = df2.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])
    
    # inclusão coluna com nome do país
    df2['country_name'] =  df2['country_code'].apply( lambda x: country_name(x))
    
    # inclusão coluna com nome da categoria de preço
    df2['price_type'] = df2['price_range'].apply(lambda x: create_price_type(x))
    
    # inclusão coluna com nome das cores
    df2['color_name'] = df2['rating_color'].apply(lambda x: color_name(x))
    
    # limpeza de coluna 'address'
    df2['address'] = df2['address'].apply(lambda x: x.replace('\n', ' '))
    
    # limpeza de coluna 'restaurant_name'
    df2['restaurant_name'] = df2['restaurant_name'].apply(lambda x: x.replace('\n', ''))

    return df2


#========================= ESTRUTURA LÓGICA DO CÓDIGO =========================


#========================
# Extração
#========================
# importacao do dataset
df = pd.read_csv('dataset\zomato.csv')

# fazendo cópia do DataFrame original
df2 = df.copy()

#========================
# Limpeza dos dados
#========================
df2 = limpar_dados ( df2 )



st.set_page_config(page_title = "Visão países", layout = "wide")

#========================
# Side bar
#========================

# image_path = 'E:\ComunidadeDS\python_analise_dados\projeto_aluno\logo5.jpg'
# image = Image.open(image_path)
image = Image.open('logo5.jpg')
st.sidebar.image  (image, width=120)

st.sidebar.markdown( '## Flash Food')
st.sidebar.markdown( """----""")


paises_selecionados = st.sidebar.multiselect('Escolha os países que deseja visualizar', df2['country_name'].unique(), default = [ 'Brazil', 'England', 'Qatar', 'Canada', 'South Africa', 'Australia'])

# para que o data frame e gráficos sejam impactoados pelo filtro:
df2 = df2.loc[ df2['country_name'].isin(paises_selecionados), : ]

st.sidebar.markdown("""----""")
st.sidebar.markdown('##### Feito por Luciana para o curso Comunidade DS')


#========================
# layout
#========================

st.markdown('# Visão Países')

with st.container():
    st.markdown('#### Quantidade de restaurantes registrados por país')
    #st.markdown('<div style="text-align: center;">Quantidade de restaurantes registrados por país</div>', unsafe_allow_html=True)
    fig = gerar_grafico ( 'restaurant_id', 'nunique', 'Quantidade de restaurantes')  
    st.plotly_chart( fig, use_container_width=True)

with st.container():
    st.markdown('#### Quantidade de cidades registradas por país') 
    fig = gerar_grafico ( 'city', 'nunique', 'Quantidade de cidades')  
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('#### Qtd média de avaliações por país')
        fig = gerar_grafico ( 'votes', 'mean', 'Quantidade média de avaliações')  
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('#### Preço médio de prato para 2 pessoas por país')
        fig = gerar_grafico ( 'average_cost_for_two', 'mean', 'Preço médio prato para duas pessoas')
        st.plotly_chart(fig, use_container_width=True)



