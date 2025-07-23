# import streamlit as st
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# import tempfile
# import os
# from googleapiclient.http import MediaIoBaseUpload
# import io

# # 🟡 Reemplaza esto con el ID de tu carpeta en Google Drive
# FOLDER_ID = "10ZQjPf5cmva2uUqpSG8QR1uznGVnaL4O"

# # 📡 Conexión con Google Drive usando credenciales en st.secrets
# @st.cache_resource
# def get_drive_service():
#     creds = service_account.Credentials.from_service_account_info(
#         st.secrets["google_service_account"],
#         scopes=["https://www.googleapis.com/auth/drive"]
#     )
#     return build("drive", "v3", credentials=creds)

# drive_service = get_drive_service()

# # =============================
# # INTERFAZ DE USUARIO STREAMLIT
# # =============================
# st.title("📤 Cargar archivo Excel a Google Drive")

# uploaded_file = st.file_uploader(
#     "Selecciona un archivo", 
#     type=["xlsx", "xls", "csv", "txt", "zip"]
# )


# if uploaded_file:
#     # Crear archivo temporal
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
#         tmp.write(uploaded_file.read())
#         temp_path = tmp.name

#     # Crear metadatos para Drive
#     file_metadata = {
#         "name": uploaded_file.name,
#         "parents": [FOLDER_ID]
#     }

#     # media = MediaFileUpload(
#     #     temp_path,
#     #     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     # )
#     # Modificacion vs lineas anteriores
#     media = MediaIoBaseUpload(
#     io.FileIO(temp_path, 'rb'),
#     mimetype="application/octet-stream",
#     resumable=True
#     )
    
#     # Subir archivo a Google Drive
#     uploaded = drive_service.files().create(
#         body=file_metadata,
#         media_body=media,
#         fields="id, webViewLink"
#     ).execute()

#     # Borrar archivo temporal
#     os.remove(temp_path)

#     # Mensaje de éxito
#     st.success("✅ Archivo subido correctamente a Google Drive.")
#     # st.markdown(f"🔗 [Ver archivo en Drive]({uploaded['webViewLink']})")




import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import tempfile
import os

# 🟡 Reemplaza esto con el ID de tu carpeta en Google Drive
FOLDER_ID = "10ZQjPf5cmva2uUqpSG8QR1uznGVnaL4O"

# 📡 Conexión con Google Drive usando credenciales en st.secrets
@st.cache_resource
def get_drive_service():
    creds = service_account.Credentials.from_service_account_info(
        st.secrets["google_service_account"],
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    return build("drive", "v3", credentials=creds)

drive_service = get_drive_service()

# =============================
# INTERFAZ DE USUARIO STREAMLIT
# =============================
st.title("📤 Cargar archivo a Google Drive")

uploaded_file = st.file_uploader(
    "Selecciona un archivo",
    type=["xlsx", "xls", "csv", "txt", "zip"]
)

if uploaded_file:
    try:
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
            tmp.write(uploaded_file.read())
            temp_path = tmp.name

        # Metadatos para Drive
        file_metadata = {
            "name": uploaded_file.name,
            "parents": [FOLDER_ID]
        }

        # Preparar archivo para carga
        media = MediaFileUpload(
            temp_path,
            mimetype="application/octet-stream"
        )

        # Subir archivo
        uploaded = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()

        # Mostrar resultado
        st.success("✅ Archivo subido correctamente a Google Drive.")
        st.markdown(f"🔗 [Ver archivo en Drive]({uploaded['webViewLink']})")

    except Exception as e:
        st.error("❌ Ocurrió un error al subir el archivo.")
        st.exception(e)

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
