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
    - Just input your Team ID and how many players you are looking to transfer
    - Bonus -> If you are looking for differentials, you can define your maximum Selected By %

    ### I have too much time, I want to go through the process
    - Go to Deep Dive
    - Input your Team ID and go through a step by step process to optimize your team
    - Don't want to look at numbers? Fret not, I provide insights and suggestions in words
    - Have a hand at choosing who you want to transfer

    ### Coming soon -> Wildcard optimizer ###
"""
)