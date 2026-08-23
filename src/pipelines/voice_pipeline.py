import streamlit as st
from resemblyzer import VoiceEncoder,preprocess_wav
import librosa
import io
import numpy as np
from src.database.db import get_students_with_emb


@st.cache_resource
def get_encoder():
    return VoiceEncoder()

def voice_encoder(audio_bytes):
    try:
        encoder=get_encoder()
        waveform,sr=librosa.load(io.BytesIO(audio_bytes.getvalue()),sr=16000)
        transformed_waveform=preprocess_wav(waveform)
        return encoder.embed_utterance(transformed_waveform).tolist()

    except Exception as e:
    
        return None


def check_resemblance_voice(database_embeddings,query_embedding,student_ids,resemblance_threshold=0.65):
    scores=np.dot(database_embeddings,query_embedding)
    idx=np.argmax(scores)

    if scores[idx]>=resemblance_threshold:
        return student_ids[idx],scores[idx] #Best Score

    return None,scores[idx]

def predict_attendance_voice(audio_bytes):

    try:
        encoder=get_encoder()
        waveform,sr=librosa.load(io.BytesIO(audio_bytes),sr=16000)
        segments=librosa.effects.split(waveform,top_db=30)

        detected_students={}
        database_embeddings,student_ids=get_students_with_emb('V')
        if len(student_ids)==0:
            return {}
        for start,end in segments:
            if (end-start)>16000*0.5:
                seg=waveform[start:end]
                
                pre_seg=preprocess_wav(seg)
                if(len(pre_seg))==0:
                    continue
                query_embedding=encoder.embed_utterance(pre_seg)

                sid,score=check_resemblance_voice(database_embeddings,query_embedding,student_ids)

                if sid is not None:
                    if sid not in detected_students or detected_students[sid]<score:
                        detected_students[sid]=score

        return detected_students
    except Exception as e:
        st.error("Audio processing error!")
        return {}



