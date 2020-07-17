# -*- coding: utf-8 -*-

"""
Code for generating the dashboard
Author: Xin Yu
Date: May 29, 2020

"""

#--------------------------------------------Imports----------------------------------------------------------------
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import pathlib
import ast
import json

from dash.dependencies import Input, Output, State


#--------------------------------------------Server,  file path, and tokens----------------------------------------------

app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
application = app.server

# Optional Authentication
# VALID_USERNAME_PASSWORD_PAIRS = {
#     'username': 'password'
# }
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )

PATH = pathlib.Path(__file__).parent

DATA_PATH = PATH.joinpath("data").resolve()

#mapbox authentication
mapbox_token="mymapbox token"  #my mapbox token

#--------------------------------------------data processing----------------------------------------------------------

#process data
df  = pd.read_csv(DATA_PATH.joinpath("emailStat.csv"))
df2 = pd.read_csv(DATA_PATH.joinpath("webStat.csv"))
df3 = pd.read_csv(DATA_PATH.joinpath("wechatFollower.csv"))
df4 = pd.read_csv(DATA_PATH.joinpath("wechatTotalReads.csv"))
df5 = pd.read_csv(DATA_PATH.joinpath("wechatArticleSource.csv"))


# Email - get a list of email article types for the dropdown box
article_types = df['article_type'].unique()

# Website - table for all country codes
country_code=pd.read_csv("data/country_codes.csv")

# Website - load the countries_geo_json file for plotting the Choropleth map
with open('data/world_geo_json.json') as f:
    countries_geo_json = json.load(f)

# Website - get a list of webstats.
# daily stats
webStatsList= ['requests_all', 'threats_all', 'pageviews_all','unique_visitors', 'pageview_per_visitor']
# cumulative stats
webCumStatsList= ['requests_all', 'threats_all', 'pageviews_all','unique_visitors']

# Website - numEtries will be used for the sliderbar
numEntries=df2.shape[0]
lst1=[i for i in range (0, numEntries)]
lst2=df2.date
markDict={key:str(value) for (key,value) in zip(lst1, lst2)}

# General - function to get max date in the dataframe for date range picker
def get_max_date(dateCol):
    """
    Get the max date in the data set
    :param dateCol: A single pandas dataframe column containing the date information in YYYY-MM-DD format
    :return: maxDate in python datetime format
    """
    maxYear, maxMonth, maxDate = [int(x) for x in max(dateCol).split('-')]  # we read from csv so the date is actually string!
    maxDate=dt(maxYear, maxMonth, maxDate)  # use the max dates to set the date picker. Min date is 2020-05-15
    return maxDate

# Website - get max date for date range picker
webMaxDate=get_max_date(df2.date)

# Website - get the max and min requests for country. Use these 2 numbers to set the range of the gradient bar in Geo chart
countryReqDictList=[ast.literal_eval(countryDict) for countryDict in df2.requests_country.ravel()]
maxReq=max([max(countryReqDict.values()) for countryReqDict in countryReqDictList])
minReq=min([min(countryReqDict.values()) for countryReqDict in countryReqDictList])

# WeChat - Use the previous function I defined to get max date for the date range picker
wechatMaxDate=get_max_date(df3.date)

# WeChat - get a list of wechat follower stats
wechatFollowerStatsList=["new","unfollowed","net_increase","total"]

# WeChat - get a list of wechat article stats
wechatArticleStatsList=["reads","shares","jump_to_original","saves"]

#--------------------------------------------Layout and styles ------------------------------------------------------

#set title
app.title="CAS Dashboard"

#pass as value for `layout` parameter of general charts except for mapbox
general_layout={
    "hovermode": "compare",   #For charts with multiple lines. It will show multiple data tags when hover. The other option is "closest".
    "autosize": True,
    "margin": dict(t=20, b=40, l=40, r=10),
    "legend":{
        "showlegend": True,
        "orientation": "h",   #note the legends are horizontal!!
        "xanchor": "center",
        "x":0.5

    }
}

#Layout  for tabs
#this is the layout for the tabs GROUP
# tabs_styles = {
#     'height': '44px'
# }

tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '24px',  #how large each tabs are?
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#7ed4f4',
    'color': 'white',
    'padding': '24px'
}
#--------------------------------------------Main app -----------------------------------------------------------------

