import pandas as pd
import streamlit as st

URL = 'https://www.portaldetransito.rs.gov.br/dtw/servicos/crd/mostraEdital.jsp?nroEdital=21&anoEdital=2023'

tables = pd.read_html(URL)
    
if tables:
    df = pd.concat(tables, ignore_index=True)
    df[['Marca', 'Modelo']] = df['Marca/Modelo'].str.split('/', 1, expand=True)
    df['Ano'] = df['Ano'].str.split('/', 1, expand=True)[0]
    df['Valor Mínimo'] = df['Valor Mínimo'].str.replace('R\$ ', '').str.replace('.', '').str.replace(',', '.').astype(float)
else:
    st.error("Nenhuma tabela encontrada no link.")
    st.stop()

# Remover colunas específicas
columns_to_remove = ["Nº Motor", "Chassi", "Placa", "Marca/Modelo"]
df = df.drop(columns=columns_to_remove)

# Filtrar linhas com "Gasolina" no valor da coluna "Combustível"
df = df[df['Combustível'].str.contains("Gasolina", case=False, na=False)]

# Filtros interativos com seleção multi e valores padrão mais recorrentes
default_marca = df['Marca'].value_counts().index[:8].tolist()

# Criação da interface Streamlit com full width
st.set_page_config(layout="wide")
st.title("Dashboard de Estatísticas de Veículos")

with st.sidebar:
    selected_marca = st.multiselect("Filtrar por Marca:", df['Marca'].unique(), default=default_marca, key="marca")
    select_all_button = st.button("Selecionar Todos os Carros")

# Aplicar filtros
if select_all_button:
    selected_marca = df['Marca'].unique()

filtered_df = df[(df['Marca'].isin(selected_marca))]

r1col1, r1col2 = st.columns(2)

# Estatísticas expressivas em cards
with r1col1: st.info(f"Total de Registros: {filtered_df.shape[0]:,}")
with r1col2: st.info(f"Valor Médio Mínimo: R$ {filtered_df['Valor Mínimo'].mean():,.2f}")

# Tabela em uma linha sozinha
st.header("Dados Filtrados")
st.dataframe(filtered_df, height=300)

# Gráficos organizados em colunas
st.header("Gráficos")
r2col1, r2col2 = st.columns(2)

with r2col1:
    st.subheader("Contagem de Veículos por Marca")
    marca_counts = filtered_df['Marca'].value_counts()
    st.bar_chart(marca_counts, use_container_width=True)

with r2col2:
    st.subheader("Dispersão entre Ano e Valor Mínimo")
    st.line_chart(filtered_df.groupby('Ano')['Valor Mínimo'].mean(), use_container_width=True)
