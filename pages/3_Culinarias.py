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

def card_top_restaurates():

    colunas = ['restaurant_id', 'restaurant_name','country_name', 'city', 'cuisines', 'average_cost_for_two', 'currency', 'aggregate_rating', 'votes' ]
    
    dic_top_restaurante_por_culinaria = {
        'Italian': '',
        'American': '' ,
        'Arabian': '',
        'Japanese': '',
        'Brazilian': '',
    }
    
    
    for key in dic_top_restaurante_por_culinaria.keys():
        linhas_culinaria = df2['cuisines'] == key
        dic_top_restaurante_por_culinaria[key] = df2.loc[linhas_culinaria, colunas].sort_values( ['aggregate_rating', 'restaurant_id'], ascending= [False, True]).iloc[0, :].to_dict()
    
    return dic_top_restaurante_por_culinaria


    

def grafico_barra_ava (ordenacao):
       
    linhas = (df2[ 'aggregate_rating'] != 0) & (df2['country_name'].isin(paises_selecionados))
    df_culinaria_ava = df2.loc[ linhas, [ 'aggregate_rating', 'cuisines']].groupby('cuisines').mean().reset_index()
    df_culinaria_ava.columns = ['culinaria', 'Nota média de avaliação']
    df_culinaria_ava_melhor = df_culinaria_ava.sort_values ('Nota média de avaliação', ascending=ordenacao)
    fig = px.bar(df_culinaria_ava_melhor.head(top_slider), x='culinaria', y='Nota média de avaliação', labels = {'culinaria': 'Tipo de culinária', 'Nota média de avaliação': 'Nota média de avaliação'}, text_auto='.1f')
    return fig

def tabela_top_restaurantes (top):

    linhas = (df2['cuisines'].isin(culinarias_selecionadas))  & (df2['country_name'].isin(paises_selecionados))
    top_restaurantes = df2.loc[linhas, ['restaurant_id', 'restaurant_name','country_name', 'city', 'cuisines', 'average_cost_for_two', 'aggregate_rating', 'votes' ]].sort_values( ['aggregate_rating', 'restaurant_id'], ascending= [False, True])
    top_restaurantes = top_restaurantes.head(top)
    return top_restaurantes

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
df = pd.read_csv('dataset/zomato.csv')

# fazendo cópia do DataFrame original
df2 = df.copy()

#========================
# Limpeza dos dados
#========================
df2 = limpar_dados ( df2 )



st.set_page_config(page_title = "Visão culinárias", layout = "wide")

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

top_slider = st.sidebar.slider( 'Seleciona a quantidade de restaurantes que quer visualizar', value=10, min_value=1, max_value=20)

culinarias_selecionadas = st.sidebar.multiselect('Escolha os tipos de culinárias que deseja visualizar', df2['cuisines'].unique(), default = [ 'Home-made', 'BBQ', 'Japanese', 'Brazilian', 'Arabian', 'American', 'Italian'])




st.sidebar.markdown("""----""")
st.sidebar.markdown('##### Criado por Luciana para o curso Formação Profissional em Ciência de Dados da Comunidade DS')


#========================
# layout
#========================

st.markdown('# Visão Culinárias')

with st.container():
    st.markdown('#### Melhores restaurantes das principais culinárias')
           
    dic = card_top_restaurates()

    qtd_colunas = len(dic)
    col1, col2, col3, col4, col5 = st.columns(qtd_colunas)

    with col1:
        nome_rest = dic['Italian']['restaurant_name']
        medida = dic['Italian']['aggregate_rating']
        pais = dic['Italian']['country_name']
        cidade = dic['Italian']['city']
        preco = dic['Italian']['average_cost_for_two']
        moeda = dic['Italian']['currency']
        st.metric(
            label=f'Italian: {nome_rest}', 
            value= f' {medida}/5.0', 
            help=f"""
            País: {pais}\n
            Cidade: {cidade}\n
            Média preço: {preco} - {moeda}""")
                

    with col2:
        nome_rest = dic['American']['restaurant_name']
        medida = dic['American']['aggregate_rating']
        pais = dic['American']['country_name']
        cidade = dic['American']['city']
        preco = dic['American']['average_cost_for_two']
        moeda = dic['American']['currency']
        st.metric(
            label=f'American: {nome_rest}', 
            value= f' {medida}/5.0', 
            help=f"""
            País: {pais}\n
            Cidade: {cidade}\n
            Média preço: {preco} - {moeda}""")

    with col3:
        nome_rest = dic['Arabian']['restaurant_name']
        medida = dic['Arabian']['aggregate_rating']
        pais = dic['Arabian']['country_name']
        cidade = dic['Arabian']['city']
        preco = dic['Arabian']['average_cost_for_two']
        moeda = dic['Arabian']['currency']
        st.metric(
            label=f'Arabian: {nome_rest}', 
            value= f' {medida}/5.0', 
            help=f"""
            País: {pais}\n
            Cidade: {cidade}\n
            Média preço: {preco} - {moeda}""")

    with col4:
        nome_rest = dic['Japanese']['restaurant_name']
        medida = dic['Japanese']['aggregate_rating']
        pais = dic['Japanese']['country_name']
        cidade = dic['Japanese']['city']
        preco = dic['Japanese']['average_cost_for_two']
        moeda = dic['Japanese']['currency']
        st.metric(
            label=f'Japanese: {nome_rest}', 
            value= f' {medida}/5.0', 
            help=f"""
            País: {pais}\n
            Cidade: {cidade}\n
            Média preço: {preco} - {moeda}""")

    with col5:
        nome_rest = dic['Brazilian']['restaurant_name']
        medida = dic['Brazilian']['aggregate_rating']
        pais = dic['Brazilian']['country_name']
        cidade = dic['Brazilian']['city']
        preco = dic['Brazilian']['average_cost_for_two']
        moeda = dic['Brazilian']['currency']
        st.metric(
            label=f'Brazilian: {nome_rest}', 
            value= f' {medida}/5.0', 
            help=f"""
            País: {pais}\n
            Cidade: {cidade}\n
            Média preço: {preco} - {moeda}""")

with st.container():
    st.markdown(f'#### Top {top_slider} restaurantes') 
    tabela = tabela_top_restaurantes (top_slider)
    st.dataframe(tabela)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'#### Top {top_slider} melhores culinárias')
        # fig = gerar_grafico ( 'votes', 'mean', 'Quantidade média de avaliações')
        fig = grafico_barra_ava (ordenacao=False)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f'#### Top {top_slider} piores culinárias')
        fig = grafico_barra_ava (ordenacao=True)
        st.plotly_chart(fig, use_container_width=True)


