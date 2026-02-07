# imports
import streamlit as st
import pandas as pd
import altair as alt

# functions
@st.cache_data
def load_data():
    df_data = pd.read_csv('CEN0101J.csv')

    df_data.rename(columns={
        'Druh PHM': 'PalivoDruh',
        'CENPHM1': 'PalivoId',
        'Měsíce': 'RokMesicText',
        'CasM': 'RokMesicId',
        'Hodnota': 'Cena'}
        , inplace=True)

    palivo_rename = {
        'Benzin automobilový bezolovnatý Natural 95 [Kč/l]': 'Natural 95 [Kč/l]',
        'Benzin automobilový bezolovnatý Super plus 98 [Kč/l]': 'Natural 98 [Kč/l]',
        'LPG [Kč/l]': 'LPG [Kč/l]',
        'Motorová nafta [Kč/l]': 'Nafta [Kč/l]',
        'Stlačený zemní plyn - CNG [Kč/kg]': 'CNG [Kč/kg]',
    }

    df_data['PalivoDruh'] = df_data['PalivoDruh'].replace(palivo_rename)

    df_data = df_data[['PalivoDruh', 'PalivoId', 'RokMesicText', 'RokMesicId', 'Cena']]

    df_data['Datum'] = pd.to_datetime(df_data['RokMesicId'])
    df_data['Rok'] = df_data['Datum'].dt.year
    df_data['Mesic'] = df_data['Datum'].dt.month

    return df_data

@st.cache_data
def load_categories(df_data):
    categories = df_data['PalivoDruh'].unique()
    return categories.tolist()

@st.cache_data
def load_group_data(df_data):
    return df_data.groupby(['Rok', 'PalivoDruh'])['Cena'].max().reset_index()

def load_data_by_category(df_group_data, category):
    return df_group_data[df_group_data['PalivoDruh'] == category]

def get_cost(df_selected_data, asc=True):
    return df_selected_data.sort_values('Cena', ascending=asc).iloc[0]


# initial load data
data = load_data()
group_data = load_group_data(data)


# layout
st.title('Přehled cen pohonných hmot')
st.header('Ceny pohonných hmot podle typu paliva')

selected_type = st.selectbox('Vyberte typ paliva', load_categories(data))
data_by_category = load_data_by_category(group_data, selected_type)

category_chart = alt.Chart(data_by_category).mark_line().encode(x='Rok:O', y='Cena:Q')
st.altair_chart(category_chart)

col_left, col_right = st.columns(2)
with col_left:
    st.metric(f'Nejnižší cena paliva ({selected_type})', f'{get_cost(data_by_category)["Cena"]} Kč', get_cost(data_by_category)['Rok'])
with col_right:
    st.metric(f'Nejvyšší cena paliva ({selected_type})', f'{get_cost(data_by_category, asc=False)["Cena"]} Kč', get_cost(data_by_category, asc=False)['Rok'])

col_left, col_right = st.columns(2)
with col_left:
    st.metric(f'Nejnižší cena paliva ({selected_type})', f'{data_by_category["Cena"].min()} Kč')
with col_right:
    st.metric(f'Nejvyšší cena paliva ({selected_type})', f'{data_by_category["Cena"].max()} Kč')
