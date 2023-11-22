from dash import Dash, dash_table, html, dcc, State
import pandas as pd
from collections import OrderedDict
from plotly.colors import n_colors
from dateutil.relativedelta import relativedelta
from dash_table.Format import Format, Scheme, Symbol, Group
from dash_table import FormatTemplate
from dash.dependencies import Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
from datetime import date
import datetime
from pandas.tseries.offsets import MonthEnd
import numpy as np
import colorlover

bancos=pd.read_excel('bancos.xlsx')
financieras=pd.read_excel('financieras.xlsx')
tarjetas=pd.read_excel('tarjetas.xlsx')
aseguradoras=pd.read_excel('aseguradoras.xlsx')

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True
server = app.server


app.layout = html.Div([
    
 html.Br(), html.H2("Resumen de riesgo mensual"),
      dbc.Container([
    dbc.Row([
        dbc.Col([html.P("Tipo de institución:"), dcc.Dropdown( 
    id="tipo_institucion",options=["Bancos", "Financieras", "Tarjetas de crédito", "Aseguradoras"], 
                         )], ),
        dbc.Col([html.P("Razón:"), dcc.Dropdown(id="razones", options=bancos["Razón"].drop_duplicates())], )]),
             
        dbc.Row([dbc.Col([html.P("Valor a desplegar:"), dcc.Dropdown(id="valores", options=bancos["Tipo"].drop_duplicates(), )]),
            dbc.Col([html.P("Fecha (mes):"),dcc.DatePickerSingle(
        id='fecha',display_format='DD/MM/YYYY',
        min_date_allowed=bancos["Fecha"].min().strftime('%Y-%m-%d'),
        max_date_allowed=bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max().strftime('%Y-%m-%d'),
        initial_visible_month=bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max().strftime('%Y-%m-%d'),
        date=bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max().strftime('%Y-%m-%d')
    ),])],
            )], fluid=True),
    
   html.Br(),
    dash_table.DataTable(id='table',sort_action='native', 
                         style_cell={'padding': '5px', 'font-family':'sans-serif'},
                         style_header={'backgroundColor': 'light gray','fontWeight': 'bold'}),
    html.Br(),dbc.Container([
    dbc.Row([dbc.Col([dbc.Button('Mostrar tabla comparativa de todas las razones', id='boton', className="mb-3", n_clicks=0)])],
            )], fluid=True),html.Br(),
    dbc.Fade(dash_table.DataTable(id='table2',sort_action='native',
                         style_cell={'padding': '5px', 'font-family':'sans-serif'},
                         style_header={'backgroundColor': 'light gray','fontWeight': 'bold'}),
            id="fade",
            is_in=False,
            appear=False),
     html.Br(),
    html.H2("Gráfica comparativa"),
    dbc.Container([
    dbc.Row([html.P("Instituciones:"), dcc.Dropdown( 
    id="instituciones",options=bancos["Institución"].drop_duplicates(), multi=True,
                         )])], fluid=True),

    html.Br(),
   
        dbc.Container([
    dbc.Row([dbc.Col([html.P("Razón:"), dcc.Dropdown(id="razones2", options=bancos["Razón"].drop_duplicates(), )], ),
             dbc.Col([html.P("Valor a desplegar:"), dcc.Dropdown(id="valores2", options=bancos["Tipo"].drop_duplicates(),  )])],
            )], fluid=True),
        
    html.Br(),
  dbc.Container([
    dbc.Row([dbc.Col([html.P("Rango de fechas:"),   dcc.Dropdown(
        id = 'timeframe_dropdown', 
        options = [
            {'label': 'Último año', 'value': 'Último año'},
            {'label': 'Últimos 2 años', 'value': 'Últimos 2 años'},
            {'label': 'Últimos 3 años', 'value': 'Últimos 3 años'}
        ], 
        value='Últimos 5 años',
        clearable=False,
    ), dcc.DatePickerRange(
        id='fechas', display_format='DD/MM/YYYY',
        min_date_allowed=bancos["Fecha"].min().strftime('%Y-%m-%d'),
        max_date_allowed=bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max().strftime('%Y-%m-%d'),
        initial_visible_month=bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max().strftime('%Y-%m-%d'),
        start_date=date(2018, 1, 1),
        end_date=bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max().strftime('%Y-%m-%d'),) ], width=6)])], fluid=True), 
    
    #graficas
    html.Div(dcc.Graph(id="grafica")
            ),
    
])

