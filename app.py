# import packages
import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px

# import stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] 

# create a Dash app
app = Dash(__name__, external_stylesheets=stylesheets)

# read data
df = pd.read_csv('gdp_pcap.csv')

server = app.server

# turn all the values into floats
def parse_number(value):
    str_num = str(value)
    if 'k' in str_num:
        return float(str_num.replace('k', '')) * 1000
    else:
        return float(str_num)

for col in df.columns[1:]:
    df[col] = df[col].apply(parse_number)

# create the label and value pairs for the dropdown
country_options = [{"label": country, "value": country} for country in df['country']]

# app layout
app.layout = html.Div([
    html.Div([
        html.H1("GDP Per Capita Over Time"),
        html.P("""This app visualizes the Gross Domestic Product (GDP) Per Capita over time across different countries. 
            The data is sourced from the Gapminder dataset, which contains historical GDP per capita information for 
            multiple countries across different years. The data is visualized using a line chart. The user can select 
            the countries to visualize using the dropdown and can also select the range of years to visualize using the
            range slider. The data is visualized using the Plotly library. The app is built using the Dash library in Python.""")
    ]),
    html.Div([
        html.Div([
            dcc.Dropdown(id='dropdown', options=country_options, multi=True, value=df['country'][0:1])
        ], className='six columns'),
        html.Div(
            [dcc.RangeSlider(
                id='year-slider',
                min=0,
                max=len(df.columns[1:]) - 1,
                value=[0, len(df.columns[1:]) - 1],
                marks={i: {'label': str(year)} for i, year in enumerate(df.columns[1:]) if int(year) % 50 == 0},
                step=1
            )], className='six columns',
        ),
    ], className='row'),
    html.Div([
       dcc.Loading(dcc.Graph(id='gdp-graph'), type='cube')
    ])
])

# add controls to build the interaction
@callback(
    Output('gdp-graph', 'figure'), [Input('dropdown', 'value'), Input('year-slider', 'value')])
def update_graph(selected_countries, selected_year):
    filtered_df = df[df['country'].isin(selected_countries)]
    indexes_to_keep = [0] + list(range(selected_year[0] + 1, selected_year[1] + 2)) 
    filtered_df = filtered_df.iloc[:, indexes_to_keep]
    melted_df = pd.melt(filtered_df, id_vars='country', value_vars=filtered_df.columns[1:], var_name='year', value_name='gdp')
    fig = px.line(melted_df, x='year', y='gdp', color='country', title='GDP Per Capita Over Time')
    return fig

# run the app
if __name__ == '__main__':
    app.run_server(debug=True)