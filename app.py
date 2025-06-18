import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import tempfile
import os

# 📂 Reemplaza por el ID de tu carpeta en Google Drive
FOLDER_ID = "10ZQjPf5cmva2uUqpSG8QR1uznGVnaL4O"

@st.cache_resource
def get_drive_service():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

drive_service = get_drive_service()

st.title("📤 Subir archivo Excel a Google Drive")

uploaded_file = st.file_uploader("Selecciona un archivo Excel", type=["xlsx", "xls"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    file_metadata = {
        "name": uploaded_file.name,
        "parents": [FOLDER_ID]
    }
    media = MediaFileUpload(temp_path, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    uploaded = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id, webViewLink"
    ).execute()

    os.remove(temp_path)

    st.success("✅ Archivo subido correctamente a Google Drive.")
    st.markdown(f"🔗 [Ver archivo en Drive]({uploaded['webViewLink']})")