@app.callback(
    [Output('razones', 'options'), # This updates the field start_date in the DatePicker
    Output('razones2', 'options'),  Output('instituciones', 'value'), ], # This updates the field end_date in the DatePicker
    [Input('tipo_institucion', 'value')],
)

def updateDataPicker(tipo_institucion):
    if tipo_institucion == 'Bancos':
        return bancos["Razón"].drop_duplicates(),  bancos["Razón"].drop_duplicates(), ["SISTEMA BANCARIO"]
    elif tipo_institucion == 'Financieras':
        return financieras["Razón"].drop_duplicates(),  financieras["Razón"].drop_duplicates(), ["SISTEMA FINANCIERO"]
    elif tipo_institucion == 'Tarjetas de crédito':
        return tarjetas["Razón"].drop_duplicates(),  tarjetas["Razón"].drop_duplicates(), ["SISTEMA CREDITICIO"]
    elif tipo_institucion == 'Aseguradoras':
        return aseguradoras["Razón"].drop_duplicates(), aseguradoras["Razón"].drop_duplicates(), ["SISTEMA ASEGURADOR"]
    else:
        pass

    
@app.callback(
    [Output('instituciones', 'options'),Output('razones2', 'value'),Output('valores2', 'value') ], # This updates the field end_date in the DatePicker
    [Input('tipo_institucion', 'value'), Input('fechas', 'start_date'), Input('razones', 'value'), Input('valores', 'value')],
)

