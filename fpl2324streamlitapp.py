#%%
import pandas as pd
from scipy import stats
import requests
import plotly_express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np

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

#%%
#Ask for Gameweek
gameweek = st.number_input(
    'Input Gameweek',
    min_value=1,
    max_value=38,
    value=4
)

gameweek_m_1 = gameweek - 1

#%%
@st.cache_data
def master_table():
    #Get Master Table
    url = 'https://drive.google.com/file/d/1f-q5duVoamPtC9kZxvyXLPANdcYYzBKE/view?usp=sharing'
    url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
    df = pd.read_csv(url)
    df = df.drop('Unnamed: 0',axis=1)
    return df


@st.cache_data
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

@st.cache_data
def average_score():
    url3 = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    with requests.get(url3) as f:
        d = f.json()
    d = pd.json_normalize(d['events'])
    return d

@st.cache_data
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

@st.cache_data
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
weekly_table = weekly_table.drop([0])[['multiplier','element',
'Name', 'Position', 'Team_x', 'Current Price',
'PointsPerGame', 'EventPoints','Form', 'ICTIndex','PenaltiesOrder', 
'Corners/IndirectOrder', 'Minutes', 'Influence', 'Creativity', 'Threat', 'Merit',
'Form over/under-performance over the last 4 GW', 'Prob. of Appearring',
'PP_GW', 'PPNext2', 'ValNext2', 'PPNext3',
'ValNext3', 'Selected By %']]

average_points = []
percentile = []
pp_1_percentile = []
pp_percentile = []
threat_perc = []
creativity_perc = []        

#column_mod = f'PPGW{gameweek+1}'
#print(column_mod)

list1 = list(weekly_table['Current Price'])
list2 = list(weekly_table['Position'])
list3 = list(weekly_table['Form'])
list4 = list(weekly_table['PPNext3'])
list5 = list(weekly_table['Threat'])
list6 = list(weekly_table['Creativity'])
list7 = list(weekly_table['PP_GW'])

for i,x,y,a,b,c,d in zip(list1,list2,list3,list4,list5,list6,list7):
    lower_range = i-0.5
    upper_range = i+0.5
    pos = x
    filtered_players = master_table.sort_values(by=['Form'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range, inclusive=True)) & (master_table['Position'] == pos)].head(10)
    filtered_players2 = master_table.sort_values(by=['Form'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range, inclusive=True)) &(master_table['Position'] == pos)].head(15)

    #avg_points = filtered_players['Form'].mean()
    #avg_points = round(avg_points,1)

    #Form Percentile Using Filtered Players 2
    pt = stats.percentileofscore(filtered_players2['Form'], y, kind='rank')
    pt = round(pt,0)

    #PPNext Percenitle
    pp_pt_1_filtered = master_table.sort_values(by=['PP_GW'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range, inclusive=True)) &(master_table['Position'] == pos)].head(15)

    pp_pt_1 = stats.percentileofscore(pp_pt_1_filtered['PP_GW'], d, kind='rank')

    #PPNext3 Percentile
    pp_pt_filtered = master_table.sort_values(by=['PPNext3'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range, inclusive=True)) &(master_table['Position'] == pos)].head(15)

    pp_pt = stats.percentileofscore(pp_pt_filtered['PPNext3'], a, kind='rank')
    pp_pt = round(pp_pt,0)

    #Threat Percentile
    threat_perc_filtered = master_table.sort_values(by=['Threat'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range, inclusive=True)) &(master_table['Position'] == pos)].head(15)

    threat_perc_pt = stats.percentileofscore(threat_perc_filtered['Threat'], b, kind='rank')
    threat_perc_pt = round(threat_perc_pt,0)

    #Creativity Percentile
    creativity_perc_filtered = master_table.sort_values(by=['Creativity'],ascending=False)[(master_table['Current Price'].between(lower_range,upper_range, inclusive=True)) &(master_table['Position'] == pos)].head(15)

    creativity_perc_pt = stats.percentileofscore(creativity_perc_filtered['Creativity'], c, kind='rank')
    creativity_perc_pt = round(creativity_perc_pt,0)

    percentile.append(pt)
    pp_1_percentile.append(pp_pt_1)
    pp_percentile.append(pp_pt)
    threat_perc.append(threat_perc_pt)
    creativity_perc.append(creativity_perc_pt)

