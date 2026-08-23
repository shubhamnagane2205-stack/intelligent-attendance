import streamlit as st
import streamlit as st
from src.ui.base_layout import style_background_dashboard,base_layout
from src.components.header import dashboard_header
from PIL import Image
import numpy as np
from src.pipelines.face_pipeline import predict_attendance_face,get_face_embeddings
from src.pipelines.voice_pipeline import voice_encoder
from src.database.db import get_all_students,create_student
import time


def student_dashboard():
    st.header('Student Dashboard')
    
    

def student_screen():

    if 'student_data' in st.session_state:
        student_dashboard()
        return 

    style_background_dashboard()
    base_layout()

    col1,col2=st.columns(2,vertical_alignment='center',gap="xxlarge")
    with col1:
        dashboard_header()
    with col2:
        if st.button("Go back to home",shortcut="control+backspace"):
            st.session_state.login_type=None
            st.rerun()

    st.header("Login using FaceId",text_alignment='center')

    st.space()
    st.space()

    img=st.camera_input("Position your face in the center")
    
    if 'show_registration' not in st.session_state :
        if img:
            img_np=np.array(Image.open(img))
            with st.spinner("AI is scanning...."):
                detected_student,n_students=predict_attendance_face(img_np)
                if n_students==0:
                    st.warning("No face detected")

                elif n_students>1:
                    st.warning("Multiple faces detected")
                
                else:
                    if detected_student:
                        student_id=list(detected_student.keys())[0]
                        all_students=get_all_students()
                        student=next((student for student in all_students if student['student_id']==student_id))

                    
                        st.session_state.is_logged_in=True
                        st.session_state.user_type="student"
                        st.session_state.student_data=student

                        st.toast(f"Welcome back {student.get('name')}")
                        time.sleep(1)
                        st.rerun()
                    

                    else:
                        st.info("Face not recognized. You might be a new student!")
                        st.session_state.show_registration=True
    if 'show_registration' in st.session_state:
        
        with st.container(border=True):
            st.header("Register new profile")

            new_name=st.text_input("Enter your name",placeholder='E.g Raj Nagane')
            st.subheader("Optional: Voice Enrollement")
        

            audio_bytes=None
            try:
                audio_bytes=st.audio_input("Record a short phrase like I am present, My name is Bhushan")
            except Exception:
                st.error("Unable to access your microphone. Try again")

            if st.button("Create Account",type='primary'):
                if new_name is not None and img is not None:
                    with st.spinner("Creating a profile"):
                        img_np=np.array(Image.open(img))
                        face_embedding=get_face_embeddings(img_np)

                        if face_embedding.shape[0]==1:
                            face_embedding=face_embedding[0].tolist()
                            if audio_bytes:
                                voice_embedding=voice_encoder(audio_bytes)
                                if voice_embedding:
                                    response=create_student(new_name,face_embedding,voice_embedding).data
                                    if response:
                                        student_created(response,new_name)

                                    else:
                                        st.error("Could not save your profile to the database. Please try again.")
                                else:
                                    st.error('Failed to encode your voice. Please record a clear 3–5 second phrase and try again.')




                            else:
                                response=create_student(new_name,face_embedding).data
                                if response:
                                    student_created(response,new_name)
                                else:
                                    st.error("Could not save your profile to the database. Please try again.")

                        elif(face_embedding.shape[0]>1):
                            st.warning("Multiple faces detected. Please recapture photo with one face only.")          
                        else:

                            st.error("Failed to capture facial features. Please recapture the photo with your face clearly visible.")

                else:
                    st.warning("Name and Picture both are required fields!")
        


def student_created(response,new_name):
    get_all_students.clear()
    st.session_state.user_type='student'
    st.session_state.is_logged_in=True
    st.session_state.student_data=response[0]
    st.toast(f"Profile created Hi {new_name}!")
    time.sleep(1)
    st.rerun()
