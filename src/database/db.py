from src.database.config import supabase
import bcrypt as bc
import numpy as np

import streamlit as st

def hash_pass(password):
    return bc.hashpw(password.encode(),bc.gensalt()).decode()

def check_pass(password,stored_hash):
    return bc.checkpw(password.encode(),stored_hash.encode())


def check_teacher_exists(username):
    response=supabase.table('teachers').select('teacher_username').eq('teacher_username',username).execute()
    return (len(response.data)>0)

def create_teacher(username,name,password):
    data={'teacher_username':username,'teacher_password':hash_pass(password),'teacher_name':name}
    response=supabase.table('teachers').insert(data).execute()
    return response

def validate_login(username,password):
    response=supabase.table('teachers').select('*').eq('teacher_username',username).execute()
    if response.data:
        teacher=response.data[0]
        if check_pass(password,teacher['teacher_password']):
            return teacher

    return None

def create_student(name,face_embedding,voice_embedding=None):
    data={"name":name,'face_embedding':face_embedding,'voice_embedding':voice_embedding}
    response=supabase.table('students').insert(data).execute()
    return response

@st.cache_data
def get_all_students():
    
    return supabase.table('students').select('*').execute().data
    
    
def get_students_with_emb(emb_type='F'):
    try:
        students=get_all_students()
    except Exception:
        students=[]
        st.toast("Unable to fetch students. Please try again.")
    face_embeddings=[]
    voice_embeddings=[]
    student_ids=[]
    if emb_type=="F":
        for student in students:
            if student.get('face_embedding') is not None:
                face_embeddings.append(student.get('face_embedding'))
                student_ids.append(student.get('student_id'))
        return np.array(face_embeddings,dtype=np.float32),np.array(student_ids)

    if emb_type=='V':
        for student in students:
            if student.get('voice_embedding') is not None:
                voice_embeddings.append(student.get('voice_embedding'))
                student_ids.append(student.get('student_id'))    

        return np.array(voice_embeddings,dtype=np.float32),np.array(student_ids)


def check_subject_exists(subject_name,subject_code,class_,division,teacher_id):

    response=supabase.table("subjects").select("subject_id").eq("subject_name",subject_name).eq("subject_code",subject_code).eq("class",class_).eq("division",division).eq("teacher_id",teacher_id).execute()
    return(bool(response.data))

def create_subject(subject_name,subject_code,class_,division,teacher_id):
    response=supabase.table('subjects').insert({'subject_name':subject_name,'subject_code':subject_code,'class':class_,"division":division,'teacher_id':teacher_id}).execute()
    return(bool(response.data))

def get_teacher_subjects(teacher_id):
    response=supabase.table("subjects").select("*,student_subjects(count),attendance_logs(timestamp)").eq("teacher_id",teacher_id).execute()
    subjects=response.data
    for sub in subjects:
        student_count=sub.get('student_subjects') or [{}]
        sub["total_students"]=student_count[0].get('count',0)
        unique_sessions=sub.get('attendance_logs') or []
        unique_sessions=len(set(log['timestamp'] for log in unique_sessions))
        sub['total_classes']=unique_sessions

        sub.pop('student_subjects',None)
        sub.pop('attendance_logs',None)
    return subjects


def enroll_student_to_subject(subject_id,student_id):
    data={"subject_id":subject_id,"student_id":student_id}
    response=supabase.table('student_subjects').insert(data).execute()
    return bool(response.data)

def unenroll_student_from_subject(subject_id,student_id):
    response=supabase.table('student_subjects').delete().eq("student_id",student_id).eq("subject_id",subject_id).select().execute()
    return bool(response.data)

def get_student_subjects(student_id):
    response=supabase.table("student_subjects").select("*",'subjects(*)').eq('student_id',student_id).execute()
    return response.data

def get_student_attendance(student_id):
    response=supabase.table('attendance_logs').select('*','subjects(*)').eq('student_id',student_id).execute()
    return response.data

def create_attendance(logs):
    response = supabase.table('attendance_logs').insert(logs).execute()
    return response.data

def get_attendance_records(selected_subject_id):
    response=supabase.table('attendance_logs').select('*,students(*)').eq('subject_id',selected_subject_id).execute()
    return response.data