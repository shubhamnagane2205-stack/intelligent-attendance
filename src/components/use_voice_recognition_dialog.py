import streamlit as st
import pandas as pd
from src.database.config import supabase
from src.pipelines.voice_pipeline import predict_attendance_voice
from src.components.attendance_result_dialog import show_attendance_results
from datetime import datetime
@st.dialog("Voice Attendace")
def use_voice_recognition(selected_subject_id):
    st.write('Ask students to say **“I am present.”** AI will recognize each student by their voice.')
    audio_input=st.audio_input('Record Audio')

    if st.button("Analyze Audio",type='primary',width='stretch',disabled= not audio_input):
        try:
            response=supabase.table("student_subjects").select('*,students(*)').eq('subject_id',selected_subject_id).execute()
            enrolled_students=response.data
        except Exception as e:
            st.error("Unexpected Error!")
            return
        
        if not response.data:
            st.warning("No students are enrolled in this subject.")
            st.session_state.voice_attendance_results=None
        else:
            
            with st.spinner("Analyzing audio..."):
                
                candidate_dict={student['students'].get('student_id'):student['students'].get('voice_embedding') for student in enrolled_students if student['students'].get('voice_embedding')}
                if not candidate_dict:
                    st.error("No enrolled students have registered voice profiles.")
                    st.session_state.voice_attendance_results=None
                    return
                detected_students=predict_attendance_voice(audio_input.read())
                current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                attendance_to_log=[]
                results=[]
                for node in enrolled_students:
                    student=node['students']
                    score=detected_students.get(student['student_id'],0)
                    is_present=(score>0)

                    results.append({
                    'Student Name':student['name'],
                    'Student ID':student['student_id'],
                    'Score':score if is_present else '-',
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
                
                st.session_state.voice_attendance_results = (pd.DataFrame(results), attendance_to_log)


    if st.session_state.get('voice_attendance_results'):    
        st.divider()       
        df_results, logs = st.session_state.voice_attendance_results     
        show_attendance_results(df_results, logs)





    