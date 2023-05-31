from dash import Dash, html, dcc
from dash.dash_table import DataTable, FormatTemplate
from dash.dash_table.Format import Format, Scheme
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

import pandas as pd
import os, sys 
# sys.path.append('/Users/asbjornfyhn/Desktop/Python/Work/PortfolioSummaryReport')
from PortfolioSummaryReport import PDFDataExtractor

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Sample data for the table
data = {'Name': ['John', 'Emma', 'Michael'],
        'Age': [25, 32, 41]}
df1 = pd.DataFrame(data)

def create_dash_table(df):
    c_names = []
    for k, i in df.items():
        if k.lower() in ['hz return', '100bp up', '50bp up', '50bp down', '100bp down', 'effective yield', 'coupon']:
            c_names.append({'name': k, 'id': k, 'type': 'numeric','format': Format(precision=2, scheme=Scheme.percentage)})
        elif k.lower() in ['modified duration']:
            c_names.append({'name': k, 'id': k, 'type': 'numeric','format': Format(precision=4)})
        else: 
            c_names.append({'name': k, 'id': k, 'type': 'text',})
    return DataTable(df.to_dict('records'), 
                     c_names, editable=True,
                     style_cell={'textAlign': 'left'},
                     style_header={'fontWeight': 'bold'}, 
                     id='tabledata')


app.layout = dbc.Container(
    fluid=True,
    children=[
        dcc.Store(id='memory-output'),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Button('Update Table', id='update-button', n_clicks=0, className="btn btn-primary"),
                        html.Button('Update using stored data', id='update-button1', n_clicks=0, className="btn btn-primary"),
                        dbc.Input(id='input-box', type='text', placeholder='Enter something...'),
                    ],
                    width=2
                ),
                dbc.Col(
                    [
                        html.H2('Table12'),
                        html.Div(id='table', children=create_dash_table(df1))
                    ],
                    width=10
                )
            ]
        )
    ]
)

@app.callback(Output('input-box', 'value'),
              Output('tabledata', 'data'),
                Input('update-button1', 'n_clicks'),
                Input('memory-output', 'data'),
                prevent_initial_call=True)
def update_table(n_clicks, data):
    if n_clicks > 0:
        df = pd.DataFrame.from_dict(data)
        print('\n\n\n\n\n\n\n\n',df,'\n\n\n\n\n\n\n\n')
        
        return 'clicked', df.to_dict('records')
    else:
        raise PreventUpdate


@app.callback(
    Output('table', 'children'),
    Output('memory-output', 'data'),
    [Input('update-button', 'n_clicks')]
)
def update_table(n_clicks):
    if n_clicks > 0:
        pdf_data_extractor = PDFDataExtractor(usd_cost=0.025, gbp_cost=0.02, eur_cost=0.000)

        # get all files in the specified directory
        path = r'path/portfolio_summary_reports'
        df = pd.DataFrame()
        for file in os.listdir(path):
            if (file.endswith(".pdf")) and (file.startswith("Summary")):
                fund = file.split('-')[1]
                if fund[-1:] == ' ':
                    fund = fund[:-1]
                if fund[:1] == ' ':
                    fund = fund[1:]
                print(f'Extracting data from {fund}')
                _dict = pdf_data_extractor.main(pdf_path=f'{path}/{file}', rul=0)
                _df = pd.DataFrame(_dict, index=[fund])
                df = pd.concat([df,_df])
                df['Fund'] = df.index

    table = create_dash_table(df)
    # Return the updated table
    return table, df.to_dict('records')
        


#python ~/Desktop/Python/Work/SumReportWebApp.py
#Python % conda activate py39
if __name__ == '__main__':
    app.run_server(debug=True)