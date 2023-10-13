import streamlit as st
import pandas as pd
import pulp
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

# Load data function
#@st.cache_data
#def load_data(uploaded_file):
#    return pd.read_csv(uploaded_file)

# Optimization function
def optimize_team(all_players, current_team, num_transfers, budget, chosen_metric, top_n=3):
    solutions = []

    # List of players to consider for transfer in
    transfer_pool = all_players[~all_players['Name'].isin(current_team['Name'])]
    used_solutions = []

    for _ in range(top_n):
        prob = pulp.LpProblem(f"FantasyFootballOptimization_{_}", pulp.LpMaximize)
        
        # Create decision variables
        in_vars = pulp.LpVariable.dicts("In", range(len(transfer_pool)), cat="Binary")
        out_vars = pulp.LpVariable.dicts("Out", range(len(current_team)), cat="Binary")
        
        # Objective function: maximize adjusted difference in PPNext3 for players in and out
        prob += pulp.lpSum([in_vars[i] * transfer_pool.iloc[i][chosen_metric] * transfer_pool.iloc[i]['Prob. of Appearring'] for i in range(len(transfer_pool))]) - \
               pulp.lpSum([out_vars[i] * current_team.iloc[i][chosen_metric] * current_team.iloc[i]['Prob. of Appearring'] for i in range(len(current_team))])
        
        # Constraint: number of players transferred in and out should be equal to num_transfers
        prob += pulp.lpSum(in_vars.values()) == num_transfers
        prob += pulp.lpSum(out_vars.values()) == num_transfers
        
        # Constraint: The total cost of the original and updated weekly table should be the same
        #prob += pulp.lpSum([in_vars[i] * transfer_pool.iloc[i]['Current Price'] for i in range(len(transfer_pool))]) - \
        #       pulp.lpSum([out_vars[i] * current_team.iloc[i]['Current Price'] for i in range(len(current_team))]) == 0

        # Constraint: Budget
        total_cost = current_team['Current Price'].sum() - pulp.lpSum([out_vars[i] * current_team.iloc[i]['Current Price'] for i in range(len(current_team))]) + \
                     pulp.lpSum([in_vars[i] * transfer_pool.iloc[i]['Current Price'] for i in range(len(transfer_pool))])
        prob += total_cost <= budget
        
        # Positional constraints
        for position in ['Goalkeeper', 'Defender', 'Midfielder', 'Forward']:
            prob += pulp.lpSum([in_vars[i] for i in range(len(transfer_pool)) if transfer_pool.iloc[i]['Position'] == position]) == \
                    pulp.lpSum([out_vars[i] for i in range(len(current_team)) if current_team.iloc[i]['Position'] == position])
        
        # Team constraints
        for team in all_players['Team_x'].unique():
            team_players_current = sum([1 for _, player in current_team.iterrows() if player['Team_x'] == team])
            prob += pulp.lpSum([in_vars[i] for i in range(len(transfer_pool)) if transfer_pool.iloc[i]['Team_x'] == team]) - \
                    pulp.lpSum([out_vars[i] for i in range(len(current_team)) if current_team.iloc[i]['Team_x'] == team]) + team_players_current <= 3
        
        # Constraint to ensure different solutions
        for solution in used_solutions:
            prob += pulp.lpSum([out_vars[i] for i in solution[0]] + [in_vars[i] for i in solution[1]]) <= num_transfers * 2 - 1

        # Solve the problem
        prob.solve()

        # Extract the solution
        players_in_indices = [i for i in range(len(transfer_pool)) if in_vars[i].value() == 1.0]
        players_out_indices = [i for i in range(len(current_team)) if out_vars[i].value() == 1.0]
        
        solutions.append((players_out_indices, players_in_indices))
        
        # Add to used solutions
        used_solutions.append((players_out_indices, players_in_indices))

    return solutions

# Streamlit app

st.set_page_config(
    layout='wide'
)

st.title('FPL 23/24 Auto Optimizer')
st.write('Find the transfers that give you highest potential points in seconds')

#Get needed data
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
master_table = master_table.rename(columns={f'{list(master_table.columns)[51]}':'PP_GW'})
gameweek_data = gameweek_data(team_id,gameweek)
metrics_data =metrics_data(team_id,gameweek)

