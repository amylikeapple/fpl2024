#%%
import pandas as pd
from scipy import stats
import requests
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(
    page_title='FPL 23/24 Team Optimizer',
    layout='wide',
    page_icon='⚽'
)

st.header('FPL 23/24 Team Optimizer')

#Ask for Team ID
#%%
team_id = st.number_input(
    'Input Your Team ID:',
    step=1,
    value=6806921
)

@st.cache_data(ttl=3600)
def gameweek_auto():
    url4 = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    with requests.get(url4) as f:
        d = f.json()
    d = pd.json_normalize(d['events'])
    d = d[d['finished'] == True].tail(1).iloc[0][0]
    return d

default_gw_value = gameweek_auto()

#%%
#Ask for Gameweek
gameweek = default_gw_value
#gameweek = st.number_input(
#    'Input Gameweek',
#    min_value=1,
#    max_value=38,
#    value=default_gw_value
#)

#if gameweek - 1 or gameweek +1:
#    st.cache_data.clear()

gameweek_m_1 = gameweek - 1

#%%
@st.cache_data(ttl=3600)
def master_table():
    #Get Master Table
    url = 'https://drive.google.com/file/d/1f-q5duVoamPtC9kZxvyXLPANdcYYzBKE/view?usp=sharing'
    url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
    df = pd.read_csv(url)
    df = df.drop('Unnamed: 0',axis=1)
    return df


@st.cache_data(ttl=3600)
def metrics_data(team_id,gameweek):
    #Get Gameweek Metrics Data
    team_id = team_id
    gameweek = gameweek
    strr = 'https://fantasy.premierleague.com/api/entry/{}/event/{}/picks/'
    urlteam = strr.format(team_id,gameweek)

    with requests.get(urlteam) as f:
        df2 = f.json()

    df2 = pd.json_normalize(df2['entry_history'])
    return df2

@st.cache_data(ttl=3600)
def average_score():
    url3 = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    with requests.get(url3) as f:
        d = f.json()
    d = pd.json_normalize(d['events'])
    return d

@st.cache_data(ttl=3600)
def gameweek_data(team_id, gameweek):
    #Get Gameweek Picks
    team_id = team_id
    gameweek = gameweek
    strr = 'https://fantasy.premierleague.com/api/entry/{}/event/{}/picks/'
    urlteam = strr.format(team_id,gameweek)

    with requests.get(urlteam) as f2:
        df3 = f2.json()

    df3 = pd.json_normalize(df3['picks'])
    return df3 

@st.cache_data(ttl=3600)
def metric_data_prev(team_id, gameweek):
    team_id = team_id
    gameweek = gameweek
    strr = 'https://fantasy.premierleague.com/api/entry/{}/event/{}/picks/'
    urlteam = strr.format(team_id,gameweek)

    with requests.get(urlteam) as f3:
        df4 = f3.json()

    df4 = pd.json_normalize(df4['entry_history'])
    return df4    

master_table = master_table()
#%%
master_table = master_table.rename(columns={f'{list(master_table.columns)[50]}':'PP_GW'})
metrics_data =metrics_data(team_id,gameweek)
average_score = average_score()
gameweek_data = gameweek_data(team_id,gameweek)
metric_data_prev = metric_data_prev(team_id,gameweek_m_1)
#%%

#Insert Key Metrics
col1,col2,col3,col4 = st.columns(4)

with col1:
    loc_selector = gameweek - 1
    metric = average_score.loc[loc_selector][3]

    st.metric(
        label=f'Gameweek {gameweek} Average Points',
        value=metric
    )

with col2:
    metric = metrics_data.loc[0][1]

    st.metric(
        label=f'Your Gameweek {gameweek} Points',
        value=metric
    )

with col3: 
    metric = metrics_data.loc[0][3]
    prev_gameweek = metric_data_prev.loc[0][3]
    delta = prev_gameweek - metric

    st.metric(
        label=f'Your Rank',
        value="{:,}".format(metric),
        delta="{:,}".format(int(delta))
    )

with col4: 
    metric = metrics_data.loc[0][6]

    st.metric(
        label=f'Left In Bank',
        value=metric
    )

#%%
#Prepare weekly score table

weekly_table = pd.merge(gameweek_data,master_table,how='left',left_on='element',right_on='ID')

#%%
weekly_table = weekly_table[['multiplier','element',
'Name', 'Position', 'Team_x', 'Current Price',
'Points Per Game', 'Event Points','Form', 'ICT Index','Penalties Order', 
'Corners/ Indirect Order', 'Minutes', 'Influence', 'Creativity', 'Threat', 'Merit',
'Form over/under-performance over the last 4 GW', 'Prob. of Appearring',
'PP_GW', 'PPNext2', 'ValNext2', 'PPNext3',
'ValNext3', 'Selected By %','Form_%_15', 'Threat_%_15', 'Crtvty_%_15', 'Next_GW_%_15', 'PP3_%_15','xG per 90', 'xA per 90', 'xGA per 90', 'GW1_Diff', 'GW2_Diff', 'GW3_Diff', 'GW1_Home?', 'GW2_Home?', 'GW3_Home?']]

#%%

#average_points = []
#percentile = []
#pp_1_percentile = []
#pp_percentile = []
#threat_perc = []
#creativity_perc = []        
#
##column_mod = f'PPGW{gameweek+1}'
##print(column_mod)
#
#list1 = list(weekly_table['Current Price'])
#list2 = list(weekly_table['Position'])
#list3 = list(weekly_table['Form'])
#list4 = list(weekly_table['PPNext3'])
#list5 = list(weekly_table['Threat'])
#list6 = list(weekly_table['Creativity'])
#list7 = list(weekly_table['PP_GW'])
#
#for i,x,y,a,b,c,d in zip(list1,list2,list3,list4,list5,list6,list7):
#    lower_range = i-0.5
#    upper_range = i+0.5
#    pos = x
#    filtered_players = master_table.sort_values(by=['Form'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range)) & (master_table['Position'] == pos)].head(10)
#    filtered_players2 = master_table.sort_values(by=['Form'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range)) &(master_table['Position'] == pos)].head(15)
#
#    #avg_points = filtered_players['Form'].mean()
#    #avg_points = round(avg_points,1)
#
#    #Form Percentile Using Filtered Players 2
#    pt = stats.percentileofscore(filtered_players2['Form'], y, kind='rank')
#    pt = round(pt,0)
#
#    #PPNext Percenitle
#    pp_pt_1_filtered = master_table.sort_values(by=['PP_GW'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range)) &(master_table['Position'] == pos)].head(15)
#
#    pp_pt_1 = stats.percentileofscore(pp_pt_1_filtered['PP_GW'], d, kind='rank')
#    pp_pt_1 = round(pp_pt_1,0)
#
#    #PPNext3 Percentile
#    pp_pt_filtered = master_table.sort_values(by=['PPNext3'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range)) &(master_table['Position'] == pos)].head(15)
#
#    pp_pt = stats.percentileofscore(pp_pt_filtered['PPNext3'], a, kind='rank')
#    pp_pt = round(pp_pt,0)
#
#    #Threat Percentile
#    threat_perc_filtered = master_table.sort_values(by=['Threat'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range)) &(master_table['Position'] == pos)].head(15)
#
#    threat_perc_pt = stats.percentileofscore(threat_perc_filtered['Threat'], b, kind='rank')
#    threat_perc_pt = round(threat_perc_pt,0)
#
#    #Creativity Percentile
#    creativity_perc_filtered = master_table.sort_values(by=['Creativity'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range)) &(master_table['Position'] == pos)].head(15)
#
#    creativity_perc_pt = stats.percentileofscore(creativity_perc_filtered['Creativity'], c, kind='rank')
#    creativity_perc_pt = round(creativity_perc_pt,0)
#
#    percentile.append(pt)
#    pp_1_percentile.append(pp_pt_1)
#    pp_percentile.append(pp_pt)
#    threat_perc.append(threat_perc_pt)
#    creativity_perc.append(creativity_perc_pt)
#
#weekly_table['Form_%_15'] = percentile
#weekly_table['Next_GW_%_15'] = pp_1_percentile
#weekly_table['PP3_%_15'] = pp_percentile
#weekly_table['Threat_%_15'] = threat_perc
#weekly_table['Crtvty_%_15'] = creativity_perc

