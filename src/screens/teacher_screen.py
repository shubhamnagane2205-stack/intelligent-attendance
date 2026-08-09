import streamlit as st
from src.ui.base_layout import style_background_dashboard,base_layout
from src.components.header import dashboard_header
def teacher_screen():    
    style_background_dashboard()
    base_layout()
    if 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=='login':
        teacher_login()
    elif st.session_state.teacher_login_type=='register':
        teacher_register()




def teacher_login():    

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
        st.button("Login",width='stretch',shortcut='control+enter',icon=':material/passkey:')
    with bt2:
        if st.button("Register Instead",type='primary',width='stretch'):
            st.session_state.teacher_login_type='register'
            st.rerun()

def teacher_register():
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
            st.button('Register',icon=':material/passkey:',width='stretch')
        with bt2:
            if st.button("Login Instead",width="stretch",type='primary'):
                st.session_state.teacher_login_type='login'
                st.rerun()
        
    

    