import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from plotly.subplots import make_subplots

# Carregar o dataset e preparar os dados
df = pd.read_csv("houses_to_rent_v2.csv")

# Remove - de algumas colunas
df['floor'] = df['floor'].str.replace('-', '1')
df['floor'] = pd.to_numeric(df['floor'])

df['parking spaces'] = df['parking spaces'].apply(str).str.replace('-', '0')
df['parking spaces'] = pd.to_numeric(df['parking spaces'])

# Título e configurações gerais
# Layout fixed: definindo a largura
css = '''
<style>
    section.stMain > div {max-width:1200px}
</style>
'''
st.markdown(css, unsafe_allow_html=True)

st.title("Imóveis para Aluguel no Brasil")

# Filtros
st.sidebar.header("Filtros")
cidade = st.sidebar.multiselect('Selecione a cidade', df['city'].unique(), df['city'].unique())
aluguel_min, aluguel_max = st.sidebar.slider("Selecione o Valor do Aluguel (R$)", int(df['total (R$)'].min()), int(df['total (R$)'].max()), value=(int(df['total (R$)'].min()), int(df['total (R$)'].max())))
somente_mobiliado = st.sidebar.checkbox('Imóvel mobiliado?')
aceita_animais = st.sidebar.checkbox("Permite Animais?")
garagens = st.sidebar.slider("Selecione a Quantidade de Garagens", int(df['parking spaces'].min()), int(df['parking spaces'].max()))
quartos = st.sidebar.slider('Quantidade de quartos', int(df['rooms'].min()), int(df['rooms'].max()))
banheiros = st.sidebar.slider('Quantidade de banheiros', int(df['bathroom'].min()), int(df['bathroom'].max()))
andar_minimo, andar_maximo = st.sidebar.slider("Andares aceitos", int(df['floor'].min()), int(df['floor'].max()), value=(int(df['floor'].min()), int(df['floor'].max())))
area_min, area_max = st.sidebar.slider("Selecione a Área (m²)", int(df['area'].min()), int(df['area'].max()), value=(int(df['area'].min()), int(df['area'].max())))


# Aplicando filtros
filtered_data = df[
    (df['city'].isin(cidade)) &
    (df['area'].between(area_min, area_max)) &
    (df['rooms'] >= quartos) &
    (df['bathroom'] >= banheiros) &
    (df['parking spaces'] >= garagens) &
    (df['floor'].between(andar_minimo, andar_maximo)) &
    (df['total (R$)'].between(aluguel_min, aluguel_max))
]
if somente_mobiliado:
    filtered_data = filtered_data[filtered_data['furniture'] == 'furnished']
if aceita_animais:
    filtered_data = filtered_data[filtered_data['animal'] == 'acept']


with st.expander("Análise Exploratória"):
    # [Debug] Exibir o dataframe filtrado
    st.subheader("Dados brutos filtrados")
    st.write(filtered_data)

    fig, ax = plt.subplots(1, 2, figsize=(15, 6))

    st.subheader('Gráficos de análise exploratória')
    # 1. Distribuição de valores de aluguel
    sns.histplot(filtered_data['total (R$)'],
                color='dodgerblue',
                kde=True,
                ax=ax[0])
    if(len(ax[0].lines) > 0): # Se for desenhar KDE
        ax[0].lines[0].set_color('crimson') # Pinta linha KDE
    ax[0].set_title('Distribuição do valor de aluguel', fontsize=16)
    ax[0].set_xlabel('Valor do aluguel (R$)', fontsize=12)
    ax[0].set_ylabel('')

    # 2. Distribuição das áreas dos imóveis
    sns.histplot(filtered_data['area'],
                color='lightgreen',
                kde=True,
                ax=ax[1])
    if(len(ax[1].lines) > 0): # Se for desenhar KDE
        ax[1].lines[0].set_color('crimson') # Pinta a linha KDE
    ax[1].set_title('Distribuição da área dos imóveis', fontsize=16)
    ax[1].set_xlabel('Área', fontsize=12)
    ax[1].set_ylabel('')

    st.pyplot(fig)

    # Matriz de correlação
    numeric_df = df.select_dtypes(include=['number']) # Sem colunas não numéricas
    correlation_matrix = numeric_df.corr()
    st.subheader("Matriz de correlação")
    st.write(correlation_matrix)


st.subheader('Gráficos de apresentação')
# 3. Comparação de médias de aluguel por cidade
rent_by_city = filtered_data.groupby('city')['total (R$)'].mean().reset_index().sort_values(by='total (R$)', ascending=False)
fig1 = px.bar(rent_by_city,
             x='city',
             y='total (R$)',
             color='city',  # Aplicar cores baseadas na cidade
             color_discrete_sequence=['gray'] * (len(rent_by_city) - 1) + ['lightgreen'],
             title='Média do Aluguel por Cidade',
             text='total (R$)',
             hover_data={'city': False, 'total (R$)': False})
fig1.update_traces(
    texttemplate='R$ %{text:.2f}'
)

# 4. Quantidades de imóveis por cidade
imov_by_city = filtered_data.groupby('city').size().reset_index(name='Quantidade').sort_values(by='Quantidade', ascending=True)
fig2 = px.bar(imov_by_city,
             x='city',
             y='Quantidade',
             color='city',  # Aplicar cores baseadas na cidade
             color_discrete_sequence=['gray'] * (len(imov_by_city) - 1) + ['lightgreen'],
             title='Qtd. de Imóveis a alugar por Cidade',
             text='Quantidade',
             hover_data={'city': False, 'Quantidade': False})


fig = make_subplots(rows=1, cols=2, subplot_titles=("Média do Aluguel por Cidade", "Qtd. de Imóveis por Cidade"))
fig.add_traces(fig1.data, rows=1, cols=1)
fig.add_traces(fig2.data, rows=1, cols=2)

fig.update_traces(
    textposition='outside', # Posição do texto fora das colunas
    width=1
)

fig.update_layout(
    showlegend=False # Remove legendas
)

fig.update_yaxes(showgrid=False, title='', showticklabels=False, row=1, col=1)
fig.update_yaxes(showgrid=False, title='', showticklabels=False, row=1, col=2)
fig.update_xaxes(title='Cidade', row=1, col=1)
fig.update_xaxes(title='Cidade', row=1, col=2)

st.plotly_chart(fig)



# Gráfico BoxPlot de Valor de Alguel por Área (segmentada em faixas)
# df['faixa_area'] = pd.cut(df['area'], bins=[0, 100, 200, 500, 1000, 2000], labels=['0-100 m²', '101-200 m²', '201-500 m²', '501-1000 m²', '1001-2000 m²'])

# # Criar box plot
# fig = plt.figure(figsize=(10, 6))
# sns.boxplot(data=df, x='faixa_area', y='total (R$)')

# # Configurações do gráfico
# plt.title('Distribuição do Valor do Aluguel por Faixa de Área')
# plt.xlabel('Faixa de Área')
# plt.ylabel('Valor do Aluguel (R$)')
# plt.grid(True)

# st.pyplot(fig)
