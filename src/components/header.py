import streamlit as st
from textwrap import dedent

def home_header():
    st.markdown("""
<div style="display:flex; flex-direction:column; align-items:center ;justify-content:center; margin-top:30px; margin-bottom:30px">

<image src='https://i.ibb.co/YTYGn5qV/logo.png' style="height:100px">
<h1 style='text-align:center; color:#E0E3FF'>Snap<br>Class</h1>

</div>
""",unsafe_allow_html=True)


def dashboard_header():


    
    st.markdown("""

        <style> 
        .header-dashboard{
            text-align:left !important;
            color:#5865F2 !important;
        }
        
        
        </style>
        <div style="display:flex; align-items:center; justify-content:center; gap:10px">
            <img src='https://i.ibb.co/YTYGn5qV/logo.png' style='height:85px;' />
            <h2 class="header-dashboard">SNAP<br/>CLASS</h2>
        </div>   
                
                """, unsafe_allow_html=True)