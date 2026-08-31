import streamlit as st
from src.components.share_subject_dialog import share_subject_dialog
from src.database.db import unenroll_student_from_subject
import time

def share_button(subject_name,subject_id,subject_code,user_id=None):
    if st.button(f'Share :'+subject_name,key=f"Share_"+str(subject_id),icon=":material/share:"):
        share_subject_dialog(subject_id)

def unenroll_student_button(subject_name,subject_id,subject_code,user_id=None):
    if st.button(f"Unenroll from {subject_name}", type='tertiary', width='stretch', icon=':material/delete_forever:',key=f"Share_"+str(subject_id)):
        try:

            unenroll_student_from_subject(subject_id,user_id)
            st.toast(f"Unenrolled from {subject_name} successfully!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error("Unexpected Error!")



def subject_card(subject_name, subject_code, division, subject_id,stats=None, footer_callback=None,user_id=None):
    html = f"""
        <div style="background:white; border-left: 8px solid #EB459E; padding:25px; border-radius: 20px; border: 1px solid black; margin-bottom:20px;">
        <h3 style="margin:0; color: #1e293b; font-size: 1.5rem ">{subject_name}</h3>
        <p style="color:#64748b; margin:10px 0;">Code : <span style="background:#E0E3FF; color:#5865F2; padding:2px 8px; border-radius:5px;">{subject_code} </span> | Division : {division} | Subject ID :{subject_id}</p>
        
        """
    
    if stats:
        html+= """
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
        """
        for icon, label, value in stats:
            html+= f'<div style="background: #EB459E10; padding:5px 12px; border-radius:12px; font-size:0.9rem">{icon} <b>{value}</b> {label} </div>'
        
        html+= "</div>"

    st.markdown(html, unsafe_allow_html=True)
    footer_callback(subject_name,subject_id,subject_code,user_id)
    