#%%
weekly_table_show = weekly_table[['element','Name', 'Position', 'Team_x','Current Price','Event Points','Form', 'Form_%_15', 'Influence','Threat','Threat_%_15','Creativity','Crtvty_%_15',
                             'Merit','PP_GW','Next_GW_%_15', 'PPNext2', 'PPNext3','PP3_%_15', 'Selected By %','Prob. of Appearring']]

# %%
st.header('Step 1: Assess your Gameweek Performance')
with st.expander('⬇️ Column Definitions - Read Me First!'):
    st.text('1. GW Points = Current gameweek points')
    st.text('2. Form = Average points over the past 4 gameweeks')
    st.markdown("*Heads up! An example of what percentile rank means --> 75.0 = Player is better than 75% of the top 15 players in his price bracket.*")
    st.text("3. Form Rank (%) = Player's form percentile rank ")
    st.text("4. Threat = FPL's measurement on how much the player's actions are leading to goals")
    st.text("5. Threat Rank (%) = Player threat percentile rank.")
    st.text("6. Creativity = FPL's measurement on how much the player's actions are leading to assists")
    st.text("7. Crtvty Rank(%) = Player creativity percentile rank.")
    st.text("8. Merit = FPLform's algorithm on how much we can rely on predicted scores based on recent player performance")
    st.text('9. PP Next GW: Predicted points in the next gameweek')
    st.text("10. PP Next GW Rank(%) = Player PP_GW percentile rank.")
    st.text('11. PP Next 3 GW: Predicted points in the next 3 gameweeks')
    st.text("12. PP Next 3 GW Rank(%) = Player PPNext3 percentile rank.")

#weekly_table_style = weekly_table[['Name', 'Position', 'Team_x','Current Price','Event Points','Form', 'Form_%_15','Threat_%_15','Crtvty_%_15','PP_GW','Next_GW_%_15','PPNext3','PP3_%_15','Prob. of Appearring']].style\
#                       .format(precision=2)\
#                       .background_gradient(cmap='RdYlGn',subset=pd.IndexSlice[:,['Form_%_15','PP_GW','Next_GW_%_15','PPNext3','PP3_%_15','Prob. of Appearring']])\
#%%
st.subheader("Your Gameweek Performance TLDR")

loc_selector = gameweek - 1
average_score_value = average_score.loc[loc_selector][3]
your_score_value = metrics_data.loc[0][1]
average_score_rating = ((your_score_value - average_score_value)/average_score_value)*100
form_rating = weekly_table.head(11)['Form_%_15'].mean()
potential_score_rating_1 = weekly_table.sort_values(['PP_GW'],ascending=False).head(11)['Next_GW_%_15'].mean()
potential_score_rating_3 = weekly_table.sort_values(['PPNext3'],ascending=False).head(11)['PP3_%_15'].mean()

if average_score_rating < 0:
    st.text(f"1. You scored {round(average_score_rating,1)}% below the GW average")
else:
    st.text(f"1. You scored {round(average_score_rating,1)}% above the GW average")

#st.text(f"You scored {round(average_score_rating,1)}% below the GW average")

if form_rating >=75:
    st.text(f"2. Player Form Rating: {round(form_rating,1)}/100.0 - Above Average. Your players consistently did better!")
elif 75 > form_rating >= 50  :
    st.text(f"2. Player Form Rating: {round(form_rating,1)}/100.0 - Average. Your players did alright, but no significant ground gained.")
elif 50 > form_rating >= 30:
    st.text(f"2. Player Form Rating: {round(form_rating,1)}/100.0 - Below Average. Your players consistently performed poorly.")
elif form_rating <30:
    st.text(f"2. Player Form Rating: {round(form_rating,1)}/100.0 - What were you thinking with your choices!")

#st.text(f"Player Form Rating: {round(form_rating,1)}/100.0")
if potential_score_rating_1 >= 75:
    st.text(f"3. Upcoming GW Potential Points Rating: {round(potential_score_rating_1,1)}/100.0 - Above Average. You don't need transfers!!")
elif 75 > potential_score_rating_1 >= 50:
    st.text(f"3. Upcoming GW Potential Points Rating: {round(potential_score_rating_1,1)}/100.0 - Average. Your next GW predicted point are alright.")
elif 50 > potential_score_rating_1 >= 30:
    st.text(f"3. Upcoming GW Potential Points Rating: {round(potential_score_rating_1,1)}/100.0 - Below Average. You should make some transfers. Refer to suggestions below.")
elif potential_score_rating_1 <30:
    st.text(f"3. Upcoming GW Potential Points Rating: {round(potential_score_rating_1,1)}/100.0 - Critical. You should make some transfers. Refer to suggestions below.")

#st.text(f"Upcoming GW Potential Points Rating: {round(potential_score_rating_1,1)}/100.0")

if potential_score_rating_3 >= 75:
    st.text(f"4. Upcoming 3 GW Potential Points Rating: {round(potential_score_rating_3,1)}/100.0 - Above Average. You don't need transfers!!")
elif 75 > potential_score_rating_3 >= 50:
    st.text(f"4. Upcoming 3 GW Potential Points Rating: {round(potential_score_rating_3,1)}/100.0 - Average. Your next 3 GW predicted points are alright. \nKeep a look out in the next few GW for opportunities.")
elif 50 > potential_score_rating_3 >= 30:
    st.text(f"4. Upcoming 3 GW Potential Points Rating: {round(potential_score_rating_3,1)}/100.0 - Below Average. You should make some transfers. Refer to suggestions below.")
elif potential_score_rating_3 <30:
    st.text(f"4. Upcoming 3 GW Potential Points Rating: {round(potential_score_rating_3,1)}/100.0 - Critical. You should make some transfers. Refer to suggestions below.")

#st.text(f"Upcoming 3 GW Potential Points Rating: {round(potential_score_rating_3,1)}/100.0")

st.divider()

st.markdown('*Unpacking Those Numbers In Words:*')

analysis =weekly_table.sort_values(['Form_%_15','Current Price'],ascending=[True,False])

if analysis['Form_%_15'].min() < 30:
    st.text(f"1. Your team has really suffered from {analysis.iloc[0][1]}, {analysis.iloc[1][1]} and {analysis.iloc[2][1]} as they are not doing well for players in their price bracket. \nIf their predicted points are low, prioritize transferring them.")
else:
    st.text(f"1. You should consider transferring {analysis.iloc[0][1]}, {analysis.iloc[1][1]} and {analysis.iloc[2][1]} as they are not doing well for players in their price bracket")

analysis2 = weekly_table.loc[(weekly_table['Current Price'] >= 4.7) & (weekly_table['Prob. of Appearring'] <= 0.85) & (weekly_table['PP3_%_15'] < 0.5)].sort_values(['Prob. of Appearring','PP3_%_15','Current Price'],ascending=[True,True,False])

if 1 >= len(analysis2) > 0:
    st.text(f"2. You should particularly focus on transferring {analysis2.iloc[0][1]} as he has a low probability of appearing and/or\nlow predicted points in the next 3 gameweeks")
elif 2 >= len(analysis2) > 0:
    st.text(f"2. You should particularly focus on transferring {analysis2.iloc[0][1]} and {analysis2.iloc[1][1]} as they have a low probability of appearing and/or\nlow predicted points in the next 3 gameweeks")
