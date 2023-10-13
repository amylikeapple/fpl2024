import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Welcome to TheFPLAnalyst's FPL Team Optimizer 23/24👋")

st.markdown(
    """
    Looking to optimize your FPL team for those green arrows? This tool is here to help

    ### I don't have time, just optimize for me!
    - Go to Auto Optimizer
    - Just input your Team ID and how many players you are looking to transfer. How to find [Team ID](https://allaboutfpl.com/2023/07/what-is-team-id-in-fpl-how-to-get-a-low-fpl-team-id/)

    ### I have too much time, I want to go through the process
    - Go to Deep Dive
    - Input your Team ID and go through a step by step process to optimize your team
    - Don't want to look at numbers? Fret not, I provide insights and suggestions in words
    - Have a hand at choosing who you want to transfer

    ### Tips
    - Tables are interactive. Click on column hamburgers ☰ in the headers to filter, pin or select which columns should appear
    - If you are on mobile, rotate and view in widescreen
    - If you are on mobile, press and hold column headers to filter, pin or select which columns should appear

    ### Coming soon -> Wildcard optimizer ###

    ### Important! ⬇️ ###

"""
)


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