weekly_table['Form_%_15'] = percentile
weekly_table['Next_GW_%_15'] = pp_1_percentile
weekly_table['PP3_%_15'] = pp_percentile
weekly_table['Threat_%_15'] = threat_perc
weekly_table['Crtvty_%_15'] = creativity_perc

weekly_table = weekly_table[['element','Name', 'Position', 'Team_x','Current Price','EventPoints','Form', 'Form_%_15', 'Influence','Threat','Threat_%_15','Creativity','Crtvty_%_15',
                             'Merit','PP_GW','Next_GW_%_15', 'PPNext2', 'PPNext3','PP3_%_15', 'Selected By %','Prob. of Appearring']]    

# %%
st.header('Step 1: Assess your Gameweek Performance')
with st.expander('⬇️ Column Definitions'):
    st.text('EventPoints = Current gameweek points')
    st.text('Form = Average points over the past 4 gameweeks')
    st.text("Form_%_15 = Player form percentile rank with respect to the top 15 players within +/- 0.5m range. TLDR - 100% means there's no one better")
    st.text("Threat = FPL's measurment on how much the player's actions are leading to goals")
    st.text("Threat_%_15 = Player threat percentile rank with respect to the top 15 players within +/- 0.5m range. TLDR - 100% means there's no one better")
    st.text("Creativity = FPL's measurment on how much the player's actions are leading to assists")
    st.text("Crtvty_%_15 = Player creativity percentile rank with respect to the top 15 players within +/- 0.5m range. TLDR - 100% means there's no one better")
    st.text("Merit = FPLform's algorithm on how much we can rely on predicted scores based on recent player performance")
    st.text('PP_GW: Predicted points in the next gameweek')
    st.text("Next_GW_%_15 = Player potential points percentile rank with respect to the top 15 players within +/- 0.5m range. TLDR - 100% means there's no one better that will give you points")
    st.text('PPNext3: Predicted points in the next 3 gameweeks')
    st.text("PP3_%_15 = Player PPNext3 percentile rank with respect to the top 15 players within +/- 0.5m range. TLDR - 100% means there's no one better that will give you points")

st.dataframe(
    weekly_table.style.background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Form_%_15','Threat_%_15','Crtvty_%_15','Next_GW_%_15','PP3_%_15','Prob. of Appearring']]).set_precision(2)
)
# %%
#Player To Transfer
p =weekly_table.loc[(weekly_table['Current Price'] > 4.5) & (weekly_table['Prob. of Appearring'] < 0.85)].sort_values(['PP3_%_15','Prob. of Appearring'],ascending=[True,True])
index_select = p.iloc[0].name - 1
index_select = index_select.tolist()

st.text('Suggested Players To Transfer')
st.dataframe(p.style.background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Form_%_15','Threat_%_15','Crtvty_%_15','Next_GW_%_15','PP3_%_15','Prob. of Appearring']]).set_precision(2))

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
                    'Selected By %','Prob. of Appearring']]

#%%

upper_range = player_to_transfer_1_df.iloc[0][4] + 0.5
lower_range = player_to_transfer_1_df.iloc[0][4] - 2
pos = player_to_transfer_1_df.iloc[0][2]

options = master_table.sort_values(['PPNext3','Prob. of Appearring'],ascending= [False,False])[(master_table['Current Price'].between(lower_range,upper_range, inclusive=True)) & (master_table['Position'] == pos)].head(10)

options = options[['ID','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring']]

options = options.rename(columns={'ID':'element'})

options = pd.concat([player_to_transfer_1_df,options]).reset_index(drop=True)

xg_data_list = []
xa_data_list = []
xga_data_list = []
xg_players = list(options['element'])


