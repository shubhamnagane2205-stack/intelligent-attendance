import streamlit as st
from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
from src.components.auto_enroll_dialog import auto_enroll_dialog
def main():


    st.set_page_config(
        page_title="Intelligent Attendance",
        page_icon='https://i.ibb.co/YTYGn5qV/logo.png'
    )
   
    if 'login_type' not in st.session_state:
        st.session_state.login_type=None
    
    match st.session_state.login_type:

        case 'teacher':
            teacher_screen()
        case 'student':
            student_screen()
        case None:
            home_screen()

    subject_id=st.query_params.get('join-code')
    if subject_id:
        if st.session_state.login_type!='student':
            st.session_state.login_type='student'
            st.rerun()
        if st.session_state.get('is_logged_in') and st.session_state.get('user_type')=='student':
            auto_enroll_dialog(subject_id)
main()