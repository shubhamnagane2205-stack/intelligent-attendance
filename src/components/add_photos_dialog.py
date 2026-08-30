import streamlit as st
import time
from PIL import Image

@st.dialog("Add Classroom Photos")
def add_photos_dialog():
    st.write('Capture or upload photos of the classroom to take attendance.')

    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab='camera'

    tab1,tab2=st.columns(2)

    with tab1:
        type='primary' if st.session_state.photo_tab=='camera' else 'tertiary'
        if st.button('Camera',type=type,width='stretch'):
            st.session_state.photo_tab='camera'
            st.rerun(scope='fragment')
    with tab2:
        type='primary' if st.session_state.photo_tab=='upload' else 'tertiary'
        if st.button("Upload Photos",type=type,width='stretch'):
            st.session_state.photo_tab='upload'
            st.rerun(scope='fragment')
    if st.session_state.photo_tab=='camera':
        class_photo=st.camera_input("Take a snapshot",key='dialog_cam')
        if class_photo:
            st.session_state.attendance_images.append(Image.open(class_photo))
            st.toast("Photo captured successfully!")
            time.sleep(0.5)
            st.rerun()

    if st.session_state.photo_tab=='upload':
        uploaded_files=st.file_uploader(
        "Upload classroom photos",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True,
        key="dialog_upload")
        if uploaded_files:
            for file in uploaded_files:
                st.session_state.attendance_images.append(Image.open(file))
            st.toast("Photos uploaded successfully!")
            time.sleep(0.5)
            st.rerun()
        

        