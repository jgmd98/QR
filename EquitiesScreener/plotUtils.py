import plotly.express as px

def plotlyPlot(plotType, data, xCol, yCol, xLabel, yLabel, groupBy, title, backgroundColor="white", paperColor="white", fontColor="black", grid=["lightgrey", "black"]):
    # goal: return plotly plot
    fig = {"line":px.line(data, x=xCol, y=yCol, title=title, color=groupBy),
           "scatter":px.scatter(data, x=xCol, y=yCol, title=title, color=groupBy)}[plotType]
    fig.update_layout(xaxis_title=xLabel, yaxis_title=yLabel, legend_title_text="", plot_bgcolor=backgroundColor, paper_bgcolor=paperColor, font_color=fontColor)
    fig.update_xaxes(mirror=True, ticks="outside", showline=True, linecolor=grid[1], gridcolor=grid[0])
    fig.update_yaxes(mirror=True, ticks="outside", showline=True, linecolor=grid[1], gridcolor=grid[0])
    return fig



