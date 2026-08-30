import streamlit as st
import time
import pandas as pd
from src.database.db import create_attendance

def show_attendance_results(df,logs):
    st.write("Please review the attendance before confirming.")
    st.dataframe(df,hide_index=True,width='stretch')

    col1,col2=st.columns(2)
    with col1:
        if st.button("Discard",width='stretch'):
            st.session_state.voice_attendance_results=None
            st.session_state.attendance_images=[]
            st.rerun()

    with col2:
        if st.button('Confirm & Save',type='primary',width='stretch'):
            try:
                
                create_attendance(logs)
                st.toast("Attendance recorded successfully!")
                time.sleep(1)
                st.session_state.attendance_images=[]
                st.session_state.voice_attendance_results=None
                st.rerun()
            except Exception as e:
                st.error("Failed to sync attendance.")
                


@st.dialog('Attendance Report')
def attendance_result_dialog(df,logs):
    show_attendance_results(df,logs)