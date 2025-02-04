import pandas as pd

dataset = pd.read_csv("https://raw.githubusercontent.com/dannypfo/performance-and-productivity/refs/heads/main/superstructure_all_dataset.csv")

import numpy as np
dataset['Worker density'] = dataset['Worker density'].round(0)
dataset['Batch area'] = dataset['Batch area'].round(0)
dataset['Number of workers'] = dataset['Number of workers'].round(0)
dataset['GIA'] = dataset['GIA'].round(0)
dataset['Planned production rate'] = dataset['Planned production rate'].round(0)
dataset['Actual production rate'] = dataset['Actual production rate'].round(0)
dataset['Labour productivity'] = dataset['Labour productivity'].round(2)
dataset['Cycle time'] = dataset['Cycle time'].round(0)
dataset['Actual duration'] = np.ceil(dataset['Actual duration']).astype(int)

import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import pandas as pd
import plotly.io as pio


# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

frame_sorted = dataset.sort_values(by='Frame')

# Layout
app.layout = html.Div([
    dcc.Dropdown(
        id='worker-filter',
        options=[{'label': str(worker), 'value': worker} for worker in sorted(frame_sorted['Avg number of workers'].unique())],
        placeholder="Select Average Number of Workers",
        multi=False,
        style={
        'width': '50%',         # Adjust dropdown width (e.g., 50% of container)
        #'fontSize': '14px',     # Reduce font size
        #'height': '35px',       # Adjust height
        #'padding': '3px',       # Reduce inner padding
        #'minHeight': '30px',    # Minimum height of the dropdown
    }
    ),
    dcc.Graph(id='scatter-plot'),
    html.Button("Download HTML", id="download-btn", n_clicks=0),
    dcc.Download(id="download")
])

# Callback to update scatter plot
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('worker-filter', 'value')]
)
def update_graph(selected_workers):
    filtered_data = frame_sorted if selected_workers is None else frame_sorted[frame_sorted['Avg number of workers'] == selected_workers]
    
    fig = px.scatter(
        filtered_data, 
        x='Actual production rate', 
        y='Labour productivity',
        title='<b>Superstructure: Labour productivity v Production rate<b>',
        range_x=[0, 130], 
        range_y=[0, 0.9], 
        color='Frame',
        template='seaborn',
        color_discrete_sequence=px.colors.qualitative.Dark24,
        hover_data=['Building ID','Level','Frame','Actual duration','Cycle time','GIA','Batch area',
                    'Pours','Cranes','Worker density','Number of workers'],
        opacity=0.9
    )
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(xaxis_title='Production rate (m\N{SUPERSCRIPT TWO}/day)',
                      yaxis_title='Labour productivity (m\N{SUPERSCRIPT TWO}/worker-hour)')
    fig.update_layout(
        xaxis=dict(tickfont=dict(size=18), dtick=10),
        yaxis=dict(tickfont=dict(size=18)),
        legend=dict(font=dict(size=18)),
        font=dict(family="Calibri")
        )
    fig.update_layout(template="seaborn")
    fig.update_layout(height=600, width=1000)
    fig.update_layout(title_font=dict(size=24),
                      xaxis_title_font=dict(size=21), 
                      yaxis_title_font=dict(size=21))
    fig.update_layout(plot_bgcolor='rgb(240, 240, 240)') 
    
    return fig

# Callback to generate and download the HTML file
@app.callback(
    Output("download", "data"),
    [Input("download-btn", "n_clicks")],
    [State("scatter-plot", "figure")],
    prevent_initial_call=True
)
def generate_html(n_clicks, figure):
    return dict(content=pio.to_html(figure), filename="scatter_plot_output.html")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
