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
from folium.plugins import MarkerCluster

#==============================
# funções
#==============================

def mapa_restaurantes (df2):
    
    figure = folium.Figure(width=1920, height=1080)
    mapa = folium.Map(max_bounds=True).add_to(figure)
    marker_cluster = MarkerCluster().add_to(mapa)

    
    for index, line in df2.iterrows():
                   
        name = line["restaurant_name"]
        price_for_two = line["average_cost_for_two"]
        cuisine = line["cuisines"]
        currency = line["currency"]
        rating = line["aggregate_rating"]
        color = f'{line["color_name"]}'
    
        html = "<p><strong>{}</strong></p>"
        html += "<p>Price: {},00 ({}) para dois"
        html += "<br />Type: {}"
        html += "<br />Aggragate Rating: {}/5.0"
        html = html.format(name, price_for_two, currency, cuisine, rating)
        
        popup = folium.Popup(
        folium.Html(html, script=True),
        max_width=500,
        )

        
        folium.Marker( 
          [line['latitude'],line['longitude']],
          popup=popup,
          icon = folium.Icon(color = color, icon='home', prefix='fa')
        ).add_to(marker_cluster)

    folium_static( mapa, width=1024, height=768)
    return None


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



st.set_page_config(page_title = "Visão empresa", layout = "wide")

#========================
# Side bar
#========================

# image_path = 'E:\ComunidadeDS\python_analise_dados\projeto_aluno\logo5.jpg'
# image = Image.open(image_path)
image = Image.open('logo5.jpg')
st.sidebar.image  (image, width=120)

st.sidebar.markdown( '## Flash Food')
st.sidebar.markdown( """----""")


# paises_selecionados = st.sidebar.multiselect('Escolha os países que deseja visualizar', df2['country_name'].unique(), default = [ 'Brazil', 'England', 'Qatar', 'Canada', 'South Africa', 'Australia'])

# # para que o data frame e gráficos sejam impactoados pelo filtro:
# df2 = df2.loc[ df2['country_name'].isin(paises_selecionados), : ]

# st.sidebar.markdown("""----""")
st.sidebar.markdown('### Dados tratados')
st.sidebar.download_button(
    label="Download",
    data=df.to_csv(index=False, sep=";"),
    file_name="data_flash_food.csv",
    mime="text/csv",
)

st.sidebar.markdown("""----""")
st.sidebar.markdown('##### Painel elaborado por Luciana para o curso Formação Profissional em Ciência de Dados da Comunidade DS')



#========================
# layout
#========================

st.markdown('# Flash Food')
st.markdown('## O melhor lugar para encontrar seu mais novo restaurante favorito')
st.markdown('### Temos as seguintes marcas dentro de nossa plataforma:')


with st.container():
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(
            label='Restaurantes cadastrados', 
            value= df2['restaurant_id'].nunique())

    with col2:
        st.metric(
            label='Países cadastrados', 
            value= df2['country_code'].nunique())

    with col3:
        st.metric(
            label='Cidades cadastrados', 
            value= df2['city'].nunique())
    
    with col4:
        total_avaliacoes = df2['votes'].sum()
        total_avaliacoes_texto = f'{total_avaliacoes:_}'
        total_avaliacoes_texto = total_avaliacoes_texto.replace('_', '.')
        st.metric(
            label='Avaliações', 
            value= total_avaliacoes_texto)
    
    with col5:
        st.metric(
            label='Culinárias', 
            value= df2['cuisines'].nunique())

with st.container():
    mapa_restaurantes(df2)