weekly_table = pd.merge(gameweek_data,master_table,how='left',left_on='element',right_on='ID')
weekly_table = weekly_table[['multiplier','element',
'Name', 'Position', 'Team_x', 'Current Price',
'Points Per Game', 'Event Points','Form', 'ICT Index','Penalties Order', 
'Corners/ Indirect Order', 'Minutes', 'Influence', 'Creativity', 'Threat', 'Merit',
'Form over/under-performance over the last 4 GW', 'Prob. of Appearring',
'PP_GW', 'PPNext2', 'ValNext2', 'PPNext3',
'ValNext3', 'Selected By %','Form_%_15', 'Threat_%_15', 'Crtvty_%_15', 'Next_GW_%_15', 'PP3_%_15','xG per 90', 'xA per 90', 'xGA per 90', 'GW1_Diff', 'GW2_Diff', 'GW3_Diff', 'GW1_Home?', 'GW2_Home?', 'GW3_Home?','PPNext4']]


# Define tables
#all_players_file = st.file_uploader("Upload All Players Data (Data(1).csv)", type=["csv"])
#current_team_file = st.file_uploader("Upload Current Team Selection (weekly_table.csv)", type=["csv"])
all_players_file = master_table
current_team_file = weekly_table
budget = current_team_file['Current Price'].sum() + (metrics_data.loc[0][6]/10)

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