#App Layout
app.layout = html.Div(

    children=[

        # Top Banner
        html.Div(
            className="study-browser-banner row",
            children=[
                html.H2(className="h2-title", children="Analytics Dashboard for Chinese Antibody Society's Media Platforms"), #set widescreen title here!
                html.Div(
                    className="div-logo",
                    children=html.Img(
                        className="logo", src=app.get_asset_url("dash-logo-new.png")
                    ),
                ),
                html.H2(className="h2-title-mobile", children="CAS Analytics Dashboard"), #set mobile title here!
            ],
        ),

        # Define a list of tabs
        dcc.Tabs([

            # ----------------------------------------------------------------------------------------------------------
            #                                            1st tab - Email campaign
            # ----------------------------------------------------------------------------------------------------------
            dcc.Tab(label='Email Campaigns', style=tab_style, selected_style=tab_selected_style,   #apply my custom styles as specifid in this app (not in CSS!)
                    children=[
                # body pannel - Email campaign
                html.Div(
                    className="row app-body",
                    children=[

                        # User control box - Email Campaigns
                        html.Div(
                            className="four columns card",  #4 column here, so it is 4:8 split
                            children=[
                                html.Div(
                                    className="bg-white user-control",
                                    children=[
                                        html.Div(
                                        className="padding-top-bot",
                                        children=[
                                            #section header
                                            html.H4("Email Campaigns"),
                                            #specify dropdown box content
                                            html.H6("Select Type of Email Campaign"),
                                            dcc.Dropdown(
                                                id='article-type-dd',  #use this ID for call-back
                                                options=[{'label': i, 'value': i} for i in article_types],
                                                value='newsletter'
                                            ),

                                            # specify dropdown box content
                                            html.H6("Y axis"),
                                            dcc.Dropdown(
                                                id='y-axis',          #use this ID for call-back
                                                options=[
                                                    {'label': 'unique opens', 'value': 'unique_opens'},  #value needs to match column header
                                                    {'label': 'unique clicks', 'value':'unique_clicks'}
                                                ],
                                                value='unique_opens'  #must be the same as the value specified above
                                            ),

                                            # specify dropdown box content
                                            html.H6("Y axis type"),
                                            dcc.RadioItems(
                                                id='y-axis-dt',       #use this ID for call-back
                                                options=[{'label': i, 'value': i} for i in ['Percent', 'Total']],
                                                value='Percent',
                                                labelStyle={'display': 'inline-block'}
                                            )
                                        ],
                                        )
                                    ]
                                )
                            ]
                        ),

                        # 1st Graph - Email Campaigns
                        html.Div(
                            className="eight columns card-left",  #8 column here, so it is 4:8 split
                            children=[
                                html.Div(
                                    className="bg-white",
                                    children=[
                                        html.H4("Email Reader Engagement Trends"),
                                        dcc.Graph(id="email-trend-plot"),             #use id for callback
                                    ],
                                )
                            ],
                        ),
                    ]
                ),
            ]),

            # ----------------------------------------------------------------------------------------------------------
            #                                                   2nd tab - Website Traffic
            # ----------------------------------------------------------------------------------------------------------
            dcc.Tab(label='Website Traffic', style=tab_style, selected_style=tab_selected_style,
                    children=[

                # 1st row body pannel - small container cards for web data - Website traffic
                html.Div(
                    className="row app-body",
                    children=[

                        # 1st container card for Website traffic
                        html.Div(
                            className="four columns card-statsbox",  # 4 column here. Use my layout for stats box
                            children=[
                                html.Div(
                                    className="bg-white-container", # use my layout for contents WITHIN the small container box.
                                    children=[
                                        html.H4("Avg Unique Visitors /Day", style={'text-align': 'center'}),
                                        html.H1(id="avgVisitorText",children=["No Data"], style={'text-align': 'center'}),  #"No Data" is the default text to show if data can't be retrieved
                                    ],
                                )
                            ],
                        ),

                        # 2nd container card for Website traffic
                        html.Div(
                            className="four columns card-statsbox",  # 4 column here
                            children=[
                                html.Div(
                                    className="bg-white-container",
                                    children=[
                                        html.H4("Avg Page Views /Day", style={'text-align': 'center'}),
                                        html.H1(id="avgPagePerDay", children=["No Data"], style={'text-align': 'center'}),
                                        # "No Data" is the default text to show if data can't be retrieved
                                    ],
                                )
                            ],
                        ),

                        # 3rd container card for Website traffic
                        html.Div(
                            className="four columns card-statsbox",  # 4 column here
                            children=[
                                html.Div(
                                    className="bg-white-container",
                                    children=[
                                        html.H4("Avg Page Views /Visitor", style={'text-align': 'center'}),
                                        html.H1(id="avgPagePerVisit", children=["No Data"],
                                                style={'text-align': 'center'}),
                                        # "No Data" is the default text to show if data can't be retrieved
                                    ],
                                )
                            ],
                        ),

                    ]
                ),

                # 2nd row body pannel - Daily website traffic
                html.Div(
                    className="row app-body",
                    children=[
                        # user control box - Website traffic
                        html.Div(
                            className="four columns card",  # 4 column here, so it is 4:8 split
                            children=[
                                html.Div(
                                    className="bg-white user-control",
                                    children=[
                                        html.Div(
                                            className="padding-top-bot",
                                            children=[
                                                # section header
                                                html.H4("Daily Website Stats"),
                                                # specify dropdown box content
                                                html.H6("Select (multiple) stats to view"),
                                                dcc.Dropdown(
                                                    id='web-stats-type',  # use this ID for call-back
                                                    options=[{'label': i, 'value': i} for i in webStatsList],
                                                    value=['pageviews_all', 'unique_visitors'],
                                                    multi=True,
                                                )
                                            ],
                                        )
                                    ]
                                )
                            ]
                        ),

                        # Graph - Daily website traffic
                        html.Div(
                            className="eight columns card-left",  # 8 column here, so it is 4:8 split
                            children=[
                                html.Div(
                                    className="bg-white",
                                    children=[
                                        html.H4("Daily Stats on Website Traffic"),
                                        dcc.Graph(id="web-trend-plot"),  # use id for callback
                                    ],
                                )
                            ],
                        ),
                    ]
                ),

                # 3rd row body pannel -  Cumulative website stats
                html.Div(
                    className="row app-body",
                    children=[
                        html.Div( className="four columns card",  #4 column here, so it is 4:8 split,
                            children=[
                                html.Div(
                                    className="bg-white user-control",
                                    children=[
                                        html.Div(
                                        className="padding-top-bot",
                                        children=[
                                            #section header
                                            html.H4("Cumulative Website Stats"),
                                            html.H6("Select a time period. The earliest is 2020-05-15"),

                                            #select date range
                                            dcc.DatePickerRange(
                                                id='web-date-picker',
                                                display_format='YYYY-MM-DD',
                                                start_date_placeholder_text='YYYY-MM-DD',
                                                min_date_allowed=dt(2020, 5, 15),             #must pass python datetime variable!
                                                max_date_allowed=webMaxDate+timedelta(1),     #the max date is grayed out. so I need to add 1 day
                                                start_date=dt(2020, 5, 15),                   #default start_date
                                                end_date=webMaxDate,                          #default end_date
                                            ),

                                            #multi select dropdown box
                                            html.H6("Select (multiple) stats to view"),
                                            dcc.Dropdown(
                                                    id='web-cumstats-type',  # use this ID for call-back
                                                    options=[{'label': i, 'value': i} for i in webCumStatsList],
                                                    value=['pageviews_all', 'unique_visitors'],
                                                    multi=True,
                                            ),

                                            #notes section
                                        ],
                                        )
                                    ]
                                )
                            ]
                        ),

                        # Graph for cumulative web stats
                        html.Div(
                            className="eight columns card-left",  # 8 column here, so it is 4:8 split
                            children=[
                                html.Div(
                                    className="bg-white",
                                    children=[
                                        html.H4("Cumulative Stats on Website Traffic"),
                                        dcc.Graph(id="web-cumstats-chart"),  # use id for callback
                                    ],
                                )
                            ],
                        ),
                    ]
                ),



                # 4rd row body pannel - Website traffic geo data
                html.Div(
                    className="row app-body",
                    children=[

                        # 2rd Graph - Website traffic
                        html.Div(
                            className="card-center",  # 12 column here
                            children=[
                                html.Div(
                                    className="bg-white-alt",
                                    children=[
                                        html.H4("Total Number of Requests Per Day by Geography"),
                                        dcc.Graph(id="web-traffic-geo", style={"width":"100%", 'padding': '0px'}),  # use id for callback
                                        dcc.Slider(
                                            id='web-traffic-slider',
                                            min=0,               #note that the slider returns numbers, not text!!
                                            max=numEntries-1,
                                            value=numEntries//2, #default slider position
                                            # marks=markDict,
                                            step=1,
                                            updatemode="drag",
                                            persistence="true",
                                        ),
                                        html.H6(id="web-traffic-legend", style={'text-align': 'center', 'margin-top': 0, 'padding-top': 0}),
                                    ],
                                )
                            ],
                        ),
                    ]
                ),

            ]),

            #----------------------------------------------------------------------------------------------------------
            #                                                   3rd tab - WeChat
            #----------------------------------------------------------------------------------------------------------
            dcc.Tab(label='WeChat', style=tab_style, selected_style=tab_selected_style,
                children=[


                    # 1st row body pannel - WeChat follower
                    html.Div(
                        className="row app-body",
                        children=[
                            html.Div( className="four columns card",  #4 column here, so it is 4:8 split,
                                children=[
                                    html.Div(
                                        className="bg-white user-control",
                                        children=[
                                            html.Div(
                                            className="padding-top-bot",
                                            children=[
                                                #section header
                                                html.H4("WeChat Follower Stats"),
                                                html.H6("Select a time period. The earliest is 2016-08-15"),

                                                #select date range
                                                dcc.DatePickerRange(
                                                    id='wechat-date-picker',
                                                    display_format='YYYY-MM-DD',
                                                    start_date_placeholder_text='YYYY-MM-DD',
                                                    min_date_allowed=dt(2016, 8, 15),             #must pass python datetime variable!
                                                    max_date_allowed=wechatMaxDate+timedelta(1),  #the max date is grayed out. so I need to add 1 day
                                                    start_date=dt(2016, 8, 15),                   #default start_date
                                                    end_date=wechatMaxDate,                       #default end_date
                                                ),

                                                #multi select dropdown box
                                                html.H6("Select (multiple) stats to view"),
                                                dcc.Dropdown(
                                                    id='wechat-follower-stats-type',  # use this ID for call-back
                                                    options=[{'label': i, 'value': i} for i in wechatFollowerStatsList],
                                                    value=['net_increase', 'total'],
                                                    multi=True,
                                                ),

                                                #notes section
                                                html.H6("Notes: "),
                                                html.Span("new-新增人数, unfollowed-取消关注人数, net_increase-净增人数, total-累计关注人数")

                                            ],
                                            )
                                        ]
                                    )
                                ]
                            ),

                            #Graph for wechat follower chart
                            html.Div(
                                className="eight columns card-left",  # 8 column here, so it is 4:8 split
                                children=[
                                    html.Div(
                                        className="bg-white",
                                        children=[
                                            html.H4("Number of WeChat Followers Over Time, Measured Daily"),
                                            dcc.Graph(id="wechat-follower-chart"),  # use id for callback
                                        ],
                                    )
                                ],
                            ),
                        ]
                    ),

                    #2nd row body pannel - wechat article
                    html.Div(
                        className="row app-body",
                        children=[
                            html.Div( className="four columns card",  #4 column here, so it is 4:8 split,
                                children=[
                                    html.Div(
                                        className="bg-white user-control",
                                        children=[
                                            html.Div(
                                            className="padding-top-bot",
                                            children=[
                                                #section header
                                                html.H4("WeChat Article Stats"),
                                                html.H6("Select a time period. The earliest is 2017-01-01"),

                                                #select date range
                                                dcc.DatePickerRange(
                                                    id='wechat-article-date-picker',
                                                    display_format='YYYY-MM-DD',
                                                    start_date_placeholder_text='YYYY-MM-DD',
                                                    min_date_allowed=dt(2017, 1, 1),              #must pass python datetime variable!
                                                    max_date_allowed=wechatMaxDate+timedelta(1),  #the max date is smae as the follwer max date - they're from the sam esource!
                                                    start_date=dt(2017, 1, 1),                    #default start_date
                                                    end_date=wechatMaxDate,                       #default end_date
                                                ),

                                                #multi select dropdown box
                                                html.H6("Select (multiple) stats to view"),
                                                dcc.Dropdown(
                                                    id='wechat-article-stats-type',  # use this ID for call-back
                                                    options=[{'label': i, 'value': i} for i in wechatArticleStatsList],
                                                    value=["reads","shares"],
                                                    multi=True,
                                                ),

                                                # notes section
                                                html.H6("Notes: "),
                                                html.Span(
                                                    "reads-阅读次数, shares-分享次数, saves-收藏次数, jump_to_original-转跳原文次数")
                                            ],
                                            )
                                        ]
                                    )
                                ]
                            ),

                            #Graph for wechat article stats
                            html.Div(
                                className="eight columns card-left",  # 8 column here, so it is 4:8 split
                                children=[
                                    html.Div(
                                        className="bg-white",
                                        children=[
                                            html.H4("Total Article Reads, Shares, Saves, and Jump to Originals, Measured Daily"),
                                            dcc.Graph(id="wechat-article-chart"),  # use id for callback
                                        ],
                                    )
                                ],
                            ),
                        ]
                    ),

                    # 3rd row body pannel - Source of article: How did WeChat readers found the article?
                    html.Div(
                    className="row app-body",
                    children=[

                        # Chart for source of WeChat article
                        html.Div(
                            className="card-tight-top",  # 12 column here
                            children=[
                                html.Div(
                                    className="bg-white",
                                    children=[
                                        html.H4("How did readers find out about this (these) article(s)? - 传播渠道分析"),
                                        html.P("Use lasso or box tool in the chart above to select individual point(s) for analysis here. Default analysis (upon page load/refresh) is the average of all data since 2017-01-01"),
                                        dcc.Graph(id='wechatSource'),
                                    ],
                                )
                            ],
                        ),
                    ]
                ),

                ]
            ),
        ]),


        # Footer
        html.Div(
            className="study-browser-banner row",
            children=[
                html.P("Chinese Antibody Society 2020."), #set widescreen title here!
            ],
        ),

    ]
)

