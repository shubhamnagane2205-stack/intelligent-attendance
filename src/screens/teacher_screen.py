import streamlit as st
from src.ui.base_layout import style_background_dashboard,base_layout
from src.components.header import dashboard_header
from src.database.db import check_teacher_exists,create_teacher,validate_login
import time




def teacher_screen():    
    style_background_dashboard()
    base_layout()
    if 'teacher_data' in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=='login':
        teacher_login_screen()
    elif st.session_state.teacher_login_type=='register':
        teacher_register_screen()


def teacher_login(username,password):
    if not username or not password:
        return False,"All fields are required"
    teacher=validate_login(username,password)
    if teacher:
        st.session_state.teacher_data=teacher
        st.session_state.user_type='teacher'
        st.session_state.is_logged_in=True
        return True,"Welcome back!"
    return False,"Invalid username or password."

    

def create_account(username,name,password,conf_password):
    if not username or not name or not password or not conf_password:
        return False,"All Fields Are Required!"
    if password!=conf_password:
        return False,"Passwords do not match"
    if check_teacher_exists(username):
        return False,"This username is already taken. Please choose another one."
    try:
        create_teacher(username,name,password)
        return True,'Registration successful! You can now log in.'

    except Exception as e:
        return False,'Unexpected Error'




def teacher_dashboard():
    st.header(f"Welcome back {st.session_state.teacher_data['teacher_name']}")


def teacher_login_screen():    

    col1,col2=st.columns(2,gap="xxlarge",vertical_alignment='center')
    with col1:
        dashboard_header()

    with col2:
        if st.button('Go Back To Home',shortcut="control+backspace"):
            st.session_state.login_type=None
            st.rerun()
    st.header('Login using password')
    st.space()
    st.space()
    username=st.text_input('Enter Username',placeholder='Abhay@123')
    password=st.text_input("Enter Password",placeholder="YSM",type='password')
    st.divider()
    bt1,bt2=st.columns(2)
    with bt1:
        if st.button("Login",width='stretch',shortcut='control+enter',icon=':material/passkey:'):
            success,message=teacher_login(username,password)
            if success:
                st.toast(message,icon="👋")
                time.sleep(1)
                st.rerun()
            else:
                st.error(message)
            
    with bt2:
        if st.button("Register Instead",type='primary',width='stretch'):
            st.session_state.teacher_login_type='register'
            st.rerun()

def teacher_register_screen():
        col1,col2=st.columns(2,gap="xxlarge",vertical_alignment='center')
        with col1:
            dashboard_header()
    
        with col2:
            if st.button('Go Back To Home',shortcut="control+backspace"):
                st.session_state.login_type=None
                st.rerun()
        st.header('Register your teacher profile')
        st.space()
        st.space()
        username=st.text_input('Enter Username',placeholder='Abhay@123')
        name=st.text_input('Enter name',placeholder='Abhay')
            
        password=st.text_input("Enter Password",placeholder="YSM",type='password')
        conf_password=st.text_input("Conform Password",placeholder="YSM",type='password')
        st.divider()
        bt1,bt2=st.columns(2)
        with bt1:
            if st.button('Register',icon=':material/passkey:',width='stretch'):
                success,message=create_account(username,name,password,conf_password)
                if success:
                    st.success(message)
                    time.sleep(1)
                    st.session_state.teacher_login_type='login'
                    st.rerun()

                else:
                    st.error(message)
        with bt2:
            if st.button("Login Instead",width="stretch",type='primary'):
                st.session_state.teacher_login_type='login'
                st.rerun()
        
    

    