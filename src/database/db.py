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
    students=get_all_students()
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
