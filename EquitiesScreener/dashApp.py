# other files
from equitiesData import equitiesAnalytics
from plotUtils import plotlyPlot
from tickerUniverse import tickerList
# packages
import pandas as pd
from datetime import date
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

financialsCols = pd.read_csv("financialsColMap.csv") 
financialsColsMap = dict(zip(financialsCols.New, financialsCols.Original))

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

app.layout = html.Div([
    html.Br(),
    # header
    html.H1("Equities Screener", style={"font-size": 34, "text-align": "center", "background-color": "#142d4c", "color": "#9fd3c7"}),
    html.Br(), html.Hr(style={"color":"black"}), html.Br(), html.Br(),
    # display checklist, ticker dropdown, and date range
    dbc.Row([
        dbc.Col(dcc.Checklist(id = "checklistDisplay",
                    options=[{"label": [html.Span("Performance Summary", style={"font-size": 18, "padding-left": 10})], "value": "Performance Summary"},  
                    {"label": [html.Span("Cumulative Return Chart", style={"font-size": 18, "padding-left": 10})], "value": "Cumulative Return Chart"},
                    {"label": [html.Span("Financials", style={"font-size": 18, "padding-left": 10})], "value": "Financials"}], value = ["Performance Summary", "Cumulative Return Chart", "Financials"], 
                    labelStyle={"display": "flex", "align-items": "center"},
                    style={"color": "#9fd3c7", "padding-left": 50}), lg = 3),
        dbc.Col(dcc.Dropdown(id="tickers",
                    options=[{"label": x, "value": x} for x in tickerList],
                    multi=True,
                    value=["AAPL", "MSFT", "GOOGL"],
                    style={"height": "45px", "font-size": 18}
                    ), align = "center", lg = 4),
        dbc.Col(dcc.DatePickerRange(
                    id="dateRange",
                    min_date_allowed=date(2000, 1, 1),
                    max_date_allowed=date.today(),
                    start_date=date(date.today().year, 1, 1),
                    end_date=date.today(),
                    style={"height": "45px", "color": "#9fd3c7", "font-size": 18}), align = "center")], align = "center", justify = "center"),
    html.Br(), html.Hr(style={"color": "#9fd3c7"}),
    # performance summary
    html.Div(id="perfSummTbl", style={"background-color": "#142d4c"}), html.Br(),
    # cumulative return plot
    html.Div(id="cumRetChart"), html.Br(),
    # financials drop down
    html.Div(id="finMetricsDropdown", style={"background-color": "#142d4c", "width":"80%", "padding-left":60}), html.Br(),
    # financials scatter plots
    html.Div(id="financialsCharts"), 
    html.Br(), html.Br(), html.Br(), html.Br(), 
    html.Div("Data sources: Nasdaq, Yahoo Finance. Built by Jack Martin Dyer, April 2024", style={"text-align": "center", "color":"white"}), html.Br(),
    ], style={"padding":"0","background-color": "#142d4c"})

# ------------------------------------------------------------------------------
@app.callback(
    [Output(component_id="perfSummTbl", component_property="children"),
     Output(component_id="cumRetChart", component_property="children"),
     Output(component_id="finMetricsDropdown", component_property="children")],
    [Input(component_id="checklistDisplay", component_property="value"),
    Input(component_id="tickers", component_property="value"),
    Input(component_id="dateRange", component_property="start_date"),
    Input(component_id="dateRange", component_property="end_date")])
def displayReturnsData(checklistDisplay, tickers, startDt, endDt):
    # goal: respond to user inputs and display plots
    # class for the inputted tickers
    eq = equitiesAnalytics(tickers)

    # performance metrics summary
    if "Performance Summary" in checklistDisplay:
        perfSumm = eq.getSummRetMetrics(start=startDt, end=endDt).T
        perfSumm.index.name = "Metric"
        perfSumm = perfSumm[perfSumm.columns[::-1]]
        perfSumm = perfSumm.reset_index()
        perfSummGrid = [html.H1("Performance Summary:", style={"font-size": 20, "background-color": "#142d4c", "color": "#9fd3c7", "padding-left":60}),
                        html.Br(), dag.AgGrid(rowData=perfSumm.to_dict('records'), columnDefs=[{"field": i} for i in perfSumm.columns], 
                                              style={"height": 425, "width": 850, "margin-left":"auto", "margin-right":"auto","background-color": "#142d4c"}), html.Br(), html.Hr(style={"color": "#9fd3c7"})]
    else:
        perfSummGrid = ""

    # cumulative return plot
    if "Cumulative Return Chart" in checklistDisplay:
        cumRetPlot = [html.H1("Cumulative Return:", style={"font-size": 20, "background-color": "#142d4c", "color": "#9fd3c7", "padding-left":60}),
                        html.Br(), dcc.Graph(figure=plotlyPlot("line", eq.getCumulativeReturn(start=startDt, end=endDt), "date", "Cumulative Return", "Date", "Cumulative Return", "symbol", 
                                                "Cumulative Return of {}".format(", ".join(tickers)), "white", "#142d4c", "#9fd3c7")), html.Br(), html.Hr(style={"color": "#9fd3c7"})]
    else:
        cumRetPlot = ""

    if "Financials" in checklistDisplay:
        financialsDropdown = [html.H1("Financials:", style={"font-size": 20, "background-color": "#142d4c", "color": "#9fd3c7"}), html.Br(), 
                              dcc.Dropdown(id="finMetricsDropdownInput",
                                                      options=[{"label": x, "value": x} for x in financialsColsMap.keys() if x not in ["Ticker", "As Of Date", "Period"]],
                                                      multi=True,
                                                      value=["Revenue"],
                                                      style={"height": "45px", "font-size": 18}),
                              html.Div(id="financialsCharts")]
    else:
        financialsDropdown = ""
    
    # if nothing is selected, fill UI white space 
    if [perfSummGrid, cumRetPlot, financialsDropdown] == [""]*3:
        financialsDropdown = [html.Br()]*10       

    return perfSummGrid, cumRetPlot, financialsDropdown

@app.callback(
    Output(component_id="financialsCharts", component_property="children"),
    [Input(component_id="finMetricsDropdownInput", component_property="value"),
     Input(component_id="tickers", component_property="value"),
     Input(component_id="dateRange", component_property="start_date"),
     Input(component_id="dateRange", component_property="end_date")], prevent_initial_call=True)
def displayFinancialsData(finMetrics, tickers, startDt, endDt):
    # goal: scatter plots for financial metrics selected
    fundamentalsData = equitiesAnalytics(tickers).getFundamentals(method = "all", argFreq = "a")
    financialsPlots = []
    for metric in finMetrics:
        financialsPlots.append(dcc.Graph(figure=plotlyPlot("scatter", fundamentalsData, "asOfDate", financialsColsMap[metric], "As Of Date", metric, "symbol", 
                                                           metric + " of {}".format(", ".join(tickers)), "white", "#142d4c", "#9fd3c7")))
    return financialsPlots


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