def updateDataPicker(tipo_institucion, fecha, razon, valor):
    if tipo_institucion == 'Bancos':
        return bancos[(bancos["Fecha"].dt.date>=((datetime.datetime.strptime(fecha, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]["Institución"].drop_duplicates(), razon, valor
    elif tipo_institucion == 'Financieras':
        return financieras[(financieras["Fecha"].dt.date>=((datetime.datetime.strptime(fecha, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]["Institución"].drop_duplicates(), razon, valor
    elif tipo_institucion == 'Tarjetas de crédito':
        return tarjetas[(tarjetas["Fecha"].dt.date>=((datetime.datetime.strptime(fecha, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]["Institución"].drop_duplicates(), razon, valor
    elif tipo_institucion == 'Aseguradoras':
        return aseguradoras["Institución"].drop_duplicates(), razon, valor
    else:
        pass

@app.callback(
    [Output("table","data"), Output("table","columns"), Output("table","style_data_conditional"),
    Output("table","style_cell_conditional"),
    Output("table2","data"), Output("table2","columns"), Output("table2","style_data_conditional"),
    Output("table2","style_cell_conditional"), ], 
    [Input('tipo_institucion', 'value'), Input("razones","value"), 
    Input("valores","value"), 
    Input("fecha","date")]
)
def discrete_background_color_bins(tipo_institucion, razon, valor, fecha):
    if tipo_institucion=="Bancos":
        df = bancos
    elif tipo_institucion=="Financieras":
        df = financieras
    elif tipo_institucion=="Tarjetas de crédito":
        df = tarjetas
    elif tipo_institucion=="Aseguradoras":
        df = aseguradoras
    else:
        pass
    
    
    if tipo_institucion=="Bancos":
        dfr = bancos
    elif tipo_institucion=="Financieras":
        dfr = financieras
    elif tipo_institucion=="Tarjetas de crédito":
        dfr = tarjetas
    elif tipo_institucion=="Aseguradoras":
        dfr = aseguradoras
    else:
        pass
    
    df = df[(df["Razón"]==razon)&(df["Tipo"]==valor)
            &(df["Fecha"].dt.date==((datetime.datetime.strptime(fecha, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]
    
    if valor=="Riesgo":
        aseg=(((aseguradoras[["Institución", "Fecha", "Tipo", "Razón", "Valor"]])[(aseguradoras["Tipo"]==valor)
            &(aseguradoras["Fecha"].dt.date==((datetime.datetime.strptime(fecha, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]).pivot_table(index=["Institución", "Fecha", "Tipo"], 
                        columns='Razón', 
                        values='Valor').reset_index())[["Institución"]]
        
    else: 
        aseg=(((aseguradoras[["Institución", "Fecha", "Tipo", "Razón", "Valor"]])[(aseguradoras["Tipo"]==valor)
            &(aseguradoras["Fecha"].dt.date==((datetime.datetime.strptime(fecha, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]).pivot_table(index=["Institución", "Fecha", "Tipo"], 
                        columns='Razón', 
                        values='Valor').reset_index())[["Institución", "Gastos de administración",
                                                       "Gastos de adquisición", "Siniestralidad", "Siniestralidad (original)"]]
    
        
    if valor=="Riesgo":
       
        
        dfr=(((dfr[["Institución", "Fecha", "Tipo", "Razón", "Valor"]])[(dfr["Tipo"]==valor)
            &(dfr["Fecha"].dt.date==((datetime.datetime.strptime(fecha, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]).pivot_table(index=["Institución", "Fecha", "Tipo"], 
                        columns='Razón', 
                        values='Valor').reset_index())[["Institución"]]
        
    elif tipo_institucion=="Tarjetas de crédito": 
      
        dfr=(((dfr[["Institución", "Fecha", "Tipo", "Razón", "Valor"]])[(dfr["Tipo"]==valor)
            &(dfr["Fecha"].dt.date==((datetime.datetime.strptime(fecha, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]).pivot_table(index=["Institución", "Fecha", "Tipo"], 
                        columns='Razón', 
                        values='Valor').reset_index())[["Institución", "ROA (desviación estándar)", "ROE (desviación estándar)"]]
    
    else: dfr=(((dfr[["Institución", "Fecha", "Tipo", "Razón", "Valor"]])[(dfr["Tipo"]==valor)
            &(dfr["Fecha"].dt.date==((datetime.datetime.strptime(fecha, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]).pivot_table(index=["Institución", "Fecha", "Tipo"], 
                        columns='Razón', 
                        values='Valor').reset_index())[["Institución", "ROE (desviación estándar)"]]
       
    
    
    if razon=="Ratio combinado" and valor!="Riesgo":
        df = df.merge(aseg, on=['Institución'], how='left')
        df = df[["Institución", "Valor", "Promedio","Gastos de administración", "Gastos de adquisición", 
                "Siniestralidad", "2021", "2022", "2023"]]
        df["Gastos de administración"]=round(df["Gastos de administración"], 4)
        df["Gastos de adquisición"]=round(df["Gastos de adquisición"], 4)
        df["Siniestralidad"]=round(df["Siniestralidad"], 4)
    elif razon=="Ratio combinado (original)" and valor!="Riesgo":
        df = df.merge(aseg, on=['Institución'], how='left')
        df = df[["Institución", "Valor", "Promedio","Gastos de administración", "Gastos de adquisición", 
                "Siniestralidad (original)", "2021", "2022", "2023"]]  
        df["Gastos de administración"]=round(df["Gastos de administración"], 4)
        df["Gastos de adquisición"]=round(df["Gastos de adquisición"], 4)
        df["Siniestralidad (original)"]=round(df["Siniestralidad (original)"], 4)
    elif razon=="ROE" and valor!="Riesgo":
        df = df.merge(dfr, on=['Institución'], how='left')
        df = df[["Institución", "Valor", "Promedio","ROE (desviación estándar)", "2021", "2022", "2023"]]
        df["ROE (desviación estándar)"]=round(df["ROE (desviación estándar)"], 4)
    elif razon=="ROA" and valor!="Riesgo":
        df = df.merge(dfr, on=['Institución'], how='left')
        df = df[["Institución", "Valor", "Promedio","ROA (desviación estándar)", "2021", "2022", "2023"]]
        df["ROA (desviación estándar)"]=round(df["ROA (desviación estándar)"], 4)
        
    else: df = df[["Institución", "Valor", "Promedio","2021", "2022", "2023"]]  
    
    if valor=="Riesgo" or valor=="Rank":
        df["Valor"]=round(df["Valor"], 2)
        df["Promedio"]=round(df["Promedio"], 2)
    else: 
        df["Valor"]=round(df["Valor"], 4)
        df["Promedio"]=round(df["Promedio"], 4)
    

    df = df[df['Valor'].notna()]
    
    df=df.rename(columns={'Valor': 'Valor del mes', 'Promedio':'Promedio del último año'})
    
    if razon == "Bienes realizables" or valor=="Riesgo" or valor=="Rank" or razon=="Ratio combinado" or razon=="Ratio combinado (original)" or razon=="ROA (desviación estándar)" or razon=="ROE (desviación estándar)" or razon == "Bienes realizables":
        df=df.sort_values(by=["Valor del mes"], ascending=False)
    else: df=df.sort_values(by=["Valor del mes"])
    
    
    if tipo_institucion=="Bancos":
        valor_default = "SISTEMA BANCARIO"
    elif tipo_institucion=="Financieras":
        valor_default = "SISTEMA FINANCIERO"
    elif tipo_institucion=="Tarjetas de crédito":
        valor_default = "SISTEMA CREDITICIO"
    elif tipo_institucion=="Aseguradoras":
        valor_default = "SISTEMA ASEGURADOR"
    else:
        pass
    
    
    if razon=="Capital contable":
        df = df[df['Institución']!=valor_default]
    else: pass
    
    
    def discrete_background_color_bins(df, n_bins=len(df["Institución"].drop_duplicates()), columns='all'):
        
        
        
        bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
        if columns == 'all':
            if 'id' in df:
                df_numeric_columns = df.select_dtypes('number').drop(['id'], axis=1)
            else:
                df_numeric_columns = df.select_dtypes('number')
        else:
            df_numeric_columns = df[columns]
        
        styles = []    
        for j in df_numeric_columns:
            df_max = df[j].max()
            df_min = df[j].min()
            ranges = [
                ((df_max - df_min) * i) + df_min
                for i in bounds
            ]
            
            if razon == "Bienes realizables" or razon=="Ratio combinado" or razon=="Ratio combinado (original)" or valor=="Riesgo" or valor=="Rank" or razon=="ROA (desviación estándar)" or razon=="ROE (desviación estándar)" or j in ["Gastos de administración",
                                                       "Gastos de adquisición", "Siniestralidad", "Siniestralidad (original)",  "ROA (desviación estándar)", "ROE (desviación estándar)"]:
                paleta=n_colors('rgb(0,255,0)','rgb(255,255,0)',  int(n_bins/2), colortype='rgb')+n_colors('rgb(255,255,0)','rgb(255,69,0)',  int(n_bins/2)+1, colortype='rgb')
            else: paleta=n_colors('rgb(255,69,0)','rgb(255,255,0)',  int(n_bins/2), colortype='rgb')+n_colors('rgb(255,255,0)','rgb(0,255,0)',  int(n_bins/2)+1, colortype='rgb')

            for i in range(1, len(bounds)):
                min_bound = ranges[i - 1]
                max_bound = ranges[i]
                backgroundColor = paleta[i - 1]
                color = "black"

                styles.append({
                        'if': {
                            'filter_query': (
                                '{{{column}}} >= {min_bound}' +
                                (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                            ).format(column=j, min_bound=min_bound, max_bound=max_bound),
                            'column_id': j
                        },
                        'backgroundColor': backgroundColor,
                        'color': color
                    })

        return (styles)

    (styles) = discrete_background_color_bins(df)
    
    
    
    
    
    
    if razon=="Capital contable":
        style_data_conditional=styles
    else:
        style_data_conditional=styles+ [ 
           {     'if': {'row_index': np.where(df["Institución"] == valor_default)[0][0]},
                'fontWeight': 'bold'
            } 
        ]
        
    style_cell_conditional=[
        {
            'if': {'column_id': c},
            'textAlign': 'left'
        } for c in ['Institución', '2021','2022','2023']]
    
    formatted = Format()
    formatted = formatted.scheme(Scheme.percentage)
    
    data=df.to_dict('records')
    
    if valor=="Riesgo":
        columns=[{'name': i, 'id': i, 'deletable': True,"type": "numeric", "format": {'specifier': '.2f'}} for i in df.columns]
    elif valor=="Rank":
        columns=[{'name': i, 'id': i, 'deletable': True} for i in df.columns]
    else: columns=[{'name': i, 'id': i,  "type": "numeric", "format": FormatTemplate.percentage(2),
                   'deletable': True,} for i in df.columns] 
    
    
    
    if tipo_institucion=="Bancos":
        dft = bancos
    elif tipo_institucion=="Financieras":
        dft = financieras
    elif tipo_institucion=="Tarjetas de crédito":
        dft = tarjetas
    elif tipo_institucion=="Aseguradoras":
        dft = aseguradoras
    else:
        pass
    
    
    dft=(((dft[["Institución", "Fecha", "Tipo", "Razón", "Valor"]])[(dft["Tipo"]==valor)
            &(dft["Fecha"].dt.date==((datetime.datetime.strptime(fecha, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]).pivot_table(index=["Institución", "Fecha", "Tipo"], 
                        columns='Razón', 
                        values='Valor').reset_index())
    
    if tipo_institucion=="Aseguradoras" and valor=="Razón":
        dft=dft.drop(['Gastos de administración', 'Gastos de adquisición',"Siniestralidad", "Siniestralidad (original)",
                     'Fecha','Tipo'], axis=1)
    elif tipo_institucion=="Aseguradoras" and valor!="Riesgo":
        dft=dft.drop(['Gastos de administración', 'Gastos de adquisición',"Siniestralidad", "Siniestralidad (original)",
                     'Fecha','Tipo', 'Ponderado'], axis=1)
    elif tipo_institucion!="Aseguradoras" and valor=="Razón":
        dft=dft.drop(['Fecha','Tipo'], axis=1)
    else:
        dft=dft.drop(['Fecha','Tipo', 'Ponderado'], axis=1)
    
    def discrete_background_color_bins2(dft, n_bins=len(df["Institución"].drop_duplicates()), columns='all'):
        
        
        
        bounds = [i * (1.0 / n_bins) for i in range(n_bins + 1)]
        if columns == 'all':
            if 'id' in dft:
                df_numeric_columns = dft.select_dtypes('number').drop(['id'], axis=1)
            else:
                df_numeric_columns = dft.select_dtypes('number')
        else:
            df_numeric_columns = dft[columns]
        
        styles2 = []    
        for j in df_numeric_columns:
            df_max = dft[j].max()
            df_min = dft[j].min()
            ranges = [
                ((df_max - df_min) * i) + df_min
                for i in bounds
            ]
            
            if valor=="Riesgo" or valor=="Rank" or j in ["Gastos de administración","Ratio combinado", "Ratio combinado (original)", "Bienes realizables",
                                                       "Gastos de adquisición", "Siniestralidad", "Siniestralidad (original)",  "ROA (desviación estándar)", "ROE (desviación estándar)"]:
                paleta=n_colors('rgb(0,255,0)','rgb(255,255,0)',  int(n_bins/2), colortype='rgb')+n_colors('rgb(255,255,0)','rgb(255,69,0)',  int(n_bins/2)+1, colortype='rgb')
            else: paleta=n_colors('rgb(255,69,0)','rgb(255,255,0)',  int(n_bins/2), colortype='rgb')+n_colors('rgb(255,255,0)','rgb(0,255,0)',  int(n_bins/2)+1, colortype='rgb')

            for i in range(1, len(bounds)):
                min_bound = ranges[i - 1]
                max_bound = ranges[i]
                backgroundColor = paleta[i - 1]
                color = "black"

                styles2.append({
                        'if': {
                            'filter_query': (
                                '{{{column}}} >= {min_bound}' +
                                (' && {{{column}}} < {max_bound}' if (i < len(bounds) - 1) else '')
                            ).format(column=j, min_bound=min_bound, max_bound=max_bound),
                            'column_id': j
                        },
                        'backgroundColor': backgroundColor,
                        'color': color
                    })

        return (styles2)

    (styles2) = discrete_background_color_bins(dft)
    
    style_data_conditional2=styles2+ [ 
           {     'if': {'row_index': np.where(dft["Institución"] == valor_default)[0][0]},
                'fontWeight': 'bold'
            } 
        ]
        
    style_cell_conditional2=[
        {
            'if': {'column_id': c},
            'textAlign': 'left'
        } for c in ['Institución', '2021','2022','2023']]
        
    data2=dft.to_dict('records')
    
    if valor=="Riesgo":
        columns2=[{'name': i, 'id': i, 'deletable': True,"type": "numeric", "format": {'specifier': '.2f'}} for i in dft.columns]
    elif valor=="Rank":
        columns2=[{'name': i, 'id': i, 'deletable': True} for i in dft.columns]
    else: columns2=[{'name': i, 'id': i,  "type": "numeric", "format": FormatTemplate.percentage(2),
                   'deletable': True,} for i in dft.columns] 
    
    
    
    
    return data, columns, style_data_conditional, style_cell_conditional,data2, columns2, style_data_conditional2, style_cell_conditional2


@app.callback(
    [Output('fechas', 'start_date'), # This updates the field start_date in the DatePicker
    Output('fechas', 'end_date')], # This updates the field end_date in the DatePicker
    [Input('timeframe_dropdown', 'value')],
)

def updateDataPicker(dropdown_value):
    if dropdown_value == 'Último año':
        return (bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max()-relativedelta(years=1)).strftime('%Y-%m-%d'), bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max().strftime('%Y-%m-%d')
    elif dropdown_value == 'Últimos 2 años':
        return (bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max()-relativedelta(years=2)).strftime('%Y-%m-%d'), bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max().strftime('%Y-%m-%d')
    else:
        return (bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max()-relativedelta(years=3)).strftime('%Y-%m-%d'), bancos[bancos["Razón"]!="ROE (desviación estándar)"]["Fecha"].max().strftime('%Y-%m-%d')


@app.callback(
    Output("grafica","figure"),
    [Input('tipo_institucion', 'value'),Input("instituciones","value"), Input("razones2","value"), Input("valores2","value"), 
    Input("fechas","start_date"),
    Input("fechas","end_date")]
)

#definicion de la funcion

def display_value(tipo_institucion, instituciones, razon, valor, fecha1, fecha2):
    
    
    if tipo_institucion=="Bancos":
        df2 = bancos
    elif tipo_institucion=="Financieras":
        df2 = financieras
    elif tipo_institucion=="Tarjetas de crédito":
        df2 = tarjetas
    elif tipo_institucion=="Aseguradoras":
        df2 = aseguradoras
    else:
        pass
    df2 = df2[(df2["Razón"]==razon)&(df2["Tipo"]==valor)&(df2["Institución"].isin(instituciones))&(df2["Tipo"]==valor)
            &(df2["Fecha"].dt.date>=((datetime.datetime.strptime(fecha1, '%Y-%m-%d')+ relativedelta(day=31)).date() ))
           &(df2["Fecha"].dt.date<=((datetime.datetime.strptime(fecha2, '%Y-%m-%d')+ relativedelta(day=31)).date() ))]
    df2["Valor"]=round(df2["Valor"], 2)
    df2["Promedio"]=round(df2["Promedio"], 2)
    df2 = df2[df2['Valor'].notna()]
    df2=df2.rename(columns={'Valor': 'Valor del mes', 'Promedio':'Promedio del último año'})
    

    
    fig= px.line(df2,color="Institución",x="Fecha",markers=True,y="Valor del mes",height=650, width=1400,hover_data={'Fecha': '|%d/%m/%Y'}, 
                 template="simple_white" ,labels={
                     "Valor del mes": razon})
    fig.update_layout(legend_title="", legend= dict(
    orientation="h", y=-.2
        ))
    #tabla
    return fig

@app.callback(
    [Output("fade", "is_in"), Output("boton", "children")],
    [Input("boton", "n_clicks")],
    [State("fade", "is_in")],
)
def toggle_fade(n, is_in):
    if not n:
        
        # Button has never been clicked
        return False
    button_text = 'Esconder tabla comparativa de todas las razones' if n % 2!= 0 else 'Mostrar tabla comparativa de todas las razones'
    return not is_in, button_text



app.run_server(debug=False, host="0.0.0.0", port=10000)
