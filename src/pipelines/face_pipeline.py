
import dlib
import face_recognition_models
import streamlit as st
import numpy as np
from src.database.db import get_students_with_emb

@st.cache_resource
def load_models():
    face_detector=dlib.get_frontal_face_detector()
    shape=dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )
    face_encoder=dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return face_detector,shape,face_encoder

def get_face_embeddings(img_np):
    face_detector,shape,face_encoder=load_models()
    faces=face_detector(img_np,1)
    embeddings=[]

    for face in faces:
        face_shape=shape(img_np,face)
        emb=face_encoder.compute_face_descriptor(img_np,face_shape)
        embeddings.append(np.array(emb,dtype=np.float32))
    return np.array(embeddings,dtype=np.float32)

def check_resemblance_face(database_embeddings,query_embedding,student_ids,resemblance_threshold=0.6):
    distances=np.linalg.norm(database_embeddings-query_embedding,axis=1)
    idx=np.argmin(distances)

    if distances[idx]<=resemblance_threshold:
        return student_ids[idx]
    return None


def predict_attendance_face(img_np):
    database_embeddings,student_ids=get_students_with_emb('F')
    query_embeddings=get_face_embeddings(img_np)
    if len(student_ids)==0:
        return {},len(query_embeddings)
    if len(query_embeddings)==0:
        return {},0
    detected_students={}
    for emb in query_embeddings:
        _id=check_resemblance_face(database_embeddings,emb,student_ids)
        if _id is not None:
            detected_students[_id]=True
    return detected_students,len(query_embeddings)



