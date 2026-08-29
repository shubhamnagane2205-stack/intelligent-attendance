import streamlit as st
import time
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

def clear_query_params():
    st.query_params.clear()

@st.dialog('Quick Enrollment',on_dismiss=clear_query_params)
def auto_enroll_dialog(subject_id):
    
    try:
        response=supabase.table('subjects').select('*').eq("subject_id",subject_id).execute()
    except Exception as e:
        st.error("Unexpected Error!")
        time.sleep(1)
        st.query_params.clear()
        st.rerun()

       
    if response.data:
        subject=response.data[0]
        student_id=st.session_state.student_data['student_id']
        try:
            check=supabase.table('student_subjects').select('*').eq('subject_id',subject_id).eq('student_id',student_id).execute()
            if check.data:
                st.info("You Are Already Enrolled For This Program!")
                if st.button('Got It'):
                
                    st.query_params.clear()
                    st.rerun()
                

            else:
                st.markdown(f'Would you like to enroll in **{subject['subject_name']}**?')
                col1,col2=st.columns(2)
                with col1:
                    if st.button('No thanks'):
                        st.query_params.clear()
                        st.rerun()
                with col2:
                    if st.button("Yes Enroll Now",type='primary',width='stretch'):
                        suc=enroll_student_to_subject(subject_id,student_id)
                        if suc:
                            st.info(f"You're now enrolled in {response.data[0].get('subject_name')}! 🎉")
                            st.query_params.clear()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Try again later.")
                            st.query_params.clear()
                            time.sleep(1)
                            st.rerun()

        except Exception as e:
            
            st.error("Unexpected Error!")
            st.query_params.clear()
            time.sleep(1)
            st.rerun()
    else:
        st.info(f"No subject found with ID: {subject_id}. Please check the ID or try again later.")
        if st.button("Close"):
            st.query_params.clear()
            
            st.rerun()


