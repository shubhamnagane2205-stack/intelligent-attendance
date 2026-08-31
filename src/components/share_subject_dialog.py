import streamlit as st
import segno
import io

@st.dialog('Share class link')
def share_subject_dialog(subject_id):
    app_domain="intelligent-attendance-ai.streamlit.app"
    join_url=f'{app_domain}/?join-code={subject_id}'

    st.header('Scan to Join')
    QR=segno.make(join_url)

    out=io.BytesIO()
    QR.save(out,kind='png',scale=10,border=1)

    col1,col2=st.columns(2)
    with col1:
        st.markdown('### Copy Link')
        st.code(join_url,language='text')
        st.markdown('### Subject Id')
        st.code(subject_id,language='text')
        st.info('Copy this link to share on Whatsapp or Email')

    with col2:
        st.markdown("### Scan to Join")
        st.image(out.getvalue(),caption="QR-CODE for class joining")