if len(all_players_file) > 1 and len(current_team_file) > 1:
    all_players = all_players_file
    current_team = current_team_file

    # List of players to consider for transfer in
    transfer_pool = all_players[~all_players['Name'].isin(current_team['Name'])]

    # Display original weekly table
    st.header("Original Weekly Team:")
    st.write(f"💶 :blue[Total Budget Available Including What's In Your Bank: {round(budget,1)}]")
    #st.text(f"Total Budget Available Including What's In Your Bank: {round(budget,1)}")
    original_table = current_team.sort_values(['PP_GW'],ascending=False)[['Name','PP3_%_15','Next_GW_%_15', 'Position', 'Team_x',
                        'Current Price','Merit','PP_GW', 'PPNext2', 'PPNext3','PPNext4','Selected By %','Prob. of Appearring','Form','Threat','xG per 90', 'Creativity', 'xA per 90', 'xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff','GW1_Home?','GW2_Home?','GW3_Home?']] 
    gridOptions = GridOptionsBuilder.from_dataframe(original_table)

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
    gridOptions.configure_column('PPNext4', headerTooltip='Click hamburger to filter and select columns', width = 110, header_name='PP Next 4 GW')
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
    gridOptions.configure_column('Next_GW_%_15', headerTooltip='Click hamburger to filter and select columns', width = 150, header_name='PP Next GW Rank(%)')
    gridOptions.configure_column('PP3_%_15', headerTooltip='Click hamburger to filter and select columns', width = 160, header_name='PP Next 3 GW Rank(%)')
    gridOptions.configure_columns(['Next_GW_%_15','PP3_%_15'],cellStyle =cellstylejscode)
    gridOptions.configure_columns(['PP_GW'],cellStyle =cellstylejscode3)
    gridOptions.configure_columns(['PPNext3'],cellStyle =cellstylejscode4)
    gridOptions.configure_columns(['GW1_Diff','GW2_Diff','GW3_Diff'],cellStyle =cellstylejscode5)
    gridOptions.configure_columns(['Selected By %'],cellStyle =cellstylejscode6)
    gridOptions.configure_columns(['Prob. of Appearring'],cellStyle =cellstylejscode7)
    gb = gridOptions.build()

    AgGrid(
        original_table,theme='streamlit', gridOptions=gb, allow_unsafe_jscode=True,
    )
    #st.table(current_team[['Name', 'Position', 'Team_x', 'Current Price', 'PPNext3', 'Prob. of Appearring']])
    #orig_cost = current_team['Current Price'].sum()


    # User Inputs
    num_transfers = st.slider('Number of players to transfer out:', 1, 5, 2)
    #budget = st.number_input("Total Budget:", value=orig_cost, step=0.1)
    metrics = ['PP_GW', 'PPNext2', 'PPNext3', 'PPNext4']
    chosen_metric = st.selectbox('Choose Metric to Optimize:', metrics)
    st.markdown('*PP_GW = Next Gameweek, PPNext2 = Next 2 Gameweeks, PPNext3 = Next 3 Gameweeks, etc*')

    # Run Optimization
    if st.button('Optimize Team'):
        solutions = optimize_team(all_players, current_team, num_transfers, budget, chosen_metric)
        
        # Display results
        for idx, (players_out_indices, players_in_indices) in enumerate(solutions):
            st.header(f"Option {idx + 1}:")

            # Calculate and display the increase in points and total cost
            points_before = current_team[chosen_metric].sum()
            points_after = (current_team[chosen_metric].sum() - current_team.iloc[players_out_indices][chosen_metric].sum() +
                            transfer_pool.iloc[players_in_indices][chosen_metric].sum())
            
            st.subheader(f":blue[Increase in {chosen_metric}: {round(points_after - points_before,2)}]")            

            # Display players transferred out as a table
            st.write('⬅️ :red[Players Transferred Out:]')
            transfers_out = current_team.iloc[players_out_indices][['Name','PP3_%_15','Next_GW_%_15', 'Position', 'Team_x',
                        'Current Price','Merit','PP_GW', 'PPNext2', 'PPNext3','PPNext4','Selected By %','Prob. of Appearring','Form','Threat','xG per 90', 'Creativity', 'xA per 90', 'xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff','GW1_Home?','GW2_Home?','GW3_Home?']] 
            AgGrid(
                transfers_out,theme='streamlit', gridOptions=gb, allow_unsafe_jscode=True, key= idx+1+10
            )           
            #st.table(current_team.iloc[players_out_indices][['Name', 'Position', 'Team_x', 'Current Price', chosen_metric,'Prob. of Appearring']])
            
            # Display players transferred in as a table
            st.write('➡️ :green[Players Transferred In:]')
            transfers_in = transfer_pool.iloc[players_in_indices][['Name','PP3_%_15','Next_GW_%_15', 'Position', 'Team_x',
                        'Current Price','Merit','PP_GW', 'PPNext2', 'PPNext3','PPNext4','Selected By %','Prob. of Appearring','Form','Threat','xG per 90', 'Creativity', 'xA per 90', 'xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff','GW1_Home?','GW2_Home?','GW3_Home?']]
            AgGrid(
                transfers_in,theme='streamlit', gridOptions=gb, allow_unsafe_jscode=True, key= idx+1+20
            )      
            #st.table(transfer_pool.iloc[players_in_indices][['Name', 'Position', 'Team_x', 'Current Price', chosen_metric,'Prob. of Appearring']])
            
            # Calculate and display the increase in points and total cost
            #points_before = current_team[chosen_metric].sum()
            #points_after = (current_team[chosen_metric].sum() - current_team.iloc[players_out_indices][chosen_metric].sum() +
            #                transfer_pool.iloc[players_in_indices][chosen_metric].sum())
            #
            #st.write(f":green[Increase in {chosen_metric}: {round(points_after - points_before,1)}]")
            
            #cost_of_optimized_team = orig_cost
            
            #st.write(f"Total Cost of Optimized Team: {cost_of_optimized_team}")

            # Display updated weekly table
            updated_team = pd.concat([current_team.drop(players_out_indices), transfer_pool.iloc[players_in_indices]])
            st.write("Updated Weekly Team:")
            st.write(f"Total Cost of Updated Team: {round(updated_team['Current Price'].sum(),1)}")
            new_team = updated_team.sort_values(['PP_GW'],ascending=False)[['Name','PP3_%_15','Next_GW_%_15', 'Position', 'Team_x',
                        'Current Price','Merit','PP_GW', 'PPNext2', 'PPNext3','PPNext4','Selected By %','Prob. of Appearring','Form','Threat','xG per 90', 'Creativity', 'xA per 90', 'xGA per 90','GW1_Diff','GW2_Diff','GW3_Diff','GW1_Home?','GW2_Home?','GW3_Home?']] 
            AgGrid(
                new_team,theme='streamlit', gridOptions=gb, allow_unsafe_jscode=True, key= idx+1+30
            )      
            #st.table(updated_team[['Name', 'Position', 'Team_x', 'Current Price', chosen_metric]])
            #st.write(f"Total Cost of Updated Team: {updated_team['Current Price'].sum()}")

            ## Display updated weekly table
            #updated_team = pd.concat([current_team.drop(players_out_indices), transfer_pool.iloc[players_in_indices]])
            #st.write("Updated Weekly Team:")
            #st.table(updated_team[['Name', 'Position', 'Team_x', 'Current Price', 'PPNext3']])
            #st.write(f"Total Cost of Updated Team: {updated_team['Current Price'].sum()}")
