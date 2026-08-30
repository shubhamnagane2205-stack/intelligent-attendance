import streamlit as st
from src.ui.base_layout import style_background_dashboard,base_layout
from src.components.header import dashboard_header
from src.database.db import check_teacher_exists,create_teacher,validate_login
import time
from src.components.create_subject_dialog import create_subject_dialog
from src.database.db import get_teacher_subjects,get_attendance_records
from src.components.subject_card import subject_card,share_button
from src.components.add_photos_dialog import add_photos_dialog
import numpy as np
import pandas as pd
from src.pipelines.face_pipeline import predict_attendance_face
from src.database.config import supabase
from datetime import datetime
from src.components.attendance_result_dialog import attendance_result_dialog
from src.components.use_voice_recognition_dialog import use_voice_recognition



def teacher_screen():    
    style_background_dashboard()
    base_layout()
    if 'teacher_data' in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=='login':
        teacher_login_screen()
    elif st.session_state.teacher_login_type=='register':
        teacher_register_screen()



def teacher_tab_take_attendance():
    teacher_id=st.session_state.teacher_data["teacher_id"]
    st.header('Take Attendance with AI')
    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []
    try:
        subjects=get_teacher_subjects(teacher_id)
    except Exception:
        subjects=[]
        st.toast("Unable to fetch data. Please try again.")
    if not subjects:
        st.warning('No subjects yet! Create a subject to get started.')
        return
    subject_options={f"{subject['subject_name']}-{subject['subject_code']}":subject['subject_id'] for subject in subjects}
    col1,col2=st.columns([3,1],vertical_alignment='bottom')

    with col1:
        selected_subject=st.selectbox('Select Subject',options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos',type='primary',width='stretch',icon=':material/photo_prints:'):
            add_photos_dialog()

    st.divider()

    selected_subject_id=subject_options[selected_subject]


    if st.session_state.attendance_images:
        st.header("Added Photos")
        cols=st.columns(4)
        for i,image in enumerate(st.session_state.attendance_images):
            with cols[i%4]:
                st.image(image,width='stretch',caption=f"Photo {i+1}")
    col1,col2,col3=st.columns(3)
    has_photos=bool(st.session_state.attendance_images)
    with col1:
        if st.button("Clear All Photos",width='stretch',disabled=not has_photos,type='tertiary',icon=":material/delete:"):
            st.session_state.attendance_images=[]
            st.rerun()

    with col2:
        if st.button('Analyze Photos',width='stretch',type='secondary',icon=":material/face:",disabled=not has_photos):
            try:
                response=supabase.table("student_subjects").select('*,students(*)').eq('subject_id',selected_subject_id).execute()
                enrolled_students=response.data
            except:
                enrolled_students=[]
                st.toast("Unable to fetch data. Please try again.")
            if not enrolled_students:
                st.warning("No students are enrolled in this subject.")
            else:
                with st.spinner("Identifying students in classroom photos..."):
                    all_detected_ids={}

                    for idx,img in enumerate(st.session_state.attendance_images):
                        img_np=np.array(img.convert('RGB'))
                        detected_students,no_of_students=predict_attendance_face(img_np)

                        if detected_students:
                            for student_id in detected_students.keys():
                                student_id=int(student_id)
                                all_detected_ids.setdefault(student_id,[]).append(f"Photo {idx+1}")
                    results,attendance_to_log=[],[]
                    current_timestamp=datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    for node in enrolled_students:
                        student=node['students']
                        source=all_detected_ids.get(int(student['student_id']),[])
                        is_present=bool((source))

                        results.append({
                            'Student Name':student['name'],
                            'Student ID':student['student_id'],
                            'Detected In':", ".join(source) if is_present else '-',
                            'Attendance':"✅ Present" if is_present else "❌ Absent"
                        })
                        attendance_to_log.append(
                            {
                                'timestamp':current_timestamp,
                                'subject_id':selected_subject_id,
                                'student_id':student['student_id'],
                                'is_present':is_present
                            }
                        )
                    attendance_result_dialog(pd.DataFrame(results),attendance_to_log)

    with col3:
        if st.button('Use Voice Recognition',type='primary',width='stretch',icon=':material/mic:'):
            use_voice_recognition(selected_subject_id)




            
def teacher_tab_manage_subjects():
    teacher_id=st.session_state.teacher_data['teacher_id']
    col1,col2=st.columns(2)
    with col1:
        st.header('Manage Subjects',width='stretch')
    with col2:
        if st.button('Create New Subject',width='stretch'):
            create_subject_dialog(teacher_id)
    try:
        subjects=get_teacher_subjects(teacher_id)
    except Exception:
        subjects=[]
        st.toast("Unable to fetch data. Please try again.")

    if subjects:
        for sub in subjects:
            stats=[
                ("🫂",'Students',sub['total_students']),
                ('🕰️','Classes',sub['total_classes'])
                
            ]
            subject_card(

                subject_name=sub['subject_name'],
                subject_code=sub['subject_code'],
                division=sub['division'],
                stats=stats,
                subject_id=sub['subject_id'],
                footer_callback=share_button
                
            )

            st.space()



    else:
        st.info("No Subject Found! ")    

        

def teacher_tab_attendance_records():
    st.header('Attendance Records')
    teacher_id=st.session_state.teacher_data["teacher_id"]
    try:
        subjects=get_teacher_subjects(teacher_id)
    except Exception:
        subjects=[]
        st.toast("Unable to fetch data. Please try again.")
    
    if not subjects:
        st.warning('No subjects yet! Create a subject to get started.')
        return
    subject_options={f"{subject['subject_name']}-{subject['subject_code']}":subject['subject_id'] for subject in subjects}
    col1,col2=st.columns([3,1])

    with col1:
        selected_subject=st.selectbox('Select Subject',options=list(subject_options.keys()))
    with col2:
        df=None
        if st.button("View Attendance Records"):
            with st.spinner(f"Fetching attendance records for {selected_subject}..."):
                selected_subject_id=subject_options[selected_subject]
                try:
                    all_records=get_attendance_records(selected_subject_id)
                    result={}

                    if not all_records:
                        st.info(f"No attendance records found for {selected_subject}.")
                        return
                    for log in all_records:
                        student=log['students']
                        stud_record=result.setdefault(student['student_id'],{})
                        stud_record['Name']=student['name']
                        time_stamp=log.get('timestamp')
                        time_stamp=datetime.fromisoformat(time_stamp).strftime("%Y-%m-%d %I:%M %p") if time_stamp else "N/A"
                        is_present=bool(log.get('is_present'))
                        stud_record[f'{time_stamp}']="✅ Present" if is_present else "❌ Absent"

                    df=pd.DataFrame.from_dict(result,orient='index')
                    df=df.reset_index(drop=True).fillna('Not Enrolled')
                    

                except Exception as e:
                    st.write(str(e))
                    st.error('Unexpected Error!')   
    if df is not None:
        st.subheader(f"Attendance Records — {selected_subject}")
        st.dataframe(df, width="stretch")
    
        




def teacher_login(username,password):
    if not username or not password:
        return False,"All fields are required"
    try:
        teacher=validate_login(username,password)
    except Exception as e:
        teacher=None
    if teacher:
        st.session_state.teacher_data=teacher
        st.session_state.user_type='teacher'
        st.session_state.is_logged_in=True
        return True,"Welcome back!"
    return False,"Invalid username or password, or a server error occurred."

    

def create_account(username,name,password,conf_password):
    if not username or not name or not password or not conf_password:
        return False,"All Fields Are Required!"
    if password!=conf_password:
        return False,"Passwords do not match"
    try:
        if check_teacher_exists(username):
            return False,"This username is already taken. Please choose another one."
    except Exception:
        return False,"Unexpected Error"
    try:
        create_teacher(username,name,password)
        return True,'Registration successful! You can now log in.'

    except Exception as e:
        return False,'Unexpected Error'




def teacher_dashboard():
    teacher_data=st.session_state.teacher_data

    col1,col2=st.columns(2,gap="xxlarge",vertical_alignment='center')
    with col1:
        dashboard_header()
    
    with col2:
        st.subheader(f"Welcome back {teacher_data['teacher_name']}")
        
        
        if st.button('Logout',shortcut="control+backspace"):
            st.session_state.is_logged_in=False
            del st.session_state.teacher_data
            st.rerun()

    if 'current_teacher_tab' not in st.session_state:
        st.session_state.current_teacher_tab='take_attendance'
    tab1,tab2,tab3=st.columns(3)
    with tab1:
        type='primary' if st.session_state.current_teacher_tab=='take_attendance' else 'tertiary'
        if st.button('Take Attendance',width='stretch',icon=':material/ar_on_you:',type=type):
            st.session_state.current_teacher_tab='take_attendance'
            st.rerun()

    with tab2:
        type='primary' if st.session_state.current_teacher_tab=='manage_subjects' else 'tertiary'
        if st.button('Manage Subjects',width='stretch',icon=':material/book_ribbon:',type=type):
            st.session_state.current_teacher_tab='manage_subjects'
            st.rerun()
    with tab3:
        type='primary' if st.session_state.current_teacher_tab=='attendance_records' else 'tertiary'
        if st.button('Attendance Records',width='stretch',icon=':material/cards_stack:',type=type):
            st.session_state.current_teacher_tab='attendance_records'
            st.rerun()

    st.divider()


    match st.session_state.current_teacher_tab:

        case 'take_attendance':
            teacher_tab_take_attendance()
        case 'manage_subjects':
            teacher_tab_manage_subjects()
        case 'attendance_records':
            teacher_tab_attendance_records()


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
    username=st.text_input('Enter Username',placeholder='Abhay@9922')
    password=st.text_input("Enter Password",placeholder="AS@#%^$356",type='password')
    st.divider()
    bt1,bt2=st.columns(2)
    with bt1:
        if st.button("Login",width='stretch',shortcut='control+enter',icon=':material/passkey:'):
            success,message=teacher_login(username,password)
            if success:
                st.toast(message+f'{st.session_state.teacher_data['teacher_name']}',icon="👋")
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
        username=st.text_input('Enter Username',placeholder='Abhay@9922')
        name=st.text_input('Enter name',placeholder='Abhay')
            
        password=st.text_input("Enter Password",placeholder="As@7#$2",type='password')
        conf_password=st.text_input("Confirm Password",placeholder="As@7#$2",type='password')
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
        
    

    