for i in xg_players:
    str = 'https://fantasy.premierleague.com/api/element-summary/{}/'
    url = str.format(i)
    with requests.get(url) as f:
        d = f.json()
    d = pd.json_normalize(d['history'])
    d['expected_goals'] = pd.to_numeric(d['expected_goals'])
    d['expected_assists'] = pd.to_numeric(d['expected_assists'])
    d['expected_goals_conceded'] = pd.to_numeric(d['expected_goals_conceded'])
    xg = d['expected_goals'].sum()/(d['minutes'].sum()/90)
    xa = d['expected_assists'].sum()/(d['minutes'].sum()/90)
    xga = d['expected_goals_conceded'].sum()/(d['minutes'].sum()/90)

    xg_data_list.append(xg)
    xa_data_list.append(xa)
    xga_data_list.append(xga)

options['xG per 90'] = xg_data_list
options['xA per 90'] = xa_data_list
options['xGA per 90'] = xga_data_list       



st.text(f'Suggested Transfers For {player_to_transfer_1}')
st.dataframe(options.style.background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring']]).set_precision(2))
# %%
player_to_transfer_2 = st.selectbox(
    '2nd Player to Transfer',
    list(weekly_table['Name']),
    index=index_select
)

player_to_transfer_2_df = weekly_table[weekly_table['Name'] == player_to_transfer_2]
player_to_transfer_2_df = player_to_transfer_2_df[['element','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring']]

upper_range2 = player_to_transfer_2_df.iloc[0][4] + 0.5
lower_range2 = player_to_transfer_2_df.iloc[0][4] - 2
pos2 = player_to_transfer_2_df.iloc[0][2]

options2 = master_table.sort_values(['PPNext3','Prob. of Appearring'],ascending= [False,False])[(master_table['Current Price'].between(lower_range2,upper_range2, inclusive=True)) & (master_table['Position'] == pos2)].head(10)

options2 = options2[['ID','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring']]

options2 = options2.rename(columns={'ID':'element'})

options2 = pd.concat([player_to_transfer_2_df,options2]).reset_index(drop=True)

xg_data_list2 = []
xa_data_list2 = []
xga_data_list2 = []
xg_players2 = list(options2['element'])


for i in xg_players2:
    str = 'https://fantasy.premierleague.com/api/element-summary/{}/'
    url = str.format(i)
    with requests.get(url) as f:
        d = f.json()
    d = pd.json_normalize(d['history'])
    d['expected_goals'] = pd.to_numeric(d['expected_goals'])
    d['expected_assists'] = pd.to_numeric(d['expected_assists'])
    d['expected_goals_conceded'] = pd.to_numeric(d['expected_goals_conceded'])
    xg = d['expected_goals'].sum()/(d['minutes'].sum()/90)
    xa = d['expected_assists'].sum()/(d['minutes'].sum()/90)
    xga = d['expected_goals_conceded'].sum()/(d['minutes'].sum()/90)

    xg_data_list2.append(xg)
    xa_data_list2.append(xa)
    xga_data_list2.append(xga)

options2['xG per 90'] = xg_data_list2
options2['xA per 90'] = xa_data_list2
options2['xGA per 90'] = xga_data_list2       


st.text(f'Suggested Transfers For {player_to_transfer_2}')
st.dataframe(options2.style.background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring']]).set_precision(2))


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

options_price_1 = master_table.sort_values(['PPNext3','Prob. of Appearring'],ascending= [False,False])[(master_table['Current Price'].between(lower_range_price_1,upper_range_price_1, inclusive=True)) & (master_table['Position'] == price_1_pos)].head(10)

options_price_1 = options_price_1[['ID','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring']]

options_price_1 = options_price_1.rename(columns={'ID':'element'})

xg_data_list3 = []
xa_data_list3 = []
xga_data_list3 = []
xg_players3 = list(options_price_1['element'])


for i in xg_players3:
    str = 'https://fantasy.premierleague.com/api/element-summary/{}/'
    url = str.format(i)
    with requests.get(url) as f:
        d = f.json()
    d = pd.json_normalize(d['history'])
    d['expected_goals'] = pd.to_numeric(d['expected_goals'])
    d['expected_assists'] = pd.to_numeric(d['expected_assists'])
    d['expected_goals_conceded'] = pd.to_numeric(d['expected_goals_conceded'])
    xg = d['expected_goals'].sum()/(d['minutes'].sum()/90)
    xa = d['expected_assists'].sum()/(d['minutes'].sum()/90)
    xga = d['expected_goals_conceded'].sum()/(d['minutes'].sum()/90)

    xg_data_list3.append(xg)
    xa_data_list3.append(xa)
    xga_data_list3.append(xga)

options_price_1['xG per 90'] = xg_data_list3
options_price_1['xA per 90'] = xa_data_list3
options_price_1['xGA per 90'] = xga_data_list3   

st.dataframe(options_price_1.style.background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring']]).set_precision(2))

st.text('Suggested Replacements for Player 2')

price_2_pos = st.selectbox(
    'Filter Player 2 Suggestions by Position?',
    ['Goalkeeper','Defender','Midfielder','Forward'],
    index=1
)

upper_range_price_2 = remaining_price
lower_range_price_2 = remaining_price - 2

options_price_2 = master_table.sort_values(['PPNext3','Prob. of Appearring'],ascending= [False,False])[(master_table['Current Price'].between(lower_range_price_2,upper_range_price_2, inclusive=True)) & (master_table['Position'] == price_1_pos)].head(10)

options_price_2 = options_price_2[['ID','Name', 'Position', 'Team_x',
                    'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring']]

options_price_2 = options_price_2.rename(columns={'ID':'element'})

xg_data_list4 = []
xa_data_list4 = []
xga_data_list4 = []
xg_players4 = list(options_price_2['element'])


for i in xg_players4:
    str = 'https://fantasy.premierleague.com/api/element-summary/{}/'
    url = str.format(i)
    with requests.get(url) as f:
        d = f.json()
    d = pd.json_normalize(d['history'])
    d['expected_goals'] = pd.to_numeric(d['expected_goals'])
    d['expected_assists'] = pd.to_numeric(d['expected_assists'])
    d['expected_goals_conceded'] = pd.to_numeric(d['expected_goals_conceded'])
    xg = d['expected_goals'].sum()/(d['minutes'].sum()/90)
    xa = d['expected_assists'].sum()/(d['minutes'].sum()/90)
    xga = d['expected_goals_conceded'].sum()/(d['minutes'].sum()/90)

    xg_data_list4.append(xg)
    xa_data_list4.append(xa)
    xga_data_list4.append(xga)

options_price_2['xG per 90'] = xg_data_list4
options_price_2['xA per 90'] = xa_data_list4
options_price_2['xGA per 90'] = xga_data_list4 


st.dataframe(options_price_2.style.background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['Threat','Creativity','PP_GW','PPNext3','Prob. of Appearring']]).set_precision(2))

#%%
max_potential_pp3 = options_price_1.iloc[0][12] + options_price_2.iloc[0][12]
old_potential_pp3 = player_to_transfer_1_df.iloc[0][12] + player_to_transfer_2_df.iloc[0][12]
delta_potential_pp3 = max_potential_pp3 - old_potential_pp3

st.text(f'Your transfers have the potential to give you an additional {round(delta_potential_pp3,1)} points over the next 3 gameweeks')


st.header('Step 3: Keep Updated On Macro Trends in FPL!')
st.text('Breakdown of potential points over the next 3 GW by position')
st.text('Crop to zoom in. Hover for name and price. Double click to reset graph')
fig1 = px.violin(master_table[master_table['PPNext3'] > 10], y='PPNext3',hover_data=['Name','Current Price'],points='all',box=True,color='Position')
st.plotly_chart(fig1, use_container_width=True)

st.text('Breakdown of potential points over the next 3 GW by team')
st.text('Crop to zoom in. Hover for name and price. Double click to reset graph')
fig2 = px.violin(master_table[master_table['PPNext3'] > 10], y='PPNext3',hover_data=['Name','Current Price'],points='all',box=True,color='Team_x')
st.plotly_chart(fig2, use_container_width=True)