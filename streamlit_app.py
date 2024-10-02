import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px


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
aluguel_min, aluguel_max = st.sidebar.slider("Selecione o Valor do Aluguel (R$)", int(df['rent amount (R$)'].min()), int(df['rent amount (R$)'].max()), value=(int(df['rent amount (R$)'].min()), int(df['rent amount (R$)'].max())))
mobiliado = st.sidebar.selectbox('Imóvel mobiliado?', ('Sim', 'Não'))
aceita_animais = st.sidebar.selectbox("Permitir Animais?", ('Sim', 'Não'))
garagens = st.sidebar.slider("Selecione a Quantidade de Garagens", int(df['parking spaces'].min()), int(df['parking spaces'].max()))
quartos = st.sidebar.slider('Quantidade de quartos', int(df['rooms'].min()), int(df['rooms'].max()))
banheiros = st.sidebar.slider('Quantidade de banheiros', int(df['bathroom'].min()), int(df['bathroom'].max()))
andar_maximo = st.sidebar.slider("Selecione o Andar", int(df['floor'].min()), int(df['floor'].max()))
area_min, area_max = st.sidebar.slider("Selecione a Área (m²)", int(df['area'].min()), int(df['area'].max()), value=(int(df['area'].min()), int(df['area'].max())))


# Mapeamento do de colunas para labels amigáveis
mobiliado_map = {'Sim': 'furnished', 'Não': 'not furnished'}
mobiliado_selecionado = mobiliado_map[mobiliado]

aceita_animais_map = {'Sim': 'acept', 'Não': 'not acept'}
aceita_animais_selecionado = aceita_animais_map[aceita_animais]

# Aplicando filtros
filtered_data = df[
    (df['city'].isin(cidade)) &
    (df['area'].between(area_min, area_max)) &
    (df['rooms'] >= quartos) &
    (df['bathroom'] >= banheiros) &
    (df['parking spaces'] >= garagens) &
    (df['floor'] <= andar_maximo) &
    (df['animal'] == aceita_animais_selecionado) &
    (df['furniture'] == mobiliado_selecionado) &
    (df['rent amount (R$)'].between(aluguel_min, aluguel_max))
]

with st.expander("[Debug] Dados brutos:"):
    # [Debug] Exibir o dataframe filtrado
    st.subheader("Dados brutos filtrados")
    st.write(filtered_data)

    # Matriz de correlação
    numeric_df = df.select_dtypes(include=['number']) # Sem colunas não numéricas
    correlation_matrix = numeric_df.corr()
    st.write(correlation_matrix)

### Visualizações ###

## Primeira seção [2 colunas] ##
st.subheader('Gráficos de análise exploratória')
fig, ax = plt.subplots(1, 2, figsize=(15, 6))

# 1. Distribuição de valores de aluguel
sns.histplot(filtered_data['rent amount (R$)'],
             color='dodgerblue',
             kde=True,
             ax=ax[0])
ax[0].lines[0].set_color('crimson') # Pinta linha KDE
ax[0].set_title('Distribuição do valor de aluguel', fontsize=16)
ax[0].set_xlabel('Valor do aluguel (R$)', fontsize=12)
ax[0].set_ylabel('')

# 2. Distribuição das áreas dos imóveis
sns.histplot(filtered_data['area'],
             color='lightgreen',
             kde=True,
             ax=ax[1])
ax[1].lines[0].set_color('orange') # Pinta linha KDE
ax[1].set_title('Distribuição da área dos imóveis', fontsize=16)
ax[1].set_xlabel('Área', fontsize=12)
ax[1].set_ylabel('')


st.pyplot(fig)

## Segunda seção ##
st.subheader('Gráficos de apresentação')

# 3. Comparação de médias de aluguel por cidade
rent_by_city = filtered_data.groupby('city')['rent amount (R$)'].mean().reset_index().sort_values(by='rent amount (R$)', ascending=False)
fig = px.bar(rent_by_city,
             x='city',
             y='rent amount (R$)',
             color='city',  # Aplicar cores baseadas na cidade
             color_discrete_sequence=['gray', 'gray', 'darkgreen', 'darkgreen', 'lightgreen'],
             title='Média do Aluguel por Cidade',
             text='rent amount (R$)',
             hover_data={'city': False, 'rent amount (R$)': False})
fig.update_traces(
    # Formato dos valores como moeda com 2 casas decimais
    texttemplate='R$ %{text:.2f}',
    textposition='outside'  # Posição do texto fora das colunas
)
fig.update_layout(
    xaxis=dict(title='Cidade'),  # Rotula o eixo X
    yaxis=dict(showgrid=False, showticklabels=False, title=''),   # Remove rótulos e título do eixo Y
    showlegend=False # Remove legendas
)
st.plotly_chart(fig)

# 4. Gráfico BoxPlot de Valor de Alguel por Área (segmentada em faixas)
# df['faixa_area'] = pd.cut(df['area'], bins=[0, 100, 200, 500, 1000, 2000], labels=['0-100 m²', '101-200 m²', '201-500 m²', '501-1000 m²', '1001-2000 m²'])

# # Criar box plot
# fig = plt.figure(figsize=(10, 6))
# sns.boxplot(data=df, x='faixa_area', y='rent amount (R$)')

# # Configurações do gráfico
# plt.title('Distribuição do Valor do Aluguel por Faixa de Área')
# plt.xlabel('Faixa de Área')
# plt.ylabel('Valor do Aluguel (R$)')
# plt.grid(True)

# st.pyplot(fig)