#--------------------------------------------Call backs ---------------------------------------------------------------


#call back for the email-campaign chart
@app.callback(

    #OUTPUT SYNTAX: (dcc.Graph ID, 'figure') 'figure' is required here
    Output('email-trend-plot', 'figure'),   #DO NOT use [] if output is only 1 item!!
    [
        #INPUT SYNTAX: (dcc.Dropdown or dcc.Radio ID, 'value). 'value is required here
        Input('article-type-dd', 'value'),  #column [article_type]
        Input('y-axis', 'value'),           #column [unique_opens, unique_clicks]
        Input('y-axis-dt', 'value')         # "Total" or "Percent" for Y axis
    ]
)
def update_graph(email_type, open_or_click, number_or_ratio):
    """
    Link email campaign graph to callback above
    :param email_type:      user-input value of article-type-dd in callback
    :param open_or_click:   user-input value of y-axis in callback
    :param number_or_ratio: user-input value of y-axis-dt in callback
    :return: x and y axis data in dict format
    """
    dff=df[df['article_type']==email_type]

    #if user wants to see percent, calculate percent
    if number_or_ratio=="Percent":

        #if it is unique_opens, we need to load industry avg open rate
        if open_or_click=="unique_opens":
            return {
                'data':[
                    {
                        "x": dff['send_time_date'],  # var must be named x
                        "y": dff[open_or_click] / dff["delivered"],
                        "mode": 'lines+markers',
                        "name": "unique open rate",
                        "marker": {  # marker style
                            'size': 15,
                            'opacity': 0.5,
                            'line': {'width': 0.5, 'color': 'white'}
                        }
                    },
                    {
                        "x": dff['send_time_date'],  # var must be named x
                        "y": dff["ind_open_rate"],   #load industry open rate
                        "mode": 'lines+markers',
                        "name": "industry open rate",
                        "marker": {  # marker style
                            'size': 15,
                            'opacity': 0.5,
                            'line': {'width': 0.5, 'color': 'white'}
                        }
                    },

                ],
                'layout': general_layout
            }

        # else it is unique_clicks, we need to load industry avg click rate
        else:
            return {
                'data': [
                    {
                        "x": dff['send_time_date'],  # var must be named x
                        "y": dff[open_or_click] / dff["delivered"],
                        "mode": 'lines+markers',
                        "name": "unique click rate",
                        "marker": {  # marker style
                            'size': 15,
                            'opacity': 0.5,
                            'line': {'width': 0.5, 'color': 'white'}
                        }
                    },
                    {
                        "x": dff['send_time_date'],  # var must be named x
                        "y": dff["ind_click_rate"],  # load industry avg click rate
                        "mode": 'lines+markers',
                        "name": "industry click rate",
                        "marker": {  # marker style
                            'size': 15,
                            'opacity': 0.5,
                            'line': {'width': 0.5, 'color': 'white'}
                        }
                    },

                ],
                'layout': general_layout
            }


    #If user wants number, show the total number
    else:
        return {
            'data': [                               # must be named 'data'
                {
                    "x": dff['send_time_date'],     # var must be named x
                    "y": dff['delivered'],          # var must be named y
                    "mode": 'markers',              # graph mode, line or markers. Must be named "mode"
                    "name": "total delivered",      # legend name. Must be named "name"
                    "marker": {                     # marker style. Must be named "marker"
                        'size': 15,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
                },

                {
                    "x":dff['send_time_date'],  # var must be named x
                    "y":dff[open_or_click],  # var must be named y
                    "mode": 'lines+markers',  # graph mode, line or maker
                    "name": "unique opens/clicks",
                    "marker":{  # marker style
                            'size': 15,
                            'opacity': 0.5,
                            'line': {'width': 0.5, 'color': 'white'}
                        }
                }
            ],
            'layout':general_layout
        }


#call back for the web-stats chart
@app.callback(

    Output('web-trend-plot', 'figure'), #OUTPUT SYNTAX: (dcc.Graph ID, 'figure') 'figure' is required here

    [
        #INPUT SYNTAX: (dcc.Dropdown or dcc.Radio ID, 'value). 'value is required here
        Input('web-stats-type', 'value'),  #column ['requests_all', 'threats_all', 'pageviews_all','unique_visitors', 'pageview_per_visitor']
    ]
)
def update_webstat_graph(stat_types):
    """
    updates website stat trends chart above
    :param stat_types: columns selected by the user, in a list. webStatsList= ['requests_all', 'threats_all', 'pageviews_all','unique_visitors', 'pageview_per_visitor']
    :return: data for plotting
    """

    webstat_data=[]  # use this as the return value for 'data' - a list of dict, where each dict is a line

    for stat in stat_types:  #iterate through hte list of columns that the user has chosen
        dat_dict={
                    "x": df2['date'],  # var must be named x
                    "y": df2[stat],  # var must be named y
                    "mode": 'markers+lines',  # graph mode, line or markers. Must be named "mode"
                    "name": stat,  # legend name. Must be named "name".
                    "marker": {  # marker style. Must be named "marker"
                        'size': 15,
                        'opacity': 0.5,
                        'line': {'width': 0.5, 'color': 'white'}
                    }
            }
        webstat_data.append(dat_dict)

    return{
        'data':webstat_data,  #this is a list of dicts, where each dict is a line,
        'layout': general_layout
    }


#Call back for returning simple text to web traffic
@app.callback(
    [
        Output('avgVisitorText', 'children'),
        Output('avgPagePerDay', 'children'),
        Output('avgPagePerVisit', 'children')
    ],

    [
        Input('web-stats-type', 'value'),  #seems like you must put something even if you don't need it...
    ]
)
def updateWebStatText(stat_types):

    #do some calc here
    avgVisitorPerDay=round(df2["unique_visitors"].sum()/df2.shape[0], 0)
    avgPagePerDay=round(df2['pageviews_all'].sum()/df2.shape[0], 0)
    avgPagePerVisit=round(df2['pageviews_all'].sum()/df2["unique_visitors"].sum(), 1)

    #each returning var matches to an output destination in the call back. For example,`avgVisitorPerDay` matches to `Output('avgVisitorText', 'children')`
    return avgVisitorPerDay,avgPagePerDay, avgPagePerVisit


#call back for cumulative website stats
@app.callback(
    Output('web-cumstats-chart', 'figure'),

    [
        #For date range picker, there are 2 inputs from user. BOTH inputs are returned to the program as STRINGS in the format user entered. This format is specified in dcc.DatePickerRange{display_format='YYYY-MM-DD'}. i.e. here, the user input is returend as "2020-01-01"
        Input('web-date-picker', 'start_date'),
        Input ('web-date-picker', "end_date") ,    #`web-date-picker` is the ID of the date pikcer. `start_date` and `end_date` are fixed expression you must use
        Input('web-cumstats-type', 'value')  #columns ['requests_all', 'threats_all', 'pageviews_all','unique_visitors']
    ]
)
def webCumStats(startDate, endDate, statsList):    #startDate = start_date in the input, endDate = end_date in the input. BOTH ARE STRINGS

    #filter by the date range
    criteria = (df2.date >= startDate) & (df2.date <= endDate)
    df2f=df2[criteria]

    #calculate cumulative stats columns
    def get_cum_stats(colName):
        """
        add a cumulative stats column
        :param colName: STR, original column name, such as `requests_all`
        :return: STR, column name for the new cumulative stat. Note that the new stat column is added to df2f directly
        """
        newColName=colName+'_cumsum'
        df2f[newColName] = df2f[colName].cumsum()
        return newColName

    #iterate through the stats list that the user selected, add them to the `data` list
    webCumStats_data=[]
    for stat in statsList:

        # get a cumulative stat
        cumStatColName= get_cum_stats(stat)

        # add trace data to the list of dicts
        data_dict = {
            "x": df2f['date'],  # var must be named x
            "y": df2f[cumStatColName],  # var must be named y
            "mode": 'markers+lines',  # graph mode, line or markers. Must be named "mode"
            "name": stat,  # legend name. Must be named "name".
            "marker": {  # marker style. Must be named "marker"
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        }
        webCumStats_data.append(data_dict)

    return {
        'data': webCumStats_data,  # this is a list of dicts, where each dict is a line graph
        'layout': general_layout
    }


#call back for web trafic geo
@app.callback(
    [
        Output('web-traffic-geo', 'figure'),
        Output('web-traffic-legend', 'children')
    ],
    [
        Input('web-traffic-slider', 'value'),  #returns string date like 2020-05-15 (which has a value of 0). You need to use markDict to convert that to strin,g then conver to datetime
    ]
)
def updateWebTrafficGeo(whatDate):

    # filter using the user-selected date
    df2f=df2[df2["date"]==markDict[whatDate]]

    # extract the country requests dict
    countryDict=ast.literal_eval(df2f.requests_country.ravel()[0])
    countryDf = pd.DataFrame({
        "country": list(countryDict.keys()),
        "requests": list(countryDict.values())  #total number of requests from each country
    })

    # combine `countryDf` dataframe (containing the reqeusts) with `country_code` dataframe (containing standard country codes in 2/3 letters)
    mergedCountryDf = pd.merge(countryDf, country_code, left_on="country", right_on="2_letter")

    # create a figure
    fig=go.Figure()

    # add trace. Note that the names for arugments are different from the px.choropleth_mapbox() function.
    # Read the go.Choroplethmapbox() documentation for details!
    fig.add_trace(
        go.Choroplethmapbox(geojson=countries_geo_json,                 # geo json file in json format
                            locations=mergedCountryDf['3_letter'],      # column in the dataframe with the 3_letter fips code
                            z=mergedCountryDf['requests'],              # column in the dataframe with the stats you want to plot
                            zmin=minReq,                                # if a shared colobar is used, you can specify the global min on the color bar
                            zmax=maxReq,                                # if a shared colobar is used, you can specify the global min on the color bar
                            colorscale="Plasma")                        # color map to use
    )

    # update the mapbox layout.
    # Note that the names for arugments are different from the px.choropleth_mapbox() function.
    # specifically, you need to add `mapbox_` to the mapbox parameters!
    fig.update_layout(
        mapbox_accesstoken=mapbox_token,                    # your mapbox token
        mapbox_style="carto-positron",                      # mapbox style
        mapbox_center={"lat": 41.141478, "lon": 3.169980},  # center on mediterranean sea
        mapbox_zoom=1                                       # zoom 1
    )

    # update the graph layout
    fig.update_layout(
        autosize=True,
        margin=dict(t=0, b=20, l=2, r=2)
    )

    # another way to write the layout...
    # mapbox_layout = {
    #     "hovermode": "compare",
    #     "autosize": True,
    #     "margin": dict(t=0, b=2, l=2, r=2),
    #     "mapbox": {
    #         "accesstoken": mapbox_token,
    #         "center": {"lat": 40.363062, "lon": 178.253897},  # center on the north pacific ocean
    #         "zoom": 0.5,
    #         "mapbox_style": "carto-positron"
    #     }
    # }

    mapLegend="Move slider or use keyboard arrow to select date. Currently date = " + markDict[whatDate]

    return fig, mapLegend    #return 2 things here! Direclty return the fig object

#call back for wechat follower
@app.callback(
    Output('wechat-follower-chart', 'figure'),

    [
        #For date range picker, there are 2 inputs from user. BOTH inputs are returned to the program as STRINGS in the format user entered. This format is specified in dcc.DatePickerRange{display_format='YYYY-MM-DD'}. i.e. here, the user input is returend as "2020-01-01"
        Input('wechat-date-picker', 'start_date'),
        Input ('wechat-date-picker', "end_date") ,    #`wechat-date-picker` is the ID of the date pikcer. `start_date` and `end_date` are fixed expression you must use
        Input('wechat-follower-stats-type', 'value')  #columns ["new","unfollowed","net_increase","total"]
    ]
)
def wechatFollwer(startDate, endDate, statsList):    #startDate = start_date in the input, endDate = end_date in the input. BOTH ARE STRINGS

    #filter by the date range
    criteria = (df3.date >= startDate) & (df3.date <= endDate)
    df3f=df3[criteria]

    #iterate through the stats list that the user selected, add them to the `data` list
    follower_data=[]
    for stat in statsList:
        data_dict = {
            "x": df3f['date'],  # var must be named x
            "y": df3f[stat],  # var must be named y
            "mode": 'markers+lines',  # graph mode, line or markers. Must be named "mode"
            "name": stat,  # legend name. Must be named "name".
            "marker": {  # marker style. Must be named "marker"
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        }
        follower_data.append(data_dict)

    return {
        'data': follower_data,  # this is a list of dicts, where each dict is a line,
        'layout': general_layout
    }

#call back for wechat article
@app.callback(
    Output('wechat-article-chart', 'figure'),

    [
        #For date range picker, there are 2 inputs from user. BOTH inputs are returned to the program as STRINGS in the format user entered. This format is specified in dcc.DatePickerRange{display_format='YYYY-MM-DD'}. i.e. here, the user input is returend as "2020-01-01"
        Input('wechat-article-date-picker', 'start_date'),
        Input ('wechat-article-date-picker', "end_date") ,    #`start_date` and `end_date` are fixed expression you must use
        Input('wechat-article-stats-type', 'value')           #columns ["reads","shares","jump_to_original","saves"]
    ]
)
def wechatArticle(startDate, endDate, statsList):    #startDate = start_date in the input, endDate = end_date in the input. BOTH ARE STRINGS

    #filter by the date range
    criteria = (df4.date >= startDate) & (df4.date <= endDate)
    df4f=df4[criteria]

    #iterate through the stats list that the user selected, add them to the `data` list
    article_data=[]
    for stat in statsList:
        data_dict = {
            "x": df4f['date'],  # var must be named x
            "y": df4f[stat],  # var must be named y
            "mode": 'markers+lines',  # graph mode, line or markers. Must be named "mode"
            "name": stat,  # legend name. Must be named "name".
            "marker": {  # marker style. Must be named "marker"
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        }
        article_data.append(data_dict)

    return {
        'data': article_data,  # this is a list of dicts, where each dict is a line,
        'layout': general_layout
    }

#Call back for the wechat article source chart
@app.callback(
    Output('wechatSource', 'figure'),
    [
        Input('wechat-article-chart', 'selectedData')  #`wechat-article-chart` is the figure ID. `selectedData` is s fixed expression you must use.
    ]
)
def wechatArticleSource(selectedData):   #selectedData is returned as a dict, like below:
    """
    {
  "points": [    #Points is a list of dict. Each dict is a single selected point. "x" is the value of the x axis, and "y" the "y axis" of that point. If nothing is selected, it will return "null". Therefore you can set an default option to show if the user doesn't click on anything.
    {
      "curveNumber": 0,
      "pointNumber": 3,
      "pointIndex": 3,
      "x": 4,
      "y": 5,
      "customdata": "c.d",
      "text": "d"
    }
  ],
  "lassoPoints": {
    "x": [
      3.905970149253732,
      4.001492537313434,
    ],
    "y": [
      5.526315789473683,
      5.280701754385964,
    ]
  }
}
    :param selectedData:
    :return:
    """
    ch=['公众号消息', '其它', '历史消息', '搜一搜', '朋友圈', '朋友在看', '看一看精选', '聊天会话']  #list of possible channels

    data_dict = {
        'channels': ch,
        'percent': [],
    }

    if selectedData!= None:               #if points are selected
        pointList=selectedData["points"]  #a list of dicts
        dateList=[]                       #a list of lasso selected x values (which is date)
        for point in pointList:           #get the x value (date) of the points the user selected
            dateList.append(point["x"])

        df5f = df5[df5['date'].isin(dateList)]    #filter through the df5 for only the dates that the user selected

        # for each channel, sum up the numbers, then divide by total to get the percentage. Round to the 4th decimal so the numbers sum up to 1
        total = df5f['全部'].sum()
        for channel in data_dict['channels']:
            data_dict['percent'].append(round(df5f[channel].sum() / total, 4))

        dataDf=pd.DataFrame(data_dict)    #put the data in a clean dict for plotting using px

        fig = px.bar(dataDf, x='channels', y='percent', color='channels')  #color each by by channel

        fig.update_layout(           #update the layout
            autosize=True,
            template="plotly_white", #get rid of the default light blue background
            margin=dict(t=20, b=35, l=10, r=10),
            showlegend=False  #legend is the color code, we don't need it
        )

        return fig     #just return the fig

    else:  #if no points are selected, it will return an empty dict {}, we will show the graph with averaged across all datapoints

        total = df5['全部'].sum()
        for channel in data_dict['channels']:
            data_dict['percent'].append(round(df5[channel].sum() / total, 4))  #keeep 4 digits otherwise the numbers might not add up to 1

        dataDf=pd.DataFrame(data_dict)

        fig = px.bar(dataDf, x='channels', y='percent', color='channels')  #color each by by channel

        fig.update_layout(
            autosize=True,
            template="plotly_white", #get rid of the default light blue background
            margin=dict(t=20, b=20, l=40, r=10),
            #margin=dict(t=20, b=35, l=10, r=10),
            height=300,       #still responsive. no worries!
            showlegend=False,  #legend is the color code, we don't need it
        )

        return fig

#
#
#

if __name__ == "__main__":
    application.run(debug=True, port=8080)
