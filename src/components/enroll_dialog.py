import streamlit as st
from src.database.config import supabase
import time
from src.database.db import enroll_student_to_subject

@st.dialog('Enroll in Subject')
def enroll_dialog():
    st.write("Enter the Subject ID provided by your teacher to enroll.")
    subject_id=st.text_input('Subject ID',placeholder="4")
    if st.button("Enroll",type='primary',width='stretch'):
        if subject_id:
            try:
                response=supabase.table('subjects').select('*').eq("subject_id",subject_id).execute()
            except Exception as e:
                response=None
            if response.data:
                student_id=st.session_state.student_data['student_id']
                try:
                    check=supabase.table('student_subjects').select('*').eq('subject_id',subject_id).eq('student_id',student_id).execute()
                    if check.data:
                        st.info("You Are Already Enrolled For This Program!")
                        

                    else:
                        suc=enroll_student_to_subject(subject_id,student_id)
                        if suc:
                            st.toast(f"You're now enrolled in {response.data[0].get('subject_name')}! 🎉")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Try again later.")

                except Exception as e:
                    st.error(str(e))
                    st.error("Unexpected Error!")
            else:
                st.info(f"No subject found with ID: {subject_id}. Please check the ID or try again later.")
        else:
            st.warning("Please enter a Subject ID")

                    


            


