import streamlit as st
import pandas as pd
import requests
from scipy import stats
import itertools
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Function to perform the optimization
def optimize_team(weekly_table, new_data, num_replacements, metric, max_selected_by_percent, players_to_retain):
    # Adjust the metric value with the probability of appearing for both datasets
    if 'Prob. of Appearring' in weekly_table.columns:
        weekly_table['Adjusted Metric'] = weekly_table[metric] * weekly_table['Prob. of Appearring']
    else:
        weekly_table['Adjusted Metric'] = weekly_table[metric]

    if 'Prob. of Appearring' in new_data.columns:
        new_data['Adjusted Metric'] = new_data[metric] * new_data['Prob. of Appearring']
    else:
        new_data['Adjusted Metric'] = new_data['Metric']

    # Create a combined metric for removal, factoring in the Current Price
    max_price = weekly_table['Current Price'].max()
    weekly_table['Removal Metric'] = weekly_table['Adjusted Metric'] - (weekly_table['Current Price'] / max_price)
    weekly_table2 = weekly_table
    
    # Filter out players based on the Selected By % threshold
    new_data = new_data[new_data['Selected By %'] <= max_selected_by_percent]
    
    # Exclude players that users want to retain
    players_to_remove = weekly_table[~weekly_table['Name'].isin(players_to_retain)].nsmallest(num_replacements, 'Removal Metric')
    
    # Remaining players in the weekly table
    remaining_weekly_players = weekly_table.drop(players_to_remove.index)

    # Identify the best replacements for the players to remove
    available_budget = players_to_remove['Current Price'].sum() + (metrics_data.loc[0][6]/10)
    potential_replacements_list = []
    for _, player in players_to_remove.iterrows():
        potential_replacements_for_player = new_data[
            (new_data['Position'] == player['Position'])
        ]
        potential_replacements_list.append(potential_replacements_for_player)

    # Get combinations of potential replacements
    best_replacements = None
    best_metric = -float('inf')
    for comb in itertools.product(*[df.itertuples(index=False) for df in potential_replacements_list]):
        # Avoiding duplicate players
        player_names = [player.Name for player in comb]
        if len(player_names) != len(set(player_names)):
            continue        

        total_price = sum([getattr(player, 'Price') for player in comb])
        total_metric = sum([getattr(player, metric) for player in comb])
        
        if total_price <= available_budget and total_metric > best_metric:
            best_metric = total_metric
            best_replacements = comb

    if best_replacements:
        best_replacements_df = pd.DataFrame(best_replacements, columns=new_data.columns)
        best_replacements_df = best_replacements_df[['ID','Name', 'Position', 'Team_x',
                   'Current Price','Form','Influence', 'Creativity',
                    'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
                    'Selected By %','Prob. of Appearring','Adjusted Metric','Form_%_15', 'Threat_%_15', 'Crtvty_%_15', 'Next_GW_%_15', 'PP3_%_15','xG per 90', 'xA per 90', 'xGA per 90', 'GW1_Diff', 'GW2_Diff', 'GW3_Diff', 'GW1_Home?', 'GW2_Home?', 'GW3_Home?']]

        #xg_data_list = []
        #xa_data_list = []
        #xga_data_list = []
        #xg_players = list(best_replacements_df['ID'])
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
        #    xg_data_list.append(xg)
        #    xa_data_list.append(xa)
        #    xga_data_list.append(xga)
        #    dif1_list.append(dif1)
        #    home1_list.append(home1)
        #    dif2_list.append(dif2)
        #    home2_list.append(home2)
        #    dif3_list.append(dif3)
        #    home3_list.append(home3)
#
        #best_replacements_df['xG per 90'] = xg_data_list
        #best_replacements_df['xA per 90'] = xa_data_list
        #best_replacements_df['xGA per 90'] = xga_data_list     
        #best_replacements_df['GW1_Diff'] = dif1_list
        #best_replacements_df['GW1_Home?'] = home1_list
        #best_replacements_df['GW2_Diff'] = dif2_list
        #best_replacements_df['GW2_Home?'] = home2_list
        #best_replacements_df['GW3_Diff'] = dif3_list
        #best_replacements_df['GW3_Home?'] = home3_list

        # Updated weekly table after the replacements
        updated_weekly_table = pd.concat([remaining_weekly_players, best_replacements_df], ignore_index=True)
        # Calculate the increase in the chosen metric
        increase = updated_weekly_table['Adjusted Metric'].sum() - weekly_table['Adjusted Metric'].sum()
    else:
        updated_weekly_table = remaining_weekly_players.copy()
        increase = 0



    
    ## Sort the player pool based on Adjusted Metric in descending order
    #sorted_new_data = new_data.sort_values(by='Adjusted Metric', ascending=False)
