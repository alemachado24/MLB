import pandas as pd
import numpy as np
import streamlit as st
import json
import requests
from urllib.request import urlopen
import plotly.express as px

#cd Desktop/AleClasses/MLB
#streamlit run mlb.py

st.set_page_config(page_title="MLB", page_icon="⚾️",layout="wide",)

st.sidebar.markdown("MLB Forecast ⚾️")

st.caption("This app performs simple webscraping of MLB player stats data")
st.caption("Data Sources: fivethirtyeight Website")# and pro-basketball-reference

#sidebar
selected_year = st.sidebar.selectbox('Year', list(reversed(range(2020,2024))))

team_names = ['Dodgers',
'Astros',
'Braves',
'Yankees',
'Mets',
'Padres',
'Blue Jays',
'Guardians',
'Rays',
'Brewers',
'Cardinals',
'Twins',
'Phillies',
'Angels',
'Mariners',
'Giants',
'Rangers',
'Red Sox',
'White Sox',
'Marlins',
'Cubs',
'Orioles',
'Diamondbacks',
'Reds',
'Pirates',
'Rockies',
'Tigers',
'Royals',
'Athletics',
'Nationals']

# selected_team_full = st.multiselect('',team_names,default = team_names[25])

# if selected_team_full[0] == 'Astros':
#     short_name = 'HOU'
# elif selected_team_full[0] == 'Dodgers':
#     short_name = 'LAD'
# elif selected_team_full[0] == 'Braves':
#     short_name = 'ATL'
# elif selected_team_full[0] == 'Yankees':
#     short_name = 'NYY'
# elif selected_team_full[0] == 'Mets':
#     short_name = 'NYM'
# elif selected_team_full[0] == 'Padres':
#     short_name = 'SD'
# elif selected_team_full[0] == 'Blue Jays':
#     short_name = 'TOR'
# elif selected_team_full[0] == 'Guardians':
#     short_name = 'CLE'
# elif selected_team_full[0] == 'Rays':
#     short_name = 'TB'
# elif selected_team_full[0] == 'Brewers':
#     short_name = 'MIL'
# elif selected_team_full[0] == 'Cardinals':
#     short_name = 'STL'
# elif selected_team_full[0] == 'Twins':
#     short_name = 'MIN'
# elif selected_team_full[0] == 'Phillies':
#     short_name = 'PHI'
# elif selected_team_full[0] == 'Angels':
#     short_name = 'LAA'
# elif selected_team_full[0] == 'Mariners':
#     short_name = 'SEA'
# elif selected_team_full[0] == 'Giants':
#     short_name = 'SF'
# elif selected_team_full[0] == 'Rangers':
#     short_name = 'TEX'
# elif selected_team_full[0] == 'Red Sox':
#     short_name = 'BOS'
# elif selected_team_full[0] == 'White Sox':
#     short_name = 'CHW'    
# elif selected_team_full[0] == 'Marlins':
#     short_name = 'MIA'
# elif selected_team_full[0] == 'Cubs':
#     short_name = 'CHC'
# elif selected_team_full[0] == 'Orioles':
#     short_name = 'BAL'  
# elif selected_team_full[0] == 'Diamondbacks':
#     short_name = 'ARI'
# elif selected_team_full[0] == 'Reds':
#     short_name = 'CIN'
# elif selected_team_full[0] == 'Pirates':
#     short_name = 'PIT'
# elif selected_team_full[0] == 'Rockies':
#     short_name = 'COL'
# elif selected_team_full[0] == 'Tigers':
#     short_name = 'DET'
# elif selected_team_full[0] == 'Royals':
#     short_name = 'KC'
# elif selected_team_full[0] == 'Athletics':
#     short_name = 'OAK'
# elif selected_team_full[0] == 'Nationals':
#     short_name = 'WSH'


# store the URL in url as 
# parameter for urlopen
url = f'https://projects.fivethirtyeight.com/{selected_year}-mlb-predictions/data.json'
  
# store the response of URL
response = urlopen(url)
  
# storing the JSON response 
# from url in data
data_json = json.loads(response.read())

data = []
for row in data_json['games']:
    data.append(row)

# print(url)
df = pd.json_normalize(data)

df_final=df.drop(['id','datetime','neutral','pitcher1_id','pitcher2_id','pitcher1',
                  'pitcher2','playoff','rating1','rating2','rating1_post',
                  'rating2_post','dist_adj1','dist_adj2','rest_adj1','rest_adj2',
                 'pitcher_adj1','pitcher_adj2','opener1','opener2','hfa_adj',
                 'favorite','underdog','favprob','dogprob'], axis=1)

first_column = df_final.pop('date')
  
# first_column) function
df_final.insert(1, 'Date', first_column)
# df_final['team1'] = df_final['team1'].str.replace(df_final['team1'],selected_team_full[0])

df_final['prob2'] = df_final['prob2']*100
df_final['prob1'] = df_final['prob1']*100

upcoming_games = df_final.loc[df_final['status']=='pre']
past_games = df_final.loc[df_final['status']=='post']

upcoming_games=upcoming_games.drop(['status','score1','score2'], axis=1)

def color_negative_red(val):
    '''
    highlight the maximum in a Series yellow.
    '''
    color = 'lightgreen' if str(val) > str(65) else 'white'
    return 'background-color: %s' % color
upcoming_games_color = upcoming_games.style.format(precision=0).applymap(color_negative_red, subset=['prob1','prob2'])


predicted = np.where((((past_games['score1']>past_games['score2']) & (past_games['prob1']>past_games['prob2'])) | ((past_games['score1']<past_games['score2']) & (past_games['prob1']<past_games['prob2']))) , 'Predicted', 'Turnaround')

new_analysis = np.where((past_games['score1']>past_games['score2']) , 'W', 'L')

column_results=pd.DataFrame(new_analysis, columns=['Results'])
column_predicted=pd.DataFrame(predicted, columns=['Predicted'])

combined_list = pd.concat([past_games,column_results,column_predicted], axis=1)

combined_list=combined_list.drop(['status'], axis=1)

groupped_scores = combined_list.groupby(['prob1','Results','Predicted']).size()

st.header('Upcoming Games')
st.dataframe(upcoming_games_color)

st.header('Past Games')
st.dataframe(combined_list)

def update_bar_chart(x):
    df = combined_list #px.data.tips() # replace with your own data source
    mask = df["prob1"] == x
    fig = px.histogram(df[mask], x="Results", y="prob1",
             color='Predicted', barmode='group',
             histfunc='count',#text_auto=True,
             height=400)
    return fig

# fig = update_bar_chart(prob1)


# st.plotly_chart(fig, theme="streamlit", use_container_width=True)

st.header('Historic Probabilities')
option1, option2 = st.columns(2)
with option1:
    st.dataframe(groupped_scores)
with option2:
    list_prob = round(combined_list['prob1'],0).sort_values(ascending=False).unique()
    prob1 = st.selectbox('Probability', list_prob)
    fig = update_bar_chart(prob1)
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
