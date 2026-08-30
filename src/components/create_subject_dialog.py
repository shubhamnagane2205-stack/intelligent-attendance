import streamlit as st
from src.database.db import create_subject,check_subject_exists
import time

@st.dialog("Create Subject")
def create_subject_dialog(teacher_id):
    st.write("Details of the new subject")
    subject_name=st.text_input("Subject Name",placeholder="Introduction To Mathematical Analysis")
    subject_code=st.text_input("Subject Code",placeholder='MA001')
    class_=st.text_input("Class",placeholder="TY-Mech")
    division=st.text_input("Division",placeholder="A")
    if st.button('Create Subject'):
        if subject_name and subject_code and class_ and division:
            exists=None
            try:
                exists=check_subject_exists(subject_name,subject_code,class_,division,teacher_id)
            except Exception as e:
                st.info("Unexpected Error!")
            if exists:
                st.warning("Subject already exists!")
            if exists is not None and not exists:
                try:
                    created=create_subject(subject_name,subject_code,class_,division,teacher_id)
                    if created:
                        st.toast("Subject Created Succesfully")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.info("Unexpected Error2!")
                except Exception as e:
                    st.info(str(e))
        else:
            st.warning("All fields are required!")