elif 3 >= len(analysis2) > 0:
    st.text(f"2. You should particularly focus on transferring {analysis2.iloc[0][1]}, {analysis2.iloc[1][1]} and {analysis2.iloc[2][1]} as they have a low probability of appearing and/or\nlow predicted points in the next 3 gameweeks")
elif len(analysis2) > 3:
    st.text("2. You should consider wildcarding, you have too many weak points in your team.")
elif len(analysis2) == 0:
    st.text(" ")

#%%
st.text("")
weekly_table_aggrid = weekly_table[['Name', 'Position', 'Team_x','Current Price','Event Points','Form', 'Form_%_15','Threat_%_15','Crtvty_%_15','PP_GW','Next_GW_%_15','PPNext3','PP3_%_15','Prob. of Appearring']]
gridOptions = GridOptionsBuilder.from_dataframe(weekly_table_aggrid)
gridOptions.configure_column('Name', headerTooltip='Click hamburger to filter and select columns', pinned='left', 
                            sorteable=False, width = 100)
gridOptions.configure_column('Position', headerTooltip='Click hamburger to filter and select columns', width = 90, header_name='Pos')
gridOptions.configure_column('Team_x', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='Team')
gridOptions.configure_column('Current Price', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='$')
gridOptions.configure_column('Event Points', headerTooltip='Click hamburger to filter and select columns', width = 80, header_name='GW Pts')
gridOptions.configure_column('Form', headerTooltip='Click hamburger to filter and select columns', width = 70, header_name='Form')
gridOptions.configure_column('Form_%_15', headerTooltip='Click hamburger to filter and select columns', width = 120, header_name='Form Rank(%)')
gridOptions.configure_column('Threat_%_15', headerTooltip='Click hamburger to filter and select columns', width = 130, header_name='Threat Rank(%)')
gridOptions.configure_column('Crtvty_%_15', headerTooltip='Click hamburger to filter and select columns', width = 130, header_name='Crtvty Rank(%)')
gridOptions.configure_column('PP_GW', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next GW')
gridOptions.configure_column('Next_GW_%_15', headerTooltip='Click hamburger to filter and select columns', width = 150, header_name='PP Next GW Rank(%)')
gridOptions.configure_column('PPNext3', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 3 GW')
gridOptions.configure_column('PP3_%_15', headerTooltip='Click hamburger to filter and select columns', width = 160, header_name='PP Next 3 GW Rank(%)')
gridOptions.configure_column('Prob. of Appearring', headerTooltip='Click hamburger to filter and select columns', width = 160, header_name='Prob of Appearring(%)')

cellstylejscode = JsCode("""
        function(params){
            if (params.value < 35) {
                return{
                    'color': 'white',
                    'backgroundColor': '#900C3F'
            }
            }
            if (params.value > 85) {return{'color':'white', 'backgroundColor': '#73C6B6'}}
                            
}                             
""")


cellstylejscode2 = JsCode("""
        function(params){
            if (params.value < 0.85) {
                return{
                    'color': 'black',
                    'backgroundColor': '#DAF7A6'
            }

            }
}                             
""")

cellstylejscode3 = JsCode("""
        function(params){
            if (params.value > 4) {
                return{
                    'color': 'black',
                    'backgroundColor': '#73C6B6'
            }

            }
}                             
""")

cellstylejscode4 = JsCode("""
        function(params){
            if (params.value > 12) {
                return{
                    'color': 'black',
                    'backgroundColor': '#73C6B6'
            }

            }
}                             
""")

cellstylejscode5 = JsCode("""
        function(params){
            if (params.value === 2) {
                return{
                    'color': 'white',
                    'backgroundColor': '#73C6B6'
            }
            }
            if (params.value === 4) {return{'color':'white', 'backgroundColor': '#CD6155'}}
            if (params.value === 5) {return{'color':'white', 'backgroundColor': '#C0392B'}}
            if (params.value === 1) {return{'color':'white', 'backgroundColor': '#45B39D'}}
                            
}                             
""")

cellstylejscode6 = JsCode("""
        function(params){
            if (params.value < 10) {
                return{
                    'color': 'black',
                    'backgroundColor': '#73C6B6'
            }

            }
}                             
""")

cellstylejscode7 = JsCode("""
        function(params){
            if (params.value < 0.9) {
                return{
                    'color': 'black',
                    'backgroundColor': '#C0392B'
            }

            }
}                             
""")


gridOptions.configure_columns(['Form_%_15','Next_GW_%_15','PP3_%_15'],cellStyle =cellstylejscode)
gridOptions.configure_columns(['Prob. of Appearring'],cellStyle =cellstylejscode2)



gb = gridOptions.build()
                        
AgGrid(
    weekly_table_aggrid,theme='streamlit', gridOptions=gb, allow_unsafe_jscode=True,
)
# %%
#Player To Transfer
p =weekly_table_show.loc[(weekly_table['Current Price'] > 4.5) & (weekly_table['Prob. of Appearring'] <= 0.85)].sort_values(['PP3_%_15','Prob. of Appearring','Current Price'],ascending=[True,True,False])
index_select = p.iloc[0].name - 1
index_select = index_select.tolist()
index_select2 = weekly_table_show.iloc[0].name

st.subheader('Suggested Players To Transfer')

if len(p) == 0:
    st.text('You have no important players to transfer this week!')
else:
    st.text('These players have been shortlisted as they have low predicted points and/or probability of appearing')

#p_style = p[['Name', 'Position', 'Team_x','Current Price','Event Points','Form', 'Form_%_15','Threat_%_15','Crtvty_%_15','PP_GW','Next_GW_%_15','PPNext3','PP3_%_15','Prob. of Appearring']].style\
#                        .format(precision=2)\
#                        .background_gradient(cmap='RdYlGn',subset=pd.IndexSlice[:,['Form_%_15','PP_GW','Next_GW_%_15','PPNext3','PP3_%_15','Prob. of Appearring']])\

#st.dataframe(p_style)

AgGrid(
    p,theme='streamlit', gridOptions=gb, allow_unsafe_jscode=True,
)

#%%
st.header('Step 2A: Assess potential replacements by selected players')

#Ask for Player To Transfer
player_to_transfer_1 = st.selectbox(
    '1st Player to Transfer',
    list(weekly_table['Name']),
    index=index_select
)

player_to_transfer_1_df = weekly_table[weekly_table['Name'] == player_to_transfer_1]
player_to_transfer_1_df = player_to_transfer_1_df[['element','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring','xG per 90', 'xA per 90', 'xGA per 90', 'GW1_Diff', 'GW2_Diff', 'GW3_Diff', 'GW1_Home?', 'GW2_Home?', 'GW3_Home?']]

#%%

upper_range = player_to_transfer_1_df.iloc[0][4] + 0.5
lower_range = player_to_transfer_1_df.iloc[0][4] - 2
pos = player_to_transfer_1_df.iloc[0][2]

options = master_table.sort_values(['PPNext3','Prob. of Appearring'],ascending= [False,False])[(master_table['Current Price'].between(lower_range,upper_range)) & (master_table['Position'] == pos)].head(10)

options = options[['ID','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring','xG per 90', 'xA per 90', 'xGA per 90', 'GW1_Diff', 'GW2_Diff', 'GW3_Diff', 'GW1_Home?', 'GW2_Home?', 'GW3_Home?']]

options = options.rename(columns={'ID':'element'})

options = pd.concat([player_to_transfer_1_df,options]).reset_index(drop=True)

#%%
#xg_data_list = []
#xa_data_list = []
#xga_data_list = []
#xg_players = list(options['element'])
#dif1_list=[]
#home1_list = []
#dif2_list=[]
#home2_list = []
#dif3_list=[]
#home3_list = []
#
#for i in xg_players:
#    str = 'https://fantasy.premierleague.com/api/element-summary/{}/'
#    url = str.format(i)
#    with requests.get(url) as f:
#        d = f.json()
#    e = pd.json_normalize(d['history'])
#    e['expected_goals'] = pd.to_numeric(e['expected_goals'])
#    e['expected_assists'] = pd.to_numeric(e['expected_assists'])
#    e['expected_goals_conceded'] = pd.to_numeric(e['expected_goals_conceded'])
#    xg = e['expected_goals'].sum()/(e['minutes'].sum()/90)
#    xa = e['expected_assists'].sum()/(e['minutes'].sum()/90)
#    xga = e['expected_goals_conceded'].sum()/(e['minutes'].sum()/90)
#    f = pd.json_normalize(d['fixtures'])
#    dif1 = f.loc[0][13]
#    home1 = f.loc[0][12]
#    dif2 = f.loc[1][13]
#    home2 = f.loc[1][12]
#    dif3 = f.loc[2][13]
#    home3 = f.loc[2][12]
#    
#
#    xg_data_list.append(round(xg,2))
#    xa_data_list.append(round(xa,2))
#    xga_data_list.append(round(xga,2))
#    dif1_list.append(dif1)
#    home1_list.append(home1)
#    dif2_list.append(dif2)
#    home2_list.append(home2)
#    dif3_list.append(dif3)
#    home3_list.append(home3)
#
#options['xG per 90'] = xg_data_list
#options['xA per 90'] = xa_data_list
#options['xGA per 90'] = xga_data_list     
#options['GW1_Diff'] = dif1_list
#options['GW1_Home?'] = home1_list
#options['GW2_Diff'] = dif2_list
#options['GW2_Home?'] = home2_list
#options['GW3_Diff'] = dif3_list
#options['GW3_Home?'] = home3_list      


#options_style = options.style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring','xG per 90','xA per 90','xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff']])

#%%

st.text(f'Suggested Transfers For {player_to_transfer_1}, added in the first row for comparison.')
#table_view = st.radio(
#    "Select your view:",
#    ['All','Predicted Points + Fixture Difficulty Rating','ICT + Form + xG','xG Data','Fixture Difficulty Rating + Home/Away'],
#    index=1,
#    key=1
#)
#if table_view == 'All':
    #options_style = options.style\
    #                .format(precision=2)\
    #                .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring','xG per 90','xA per 90','xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff']])
    #st.dataframe(options_style)
options_to_show = options[['Name', 'Position', 'Team_x',
                    'Current Price','Merit','PP_GW', 'PPNext2', 'PPNext3','Selected By %','Prob. of Appearring','Form','Threat','xG per 90', 'Creativity', 'xA per 90', 'xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff','GW1_Home?','GW2_Home?','GW3_Home?']]    
gridOptions2 = GridOptionsBuilder.from_dataframe(options_to_show)
gridOptions2.configure_column('Name', headerTooltip='Click hamburger to filter and select columns', pinned='left', 
                            sorteable=False, width = 100)
gridOptions2.configure_column('Position', headerTooltip='Click hamburger to filter and select columns', width = 90, header_name='Pos')
#gridOptions2.configure_column('element', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='ID')
gridOptions2.configure_column('Team_x', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='Team')
gridOptions2.configure_column('Current Price', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='$')
#gridOptions2.configure_column('Event Points', headerTooltip='Click hamburger to filter and select columns', width = 80, header_name='GW Pts')
gridOptions2.configure_column('Form', headerTooltip='Click hamburger to filter and select columns', width = 70, header_name='Form')
#gridOptions2.configure_column('Influence', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions2.configure_column('Creativity', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions2.configure_column('Merit', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions2.configure_column('Threat', headerTooltip='Click hamburger to filter and select columns', width = 80)
gridOptions2.configure_column('PP_GW', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next GW')
gridOptions2.configure_column('PPNext2', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 2 GW')
gridOptions2.configure_column('PPNext3', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 3 GW',pinned='left')
gridOptions2.configure_column('Selected By %', headerTooltip='Click hamburger to filter and select columns', width = 120, header_name='Selected By %')
gridOptions2.configure_column('Prob. of Appearring', headerTooltip='Click hamburger to filter and select columns', width = 160, header_name='Prob of Appearring(%)')
gridOptions2.configure_column('xG per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions2.configure_column('xA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions2.configure_column('xGA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions2.configure_column('GW1_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions2.configure_column('GW1_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions2.configure_column('GW2_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions2.configure_column('GW2_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions2.configure_column('GW3_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions2.configure_column('GW3_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions2.configure_columns(['PP_GW'],cellStyle =cellstylejscode3)
gridOptions2.configure_columns(['PPNext3'],cellStyle =cellstylejscode4)
gridOptions2.configure_columns(['GW1_Diff','GW2_Diff','GW3_Diff'],cellStyle =cellstylejscode5)
gridOptions2.configure_columns(['Selected By %'],cellStyle =cellstylejscode6)
gridOptions2.configure_columns(['Prob. of Appearring'],cellStyle =cellstylejscode7)
gb2 = gridOptions2.build()
                    
AgGrid(
    options_to_show,theme='streamlit', gridOptions=gb2, allow_unsafe_jscode=True,
)

#elif table_view == 'ICT + Form + xG':
#    #options_style = options[['Name','Team_x','Current Price','Form','Threat','xG per 90','Creativity','xA per 90','xGA per 90']].style\
#    #                .format(precision=2)\
#    #                .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Creativity','Threat','xG per 90','xA per 90']])\
#    #                .background_gradient(cmap='Reds', subset=pd.IndexSlice[:,['xGA per 90']])
#    #st.dataframe(options_style)
#    options_b = options[['Name','Team_x','Current Price','Form','Threat','xG per 90','Creativity','xA per 90','xGA per 90']]
#    gridOptions2b = GridOptionsBuilder.from_dataframe(options_b)
#    gridOptions2b.configure_column('Name', headerTooltip='Click hamburger to filter and select columns', pinned='left', 
#                                sorteable=False, width = 100)
#    #gridOptions2b.configure_column('Position', headerTooltip='Click hamburger to filter and select columns', width = 90, header_name='Pos')
#    #gridOptions2b.configure_column('element', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='ID')
#    gridOptions2b.configure_column('Team_x', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='Team')
#    gridOptions2b.configure_column('Current Price', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='$')
#    #gridOptions2b.configure_column('Event Points', headerTooltip='Click hamburger to filter and select columns', width = 80, header_name='GW Pts')
#    gridOptions2b.configure_column('Form', headerTooltip='Click hamburger to filter and select columns', width = 70, header_name='Form')
#    #gridOptions2b.configure_column('Influence', headerTooltip='Click hamburger to filter and select columns', width = 100)
#    gridOptions2b.configure_column('Creativity', headerTooltip='Click hamburger to filter and select columns', width = 100)
#    #gridOptions2b.configure_column('Merit', headerTooltip='Click hamburger to filter and select columns', width = 100)
#    gridOptions2b.configure_column('Threat', headerTooltip='Click hamburger to filter and select columns', width = 80)
#    #gridOptions2b.configure_column('PP_GW', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next GW')
#    #gridOptions2b.configure_column('PPNext2', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 2 GW')
#    #gridOptions2b.configure_column('PPNext3', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 3 GW')
#    #gridOptions2b.configure_column('Selected By %', headerTooltip='Click hamburger to filter and select columns', width = 160, header_name='Selected By %')
#    #gridOptions2b.configure_column('Prob. of Appearring', headerTooltip='Click hamburger to filter and select columns', width = 160, header_name='Prob of Appearring(%)')
#    gridOptions2b.configure_column('xG per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
#    gridOptions2b.configure_column('xA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
#    gridOptions2b.configure_column('xGA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
#    #gridOptions2b.configure_column('GW1_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
#    #gridOptions2b.configure_column('GW1_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
#    #gridOptions2b.configure_column('GW2_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
#    #gridOptions2b.configure_column('GW2_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
#    #gridOptions2b.configure_column('GW3_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
#    #gridOptions2b.configure_column('GW3_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
#
#    #gridOptions2b.configure_columns(['PP_GW'],cellStyle =cellstylejscode3)
#    #gridOptions2b.configure_columns(['PPNext3'],cellStyle =cellstylejscode4)
#    #gridOptions2b.configure_columns(['GW1_Diff','GW2_Diff','GW3_Diff'],cellStyle =cellstylejscode5)
#
#    gb2b = gridOptions2b.build()
#    AgGrid(
#        options_b,theme='streamlit', gridOptions=gb2b, allow_unsafe_jscode=True,
#    )    
#
#elif table_view == 'Predicted Points + Fixture Difficulty Rating':
#    options_style = options[['Name','Team_x','Current Price','Merit','PP_GW','PPNext2','PPNext3','Selected By %','Prob. of Appearring','GW1_Diff','GW2_Diff','GW3_Diff']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['PP_GW','PPNext2','PPNext3','Selected By %','Prob. of Appearring']])\
#                    .background_gradient(cmap='Reds', subset=pd.IndexSlice[:,['GW1_Diff','GW2_Diff','GW3_Diff']])
#    st.dataframe(options_style)
#elif table_view == 'xG Data':
#    options_style = options[['Name','Team_x','Current Price','xG per 90','xA per 90','xGA per 90']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['xG per 90','xA per 90','xGA per 90']])
#    st.dataframe(options_style)
#elif table_view == 'Fixture Difficulty Rating + Home/Away':
#    options_style = options[['Name','Team_x','Current Price','PP_GW','GW1_Diff','GW1_Home?','GW2_Diff','GW2_Home?','GW3_Diff','GW3_Home?','PPNext3']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['PP_GW','GW1_Diff','GW2_Diff','GW3_Diff','PPNext3']])
#    st.dataframe(options_style)
#

#if table_view == 'All':
#    st.dataframe(options_style)
#elif table_view == 'ICT + Form':
#    st.dataframe(options_style[['Price','Form','Influence','Creativity','Threat']])
#elif table_view == 'Predicted Points':
#    st.dataframe(options_style[['Price','Merit','PP_GW','PPNext2','PPNext3','Selected By %','Prob. Of Appearring']])
#elif table_view == 'xG Data':
#    st.dataframe(options_style[['Price','xG per 90','xA per 90','xGA per 90']])
#elif table_view == 'Fixture Difficulty Rating':
#    st.dataframe(options_style[['Price','PP_GW','GW1_Diff','GW1_Home?','GW2_Diff','GW2_Home?','GW3_Diff','GW3_Home?','PPNext3']])
# %%
player_to_transfer_2 = st.selectbox(
    '2nd Player to Transfer',
    list(weekly_table['Name']),
    index=index_select2
)

player_to_transfer_2_df = weekly_table[weekly_table['Name'] == player_to_transfer_2]
player_to_transfer_2_df = player_to_transfer_2_df[['element','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring','xG per 90', 'xA per 90', 'xGA per 90', 'GW1_Diff', 'GW2_Diff', 'GW3_Diff', 'GW1_Home?', 'GW2_Home?', 'GW3_Home?']]

upper_range2 = player_to_transfer_2_df.iloc[0][4] + 0.5
lower_range2 = player_to_transfer_2_df.iloc[0][4] - 2
pos2 = player_to_transfer_2_df.iloc[0][2]

options2 = master_table.sort_values(['PPNext3','Prob. of Appearring'],ascending= [False,False])[(master_table['Current Price'].between(lower_range2,upper_range2)) & (master_table['Position'] == pos2)].head(10)

options2 = options2[['ID','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring','xG per 90', 'xA per 90', 'xGA per 90', 'GW1_Diff', 'GW2_Diff', 'GW3_Diff', 'GW1_Home?', 'GW2_Home?', 'GW3_Home?']]

options2 = options2.rename(columns={'ID':'element'})

options2 = pd.concat([player_to_transfer_2_df,options2]).reset_index(drop=True)

#xg_data_list2 = []
#xa_data_list2 = []
#xga_data_list2 = []
#xg_players2 = list(options2['element'])
#dif1_list2=[]
#home1_list2 = []
#dif2_list2=[]
#home2_list2 = []
#dif3_list2=[]
#home3_list2 = []
#
#
#for i in xg_players2:
#    str = 'https://fantasy.premierleague.com/api/element-summary/{}/'
#    url = str.format(i)
#    with requests.get(url) as f:
#        d = f.json()
#    e = pd.json_normalize(d['history'])
#    e['expected_goals'] = pd.to_numeric(e['expected_goals'])
#    e['expected_assists'] = pd.to_numeric(e['expected_assists'])
#    e['expected_goals_conceded'] = pd.to_numeric(e['expected_goals_conceded'])
#    xg = e['expected_goals'].sum()/(e['minutes'].sum()/90)
#    xa = e['expected_assists'].sum()/(e['minutes'].sum()/90)
#    xga = e['expected_goals_conceded'].sum()/(e['minutes'].sum()/90)
#    f = pd.json_normalize(d['fixtures'])
#    dif1 = f.loc[0][13]
#    home1 = f.loc[0][12]
#    dif2 = f.loc[1][13]
#    home2 = f.loc[1][12]
#    dif3 = f.loc[2][13]
#    home3 = f.loc[2][12]
#
#    xg_data_list2.append(xg)
#    xa_data_list2.append(xa)
#    xga_data_list2.append(xga)
#    dif1_list2.append(dif1)
#    home1_list2.append(home1)
#    dif2_list2.append(dif2)
#    home2_list2.append(home2)
#    dif3_list2.append(dif3)
#    home3_list2.append(home3)
#
#options2['xG per 90'] = xg_data_list2
#options2['xA per 90'] = xa_data_list2
#options2['xGA per 90'] = xga_data_list2
#options2['GW1_Diff'] = dif1_list2
#options2['GW1_Home?'] = home1_list2
#options2['GW2_Diff'] = dif2_list2
#options2['GW2_Home?'] = home2_list2
#options2['GW3_Diff'] = dif3_list2
#options2['GW3_Home?'] = home3_list2         

#options2_style = options2.style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring']])

st.text(f'Suggested Transfers For {player_to_transfer_2}, added in the first row for comparison.')

options_to_show2 = options2[['Name', 'Position', 'Team_x',
                    'Current Price','Merit','PP_GW', 'PPNext2', 'PPNext3','Selected By %','Prob. of Appearring','Form','Threat','xG per 90', 'Creativity', 'xA per 90', 'xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff','GW1_Home?','GW2_Home?','GW3_Home?']]    
gridOptions3 = GridOptionsBuilder.from_dataframe(options_to_show2)
gridOptions3.configure_column('Name', headerTooltip='Click hamburger to filter and select columns', pinned='left', 
                            sorteable=False, width = 100)
gridOptions3.configure_column('Position', headerTooltip='Click hamburger to filter and select columns', width = 90, header_name='Pos')
#gridOptions3.configure_column('element', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='ID')
gridOptions3.configure_column('Team_x', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='Team')
gridOptions3.configure_column('Current Price', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='$')
#gridOptions3.configure_column('Event Points', headerTooltip='Click hamburger to filter and select columns', width = 80, header_name='GW Pts')
gridOptions3.configure_column('Form', headerTooltip='Click hamburger to filter and select columns', width = 70, header_name='Form')
#gridOptions3.configure_column('Influence', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions3.configure_column('Creativity', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions3.configure_column('Merit', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions3.configure_column('Threat', headerTooltip='Click hamburger to filter and select columns', width = 80)
gridOptions3.configure_column('PP_GW', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next GW')
gridOptions3.configure_column('PPNext2', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 2 GW')
gridOptions3.configure_column('PPNext3', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 3 GW',pinned='left')
gridOptions3.configure_column('Selected By %', headerTooltip='Click hamburger to filter and select columns', width = 120, header_name='Selected By %')
gridOptions3.configure_column('Prob. of Appearring', headerTooltip='Click hamburger to filter and select columns', width = 160, header_name='Prob of Appearring(%)')
gridOptions3.configure_column('xG per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions3.configure_column('xA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions3.configure_column('xGA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions3.configure_column('GW1_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions3.configure_column('GW1_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions3.configure_column('GW2_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions3.configure_column('GW2_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions3.configure_column('GW3_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions3.configure_column('GW3_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions3.configure_columns(['PP_GW'],cellStyle =cellstylejscode3)
gridOptions3.configure_columns(['PPNext3'],cellStyle =cellstylejscode4)
gridOptions3.configure_columns(['GW1_Diff','GW2_Diff','GW3_Diff'],cellStyle =cellstylejscode5)
gridOptions3.configure_columns(['Selected By %'],cellStyle =cellstylejscode6)
gridOptions3.configure_columns(['Prob. of Appearring'],cellStyle =cellstylejscode7)
gb3 = gridOptions3.build()
                    
AgGrid(
    options_to_show2,theme='streamlit', gridOptions=gb3, allow_unsafe_jscode=True,
)

#table_view2 = st.radio(
#    "Select your view:",
#    ['All','Predicted Points + Fixture Difficulty Rating','ICT + Form + xG','xG Data','Fixture Difficulty Rating + Home/Away'],
#    index=1,
#    key=2
#)
#if table_view2 == 'All':
#    options2_style = options2.style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring','xG per 90','xA per 90','xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff']])
#    st.dataframe(options2_style)
#elif table_view2 == 'ICT + Form + xG':
#    options2_style = options2[['Name','Team_x','Current Price','Form','Threat','xG per 90','Creativity','xA per 90','xGA per 90']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Creativity','Threat','xG per 90','xA per 90']])\
#                    .background_gradient(cmap='Reds', subset=pd.IndexSlice[:,['xGA per 90']])
#    st.dataframe(options2_style)
#elif table_view2 == 'Predicted Points + Fixture Difficulty Rating':
#    options2_style = options2[['Name','Team_x','Current Price','Merit','PP_GW','PPNext2','PPNext3','Selected By %','Prob. of Appearring','GW1_Diff','GW2_Diff','GW3_Diff']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['PP_GW','PPNext2','PPNext3','Selected By %','Prob. of Appearring']])\
#                    .background_gradient(cmap='Reds', subset=pd.IndexSlice[:,['GW1_Diff','GW2_Diff','GW3_Diff']])
#    st.dataframe(options2_style)
#elif table_view2 == 'xG Data':
#    options2_style = options2[['Name','Team_x','Current Price','xG per 90','xA per 90','xGA per 90']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['xG per 90','xA per 90','xGA per 90']])
#    st.dataframe(options2_style)
#elif table_view2 == 'Fixture Difficulty Rating + Home/Away':
#    options2_style = options2[['Name','Team_x','Current Price','PP_GW','GW1_Diff','GW1_Home?','GW2_Diff','GW2_Home?','GW3_Diff','GW3_Home?','PPNext3']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['PP_GW','GW1_Diff','GW2_Diff','GW3_Diff','PPNext3']])
#    st.dataframe(options2_style)


#Give the option to customize price options
st.header('Step 2B: Alternatively, assess potential replacements by price!')
st.text('This function will work well for double transfers')

total_selected_price = player_to_transfer_1_df.iloc[0][4] + player_to_transfer_2_df.iloc[0][4] + (metrics_data.loc[0][6]/10)
st.text(f'Total Price For Selected Players + Remaining In Bank: {total_selected_price}')
price_1_value = player_to_transfer_1_df.iloc[0][4]

price_1 = st.number_input(
    'Price For Player 1:',
    value = price_1_value,
    step=0.2
)

remaining_price = total_selected_price - price_1

st.text(f"Including What's Left In Your Bank, You Can Afford {round(remaining_price,1)} For The 2nd Player")

st.text('Suggested Replacements For Player 1')

price_1_pos = st.selectbox(
    'Filter Player 1 Suggestions by Position?',
    ['Goalkeeper','Defender','Midfielder','Forward'],
    index=1
)

upper_range_price_1 = price_1
lower_range_price_1 = price_1 - 2

options_price_1 = master_table.sort_values(['PPNext3','Prob. of Appearring'],ascending= [False,False])[(master_table['Current Price'].between(lower_range_price_1,upper_range_price_1)) & (master_table['Position'] == price_1_pos)].head(10)

options_price_1 = options_price_1[['ID','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring','xG per 90', 'xA per 90', 'xGA per 90', 'GW1_Diff', 'GW2_Diff', 'GW3_Diff', 'GW1_Home?', 'GW2_Home?', 'GW3_Home?']]

options_price_1 = options_price_1.rename(columns={'ID':'element'})

options_to_show3 = options_price_1[['Name', 'Position', 'Team_x',
                    'Current Price','Merit','PP_GW', 'PPNext2', 'PPNext3','Selected By %','Prob. of Appearring','Form','Threat','xG per 90', 'Creativity', 'xA per 90', 'xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff','GW1_Home?','GW2_Home?','GW3_Home?']]    
gridOptions4 = GridOptionsBuilder.from_dataframe(options_to_show3)
gridOptions4.configure_column('Name', headerTooltip='Click hamburger to filter and select columns', pinned='left', 
                            sorteable=False, width = 100)
gridOptions4.configure_column('Position', headerTooltip='Click hamburger to filter and select columns', width = 90, header_name='Pos')
#gridOptions4.configure_column('element', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='ID')
gridOptions4.configure_column('Team_x', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='Team')
gridOptions4.configure_column('Current Price', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='$')
#gridOptions4.configure_column('Event Points', headerTooltip='Click hamburger to filter and select columns', width = 80, header_name='GW Pts')
gridOptions4.configure_column('Form', headerTooltip='Click hamburger to filter and select columns', width = 70, header_name='Form')
#gridOptions4.configure_column('Influence', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions4.configure_column('Creativity', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions4.configure_column('Merit', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions4.configure_column('Threat', headerTooltip='Click hamburger to filter and select columns', width = 80)
gridOptions4.configure_column('PP_GW', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next GW')
gridOptions4.configure_column('PPNext2', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 2 GW')
gridOptions4.configure_column('PPNext3', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 3 GW',pinned='left')
gridOptions4.configure_column('Selected By %', headerTooltip='Click hamburger to filter and select columns', width = 120, header_name='Selected By %')
gridOptions4.configure_column('Prob. of Appearring', headerTooltip='Click hamburger to filter and select columns', width = 160, header_name='Prob of Appearring(%)')
gridOptions4.configure_column('xG per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions4.configure_column('xA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions4.configure_column('xGA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions4.configure_column('GW1_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions4.configure_column('GW1_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions4.configure_column('GW2_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions4.configure_column('GW2_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions4.configure_column('GW3_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions4.configure_column('GW3_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions4.configure_columns(['PP_GW'],cellStyle =cellstylejscode3)
gridOptions4.configure_columns(['PPNext3'],cellStyle =cellstylejscode4)
gridOptions4.configure_columns(['GW1_Diff','GW2_Diff','GW3_Diff'],cellStyle =cellstylejscode5)
gridOptions4.configure_columns(['Selected By %'],cellStyle =cellstylejscode6)
gridOptions4.configure_columns(['Prob. of Appearring'],cellStyle =cellstylejscode7)
gb4 = gridOptions4.build()
                    
AgGrid(
    options_to_show3,theme='streamlit', gridOptions=gb4, allow_unsafe_jscode=True,
)

#xg_data_list3 = []
#xa_data_list3 = []
#xga_data_list3 = []
#xg_players3 = list(options_price_1['element'])
#dif1_list3=[]
#home1_list3 = []
#dif2_list3=[]
#home2_list3 = []
#dif3_list3=[]
#home3_list3 = []
#
#
#for i in xg_players3:
#    str = 'https://fantasy.premierleague.com/api/element-summary/{}/'
#    url = str.format(i)
#    with requests.get(url) as f:
#        d = f.json()
#    e = pd.json_normalize(d['history'])
#    e['expected_goals'] = pd.to_numeric(e['expected_goals'])
#    e['expected_assists'] = pd.to_numeric(e['expected_assists'])
#    e['expected_goals_conceded'] = pd.to_numeric(e['expected_goals_conceded'])
#    xg = e['expected_goals'].sum()/(e['minutes'].sum()/90)
#    xa = e['expected_assists'].sum()/(e['minutes'].sum()/90)
#    xga = e['expected_goals_conceded'].sum()/(e['minutes'].sum()/90)
#    f = pd.json_normalize(d['fixtures'])
#    dif1 = f.loc[0][13]
#    home1 = f.loc[0][12]
#    dif2 = f.loc[1][13]
#    home2 = f.loc[1][12]
#    dif3 = f.loc[2][13]
#    home3 = f.loc[2][12]
#
#    xg_data_list3.append(xg)
#    xa_data_list3.append(xa)
#    xga_data_list3.append(xga)
#    dif1_list3.append(dif1)
#    home1_list3.append(home1)
#    dif2_list3.append(dif2)
#    home2_list3.append(home2)
#    dif3_list3.append(dif3)
#    home3_list3.append(home3)
#
#options_price_1['xG per 90'] = xg_data_list3
#options_price_1['xA per 90'] = xa_data_list3
#options_price_1['xGA per 90'] = xga_data_list3
#options_price_1['GW1_Diff'] = dif1_list3
#options_price_1['GW1_Home?'] = home1_list3
#options_price_1['GW2_Diff'] = dif2_list3
#options_price_1['GW2_Home?'] = home2_list3
#options_price_1['GW3_Diff'] = dif3_list3
#options_price_1['GW3_Home?'] = home3_list3
#
#table_view3 = st.radio(
#    "Select your view:",
#    ['All','Predicted Points + Fixture Difficulty Rating','ICT + Form + xG','xG Data','Fixture Difficulty Rating + Home/Away'],
#    index=1,
#    key=3
#)
#if table_view3 == 'All':
#    options_price_1_style = options_price_1.style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring','xG per 90','xA per 90','xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff']])
#    st.dataframe(options_price_1_style)
#elif table_view3 == 'ICT + Form + xG':
#    options_price_1_style = options_price_1[['Name','Team_x','Current Price','Form','Threat','xG per 90','Creativity','xA per 90','xGA per 90']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Creativity','Threat','xG per 90','xA per 90']])\
#                    .background_gradient(cmap='Reds', subset=pd.IndexSlice[:,['xGA per 90']])
#    st.dataframe(options_price_1_style)
#elif table_view3 == 'Predicted Points + Fixture Difficulty Rating':
#    options_price_1_style = options_price_1[['Name','Team_x','Current Price','Merit','PP_GW','PPNext2','PPNext3','Selected By %','Prob. of Appearring','GW1_Diff','GW2_Diff','GW3_Diff']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['PP_GW','PPNext2','PPNext3','Selected By %','Prob. of Appearring']])\
#                    .background_gradient(cmap='Reds', subset=pd.IndexSlice[:,['GW1_Diff','GW2_Diff','GW3_Diff']])
#    st.dataframe(options_price_1_style)
#elif table_view3 == 'xG Data':
#    options_price_1_style = options_price_1[['Name','Team_x','Current Price','xG per 90','xA per 90','xGA per 90']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['xG per 90','xA per 90','xGA per 90']])
#    st.dataframe(options_price_1_style)
#elif table_view3 == 'Fixture Difficulty Rating + Home/Away':
#    options_price_1_style = options_price_1[['Name','Team_x','Current Price','PP_GW','GW1_Diff','GW1_Home?','GW2_Diff','GW2_Home?','GW3_Diff','GW3_Home?','PPNext3']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['PP_GW','GW1_Diff','GW2_Diff','GW3_Diff','PPNext3']])
#    st.dataframe(options_price_1_style)


#options_price_1_style = options_price_1.style\
#                   .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring']])


#st.dataframe(options_price_1_style)

st.text('Suggested Replacements for Player 2')

price_2_pos = st.selectbox(
    'Filter Player 2 Suggestions by Position?',
    ['Goalkeeper','Defender','Midfielder','Forward'],
    index=1
)

upper_range_price_2 = remaining_price
lower_range_price_2 = remaining_price - 2

options_price_2 = master_table.sort_values(['PPNext3','Prob. of Appearring'],ascending= [False,False])[(master_table['Current Price'].between(lower_range_price_2,upper_range_price_2)) & (master_table['Position'] == price_2_pos)].head(10)

options_price_2 = options_price_2[['ID','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring','xG per 90', 'xA per 90', 'xGA per 90', 'GW1_Diff', 'GW2_Diff', 'GW3_Diff', 'GW1_Home?', 'GW2_Home?', 'GW3_Home?']]

options_price_2 = options_price_2.rename(columns={'ID':'element'})

options_to_show4 = options_price_2[['Name', 'Position', 'Team_x',
                    'Current Price','Merit','PP_GW', 'PPNext2', 'PPNext3','Selected By %','Prob. of Appearring','Form','Threat','xG per 90', 'Creativity', 'xA per 90', 'xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff','GW1_Home?','GW2_Home?','GW3_Home?']]    
gridOptions5 = GridOptionsBuilder.from_dataframe(options_to_show4)
gridOptions5.configure_column('Name', headerTooltip='Click hamburger to filter and select columns', pinned='left', 
                            sorteable=False, width = 100)
gridOptions5.configure_column('Position', headerTooltip='Click hamburger to filter and select columns', width = 90, header_name='Pos')
#gridOptions5.configure_column('element', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='ID')
gridOptions5.configure_column('Team_x', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='Team')
gridOptions5.configure_column('Current Price', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='$')
#gridOptions5.configure_column('Event Points', headerTooltip='Click hamburger to filter and select columns', width = 80, header_name='GW Pts')
gridOptions5.configure_column('Form', headerTooltip='Click hamburger to filter and select columns', width = 70, header_name='Form')
#gridOptions5.configure_column('Influence', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions5.configure_column('Creativity', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions5.configure_column('Merit', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions5.configure_column('Threat', headerTooltip='Click hamburger to filter and select columns', width = 80)
gridOptions5.configure_column('PP_GW', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next GW')
gridOptions5.configure_column('PPNext2', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 2 GW')
gridOptions5.configure_column('PPNext3', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 3 GW',pinned='left')
gridOptions5.configure_column('Selected By %', headerTooltip='Click hamburger to filter and select columns', width = 120, header_name='Selected By %')
gridOptions5.configure_column('Prob. of Appearring', headerTooltip='Click hamburger to filter and select columns', width = 160, header_name='Prob of Appearring(%)')
gridOptions5.configure_column('xG per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions5.configure_column('xA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions5.configure_column('xGA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions5.configure_column('GW1_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions5.configure_column('GW1_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions5.configure_column('GW2_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions5.configure_column('GW2_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions5.configure_column('GW3_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
gridOptions5.configure_column('GW3_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
gridOptions5.configure_columns(['PP_GW'],cellStyle =cellstylejscode3)
gridOptions5.configure_columns(['PPNext3'],cellStyle =cellstylejscode4)
gridOptions5.configure_columns(['GW1_Diff','GW2_Diff','GW3_Diff'],cellStyle =cellstylejscode5)
gridOptions5.configure_columns(['Selected By %'],cellStyle =cellstylejscode6)
gridOptions5.configure_columns(['Prob. of Appearring'],cellStyle =cellstylejscode7)
gb5 = gridOptions5.build()
                    
AgGrid(
    options_to_show4,theme='streamlit', gridOptions=gb5, allow_unsafe_jscode=True,
)

#xg_data_list4 = []
#xa_data_list4 = []
#xga_data_list4 = []
#xg_players4 = list(options_price_2['element'])
#dif1_list4=[]
#home1_list4 = []
#dif2_list4=[]
#home2_list4 = []
#dif3_list4=[]
#home3_list4 = []
#
#
#for i in xg_players4:
#    str = 'https://fantasy.premierleague.com/api/element-summary/{}/'
#    url = str.format(i)
#    with requests.get(url) as f:
#        d = f.json()
#    e = pd.json_normalize(d['history'])
#    e['expected_goals'] = pd.to_numeric(e['expected_goals'])
#    e['expected_assists'] = pd.to_numeric(e['expected_assists'])
#    e['expected_goals_conceded'] = pd.to_numeric(e['expected_goals_conceded'])
#    xg = e['expected_goals'].sum()/(e['minutes'].sum()/90)
#    xa = e['expected_assists'].sum()/(e['minutes'].sum()/90)
#    xga = e['expected_goals_conceded'].sum()/(e['minutes'].sum()/90)
#    f = pd.json_normalize(d['fixtures'])
#    dif1 = f.loc[0][13]
#    home1 = f.loc[0][12]
#    dif2 = f.loc[1][13]
#    home2 = f.loc[1][12]
#    dif3 = f.loc[2][13]
#    home3 = f.loc[2][12]
#
#    xg_data_list4.append(xg)
#    xa_data_list4.append(xa)
#    xga_data_list4.append(xga)
#    dif1_list4.append(dif1)
#    home1_list4.append(home1)
#    dif2_list4.append(dif2)
#    home2_list4.append(home2)
#    dif3_list4.append(dif3)
#    home3_list4.append(home3)
#
#options_price_2['xG per 90'] = xg_data_list4
#options_price_2['xA per 90'] = xa_data_list4
#options_price_2['xGA per 90'] = xga_data_list4
#options_price_2['GW1_Diff'] = dif1_list4
#options_price_2['GW1_Home?'] = home1_list4
#options_price_2['GW2_Diff'] = dif2_list4
#options_price_2['GW2_Home?'] = home2_list4
#options_price_2['GW3_Diff'] = dif3_list4
#options_price_2['GW3_Home?'] = home3_list4
#
#table_view4 = st.radio(
#    "Select your view:",
#    ['All','Predicted Points + Fixture Difficulty Rating','ICT + Form + xG','xG Data','Fixture Difficulty Rating + Home/Away'],
#    index=1,
#    key=4
#)
#if table_view4 == 'All':
#    options_price_2_style = options_price_2.style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring','xG per 90','xA per 90','xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff']])
#    st.dataframe(options_price_2_style)
#elif table_view4 == 'ICT + Form + xG':
#    options_price_2_style = options_price_2[['Name','Team_x','Current Price','Form','Threat','xG per 90','Creativity','xA per 90','xGA per 90']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Creativity','Threat','xG per 90','xA per 90']])\
#                    .background_gradient(cmap='Reds', subset=pd.IndexSlice[:,['xGA per 90']])
#    st.dataframe(options_price_2_style)
#elif table_view4 == 'Predicted Points + Fixture Difficulty Rating':
#    options_price_2_style = options_price_2[['Name','Team_x','Current Price','Merit','PP_GW','PPNext2','PPNext3','Selected By %','Prob. of Appearring','GW1_Diff','GW2_Diff','GW3_Diff']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['PP_GW','PPNext2','PPNext3','Selected By %','Prob. of Appearring']])\
#                    .background_gradient(cmap='Reds', subset=pd.IndexSlice[:,['GW1_Diff','GW2_Diff','GW3_Diff']])
#    st.dataframe(options_price_2_style)
#elif table_view4 == 'xG Data':
#    options_price_2_style = options_price_2[['Name','Team_x','Current Price','xG per 90','xA per 90','xGA per 90']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['xG per 90','xA per 90','xGA per 90']])
#    st.dataframe(options_price_2_style)
#elif table_view4 == 'Fixture Difficulty Rating + Home/Away':
#    options_price_2_style = options_price_2[['Name','Team_x','Current Price','PP_GW','GW1_Diff','GW1_Home?','GW2_Diff','GW2_Home?','GW3_Diff','GW3_Home?','PPNext3']].style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['PP_GW','GW1_Diff','GW2_Diff','GW3_Diff','PPNext3']])
#    st.dataframe(options_price_2_style)



#options_price_2_style = options_price_2.style\
#                    .format(precision=2)\
#                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring']])


#st.dataframe(options_price_2_style)

#%%
selected_player_1 = st.selectbox(
    'Chosen Player 1',
    list(options_price_1['Name']),
    index=0
)

selected_player_2 = st.selectbox(
    'Chosen Player 2',
    list(options_price_2['Name']),
    index=0
)

max_potential_pp3 = options_price_1[options_price_1['Name'] == selected_player_1].iloc[0][12] + options_price_2[options_price_2['Name'] == selected_player_2].iloc[0][12]
old_potential_pp3 = player_to_transfer_1_df.iloc[0][12] + player_to_transfer_2_df.iloc[0][12]
delta_potential_pp3 = max_potential_pp3 - old_potential_pp3

st.text(f'Your transfers have the potential to give you an additional {round(delta_potential_pp3,1)} points over the next 3 gameweeks')


st.header('Step 3: Keep Updated On Macro Trends in FPL!')
st.text('Breakdown of potential points over the next 3 GW by position')
st.text('Crop to zoom in. Hover for name and price. Double click to reset graph')
fig1 = px.violin(master_table[master_table['PPNext3'] > 10], y='PPNext3',hover_data=['Name','Current Price'],points='all',box=True,color='Position')
with st.expander('⬇️ Potential Points By Position'):
    st.plotly_chart(fig1, use_container_width=True)

st.text('Breakdown of potential points over the next 3 GW by team')
st.text('Crop to zoom in. Hover for name and price. Double click to reset graph')
fig2 = px.violin(master_table[master_table['PPNext3'] > 10], y='PPNext3',hover_data=['Name','Current Price'],points='all',box=True,color='Team_x')
with st.expander('⬇️ Potential Points By Team'):
    st.plotly_chart(fig2, use_container_width=True)

#st.text('xG per game by Position')
#st.text('Crop to zoom in. Hover for name and price. Double click to reset graph')
#fig2 = px.violin(master_table[master_table['xG per 90'] > 0.2], y='xG per 90',hover_data=['Name','Current Price'],points='all',box=True,color='Position')
#with st.expander('⬇️ Potential xG per 90 by Position'):
#    st.plotly_chart(fig2, use_container_width=True)
#
#st.text('xA per game by Position')
#st.text('Crop to zoom in. Hover for name and price. Double click to reset graph')
#fig2 = px.violin(master_table[master_table['xA per 90'] > 0.2], y='xA per 90',hover_data=['Name','Current Price'],points='all',box=True,color='Position')
#with st.expander('⬇️ Potential xA per 90 by Position'):
#    st.plotly_chart(fig2, use_container_width=True)
# %%