#
    ## Dictionary to keep track of best replacements
    #best_replacements_efficient = {}

    ## Iterate over players to remove and find the best replacement for each position
    #for _, player in players_to_remove.iterrows():
    #    for _, potential_replacement in sorted_new_data.iterrows():
    #        if potential_replacement['Position'] == player['Position'] and potential_replacement['Current Price'] <= player['Current Price']:
    #            best_replacements_efficient[player['Name']] = potential_replacement
    #            # Once a player from new_data is selected, we remove them to avoid selecting them again
    #            sorted_new_data = sorted_new_data.drop(potential_replacement.name)
    #            break
#
    ## Convert the best replacements found into a DataFrame
    #best_replacements_efficient_df = pd.DataFrame(list(best_replacements_efficient.values()))
#
    #best_replacements_efficient_df = best_replacements_efficient_df[['ID','Name', 'Position', 'Team_x',
    #                'Current Price','Form','Influence', 'Creativity',
    #                'Threat','Merit','PP_GW', 'PPNext2', 'PPNext3',
    #                'Selected By %','Prob. of Appearring','Adjusted Metric']]
#
    #xg_data_list = []
    #xa_data_list = []
    #xga_data_list = []
    #xg_players = list(best_replacements_efficient_df['ID'])
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
    #    xg_data_list.append(xg)
    #    xa_data_list.append(xa)
    #    xga_data_list.append(xga)
    #    dif1_list.append(dif1)
    #    home1_list.append(home1)
    #    dif2_list.append(dif2)
    #    home2_list.append(home2)
    #    dif3_list.append(dif3)
    #    home3_list.append(home3)
#
    #best_replacements_efficient_df['xG per 90'] = xg_data_list
    #best_replacements_efficient_df['xA per 90'] = xa_data_list
    #best_replacements_efficient_df['xGA per 90'] = xga_data_list     
    #best_replacements_efficient_df['GW1_Diff'] = dif1_list
    #best_replacements_efficient_df['GW1_Home?'] = home1_list
    #best_replacements_efficient_df['GW2_Diff'] = dif2_list
    #best_replacements_efficient_df['GW2_Home?'] = home2_list
    #best_replacements_efficient_df['GW3_Diff'] = dif3_list
    #best_replacements_efficient_df['GW3_Home?'] = home3_list 
#
#
#
#
    ## Updated weekly table after the replacements
    #updated_weekly_table_efficient_2 = pd.concat([remaining_weekly_players, best_replacements_efficient_df], ignore_index=True)
    #
    ## Calculate the increase in the chosen metric
    #increase = updated_weekly_table_efficient_2['Adjusted Metric'].sum() - weekly_table['Adjusted Metric'].sum()
    
    return players_to_remove, best_replacements_df, updated_weekly_table, increase, weekly_table2, available_budget


# Streamlit App
st.set_page_config(
    layout='wide'
)
st.title('FPL 23/24 Auto Optimizer')

# Get Needed Files
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
gameweek = default_gw_value

@st.cache_data(ttl=3600)
def master_table():
    #Get Master Table
    url = 'https://drive.google.com/file/d/1f-q5duVoamPtC9kZxvyXLPANdcYYzBKE/view?usp=sharing'
    url = 'https://drive.google.com/uc?id=' + url.split('/')[-2]
    df = pd.read_csv(url)
    df = df.drop('Unnamed: 0',axis=1)
    return df


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

master_table = master_table()
master_table = master_table.rename(columns={f'{list(master_table.columns)[50]}':'PP_GW'})
gameweek_data = gameweek_data(team_id,gameweek)
metrics_data =metrics_data(team_id,gameweek)

weekly_table = pd.merge(gameweek_data,master_table,how='left',left_on='element',right_on='ID')
weekly_table = weekly_table[['multiplier','element',
'Name', 'Position', 'Team_x', 'Current Price',
'Points Per Game', 'Event Points','Form', 'ICT Index','Penalties Order', 
'Corners/ Indirect Order', 'Minutes', 'Influence', 'Creativity', 'Threat', 'Merit',
'Form over/under-performance over the last 4 GW', 'Prob. of Appearring',
'PP_GW', 'PPNext2', 'ValNext2', 'PPNext3',
'ValNext3', 'Selected By %','Form_%_15', 'Threat_%_15', 'Crtvty_%_15', 'Next_GW_%_15', 'PP3_%_15','xG per 90', 'xA per 90', 'xGA per 90', 'GW1_Diff', 'GW2_Diff', 'GW3_Diff', 'GW1_Home?', 'GW2_Home?', 'GW3_Home?']]

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

#weekly_table = weekly_table[['element','Name', 'Position', 'Team_x','Current Price','Event Points','Form', 'Form_%_15', 'Influence','Threat','Threat_%_15','Creativity','Crtvty_%_15',
#                             'Merit','PP_GW','Next_GW_%_15', 'PPNext2', 'PPNext3','PP3_%_15', 'Selected By %','Prob. of Appearring']]


weekly_table_file = weekly_table
new_data_file = master_table

players_to_retain = st.multiselect('Select players to retain, if any (they won\'t be suggested as transfers out):', weekly_table['Name'].tolist())

# Input widgets
num_replacements = st.selectbox("Select number of players to transfer out:", (1,2,3),0)
st.markdown('*Heads up - 3 transfers will take some time (about 30 - 40 sec) due to increased computational requirements*')
st.text("")
max_selected_by_percent = st.slider("Looking for Differentials? Define Your Maximum 'Selected By %' for transfers in:", 0.0, 100.0, 100.0)
metric = st.selectbox('Choose the gameweek horizion to optimize for:', ['PP_GW', 'PPNext2', 'PPNext3'])
st.markdown('*PP_GW = Next Gameweek, PPNext2 = Next 2 Gameweeks, PPNext3 = Next 3 Gameweeks*')

if len(weekly_table_file) > 0  and len(new_data_file) >0:
    weekly_table = weekly_table_file
    new_data = new_data_file
    # Rename the PPGW column to PP_GW in new_data
    if 'PPGW' in new_data.columns:
        new_data.rename(columns={'PPGW': 'PP_GW'}, inplace=True)
    
    # Call the optimization function
    players_to_remove, players_to_add, updated_weekly_table, increase, weekly_table2, available_budget = optimize_team(weekly_table, new_data, num_replacements, metric, max_selected_by_percent, players_to_retain)
    
    # Display results
    st.subheader('Projected Increase in the Potential Points From Transfers')
    st.write(round(increase,1))
    #st.write(players_to_remove[['Name', 'Position', 'Team_x','Current Price','Event Points','Form', 'Form_%_15','Threat_%_15','Crtvty_%_15','PP_GW','Next_GW_%_15','PPNext3','PP3_%_15','Prob. of Appearring','Adjusted Metric','Removal Metric']])

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
    st.subheader('Players to Transfer Out')
    st.text('Players are chosen based on probability of appearing and potential points')
    st.text(f"Including what's in your bank, you have a total of {round(available_budget,1)} to spend")


    options_to_remove = players_to_remove[['Name', 'Position', 'Team_x',
                        'Current Price','Merit','PP_GW', 'PPNext2', 'PPNext3','Selected By %','Prob. of Appearring','Form','Threat','xG per 90', 'Creativity', 'xA per 90', 'xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff','GW1_Home?','GW2_Home?','GW3_Home?']]    
    gridOptions = GridOptionsBuilder.from_dataframe(options_to_remove)
    gridOptions.configure_column('Name', headerTooltip='Click hamburger to filter and select columns', pinned='left', 
                                sorteable=False, width = 100)
    gridOptions.configure_column('Position', headerTooltip='Click hamburger to filter and select columns', width = 90, header_name='Pos')
    #gridOptions.configure_column('element', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='ID')
    gridOptions.configure_column('Team_x', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='Team')
    gridOptions.configure_column('Current Price', headerTooltip='Click hamburger to filter and select columns', width = 50, header_name='$')
    #gridOptions.configure_column('Event Points', headerTooltip='Click hamburger to filter and select columns', width = 80, header_name='GW Pts')
    gridOptions.configure_column('Form', headerTooltip='Click hamburger to filter and select columns', width = 70, header_name='Form')
    #gridOptions.configure_column('Influence', headerTooltip='Click hamburger to filter and select columns', width = 100)
    gridOptions.configure_column('Creativity', headerTooltip='Click hamburger to filter and select columns', width = 100)
    gridOptions.configure_column('Merit', headerTooltip='Click hamburger to filter and select columns', width = 100)
    gridOptions.configure_column('Threat', headerTooltip='Click hamburger to filter and select columns', width = 80)
    gridOptions.configure_column('PP_GW', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next GW')
    gridOptions.configure_column('PPNext2', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 2 GW')
    gridOptions.configure_column('PPNext3', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 3 GW',pinned='left')
    gridOptions.configure_column('Selected By %', headerTooltip='Click hamburger to filter and select columns', width = 120, header_name='Selected By %')
    gridOptions.configure_column('Prob. of Appearring', headerTooltip='Click hamburger to filter and select columns', width = 160, header_name='Prob of Appearring(%)')
    gridOptions.configure_column('xG per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
    gridOptions.configure_column('xA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
    gridOptions.configure_column('xGA per 90', headerTooltip='Click hamburger to filter and select columns', width = 100)
    gridOptions.configure_column('GW1_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
    gridOptions.configure_column('GW1_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
    gridOptions.configure_column('GW2_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
    gridOptions.configure_column('GW2_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
    gridOptions.configure_column('GW3_Diff', headerTooltip='Click hamburger to filter and select columns', width = 100)
    gridOptions.configure_column('GW3_Home?', headerTooltip='Click hamburger to filter and select columns', width = 130)
    gridOptions.configure_columns(['PP_GW'],cellStyle =cellstylejscode3)
    gridOptions.configure_columns(['PPNext3'],cellStyle =cellstylejscode4)
    gridOptions.configure_columns(['GW1_Diff','GW2_Diff','GW3_Diff'],cellStyle =cellstylejscode5)
    gridOptions.configure_columns(['Selected By %'],cellStyle =cellstylejscode6)
    gridOptions.configure_columns(['Prob. of Appearring'],cellStyle =cellstylejscode7)
    gb = gridOptions.build()

    AgGrid(
        options_to_remove,theme='streamlit', gridOptions=gb, allow_unsafe_jscode=True,
    )
    
    st.subheader('Players to Transfer In')
    options_to_show = players_to_add[['Name', 'Position', 'Team_x',
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

    #table_view = st.radio(
    #    "Select your view:",
    #    ['All','Predicted Points + Fixture Difficulty Rating','ICT + Form + xG','xG Data','Fixture Difficulty Rating + Home/Away'],
    #    index=1,
    #    key=1
    #)
    #if table_view == 'All':
    #    players_to_add_style = players_to_add.style\
    #                    .format(precision=2)\
    #                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['GW1_Diff','GW2_Diff','GW3_Diff']])
    #    st.dataframe(players_to_add_style)
    #elif table_view == 'ICT + Form + xG':
    #    players_to_add_style = players_to_add[['Name','Position','Team_x','Current Price','Form','Threat','xG per 90','Creativity','xA per 90','xGA per 90']].style\
    #                    .format(precision=2)
    #    st.dataframe(players_to_add_style)
    #elif table_view == 'Predicted Points + Fixture Difficulty Rating':
    #    players_to_add_style = players_to_add[['Name','Position','Team_x','Current Price','Merit','PP_GW','PPNext2','PPNext3','Selected By %','Prob. of Appearring','GW1_Diff','GW2_Diff','GW3_Diff']].style\
    #                    .format(precision=2)\
    #                    .background_gradient(cmap='Reds', subset=pd.IndexSlice[:,['GW1_Diff','GW2_Diff','GW3_Diff']])
    #    st.dataframe(players_to_add_style)
    #elif table_view == 'xG Data':
    #    players_to_add_style = players_to_add[['Name','Position','Team_x','Current Price','xG per 90','xA per 90','xGA per 90']].style\
    #                    .format(precision=2)
    #    st.dataframe(players_to_add_style)
    #elif table_view == 'Fixture Difficulty Rating + Home/Away':
    #    players_to_add_style = players_to_add[['Name','Position','Team_x','Current Price','PP_GW','GW1_Diff','GW1_Home?','GW2_Diff','GW2_Home?','GW3_Diff','GW3_Home?','PPNext3']].style\
    #                    .format(precision=2)\
    #                    .background_gradient(cmap='RdYlGn', subset=pd.IndexSlice[:,['PP_GW','GW1_Diff','GW2_Diff','GW3_Diff','PPNext3']])
    #    st.dataframe(players_to_add_style)
    #
    #st.subheader('Updated Squad Selection')
    #updated_weekly_table_style = updated_weekly_table[['Name', 'Position', 'Team_x','Current Price','Event Points','Form', 'Form_%_15','Threat_%_15','Crtvty_%_15','PP_GW','Next_GW_%_15','PPNext3','PP3_%_15','Prob. of Appearring']].style\
    #                   .format(precision=2)\
    #                   .background_gradient(cmap='RdYlGn',subset=pd.IndexSlice[:,['Form_%_15','PP_GW','Next_GW_%_15','PPNext3','PP3_%_15','Prob. of Appearring']])
    
    #st.write(updated_weekly_table_style)
    st.subheader('Explore Other Players')
    options_to_explore = new_data[['Name', 'Position', 'Team_x',
                        'Current Price','Merit','PP_GW', 'PPNext2', 'PPNext3','Selected By %','Prob. of Appearring','Form','Threat','xG per 90', 'Creativity', 'xA per 90', 'xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff','GW1_Home?','GW2_Home?','GW3_Home?']]    
    gridOptions4 = GridOptionsBuilder.from_dataframe(options_to_explore)
    gridOptions4.configure_pagination(enabled=True,paginationAutoPageSize=True, paginationPageSize=10)
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
        options_to_explore,theme='streamlit', gridOptions=gb4, allow_unsafe_jscode=True,
    )




    st.subheader('Updated Squad Selection')
    options_to_show2 = updated_weekly_table[['Name', 'Position', 'Team_x',
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

