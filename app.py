# app.py
import streamlit as st
from supabase import create_client, Client
from io import BytesIO

# --- CONFIGURACIÓN SUPABASE ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# --- FUNCIONES ---
def get_buckets():
    response = supabase.storage.list_buckets()
    return [b["name"] for b in response]

def get_files(bucket: str):
    try:
        response = supabase.storage.from_(bucket).list()
        return [f["name"] for f in response]
    except Exception:
        return []

def upload_file(bucket: str, file):
    try:
        file_data = BytesIO(file.getvalue())
        supabase.storage.from_(bucket).upload(
            file.name,
            file_data,
            file_options={"cache-control": "3600", "upsert": "false"},
        )
        return True
    except Exception as e:
        st.error(f"Error al subir archivo: {e}")
        return False

# --- UI STREAMLIT ---
st.title("📦 Gestor de archivos en Supabase")

# Guardar bucket seleccionado en session_state
if "bucket" not in st.session_state:
    st.session_state["bucket"] = None

# 1. Mostrar buckets
buckets = get_buckets()
selected_bucket = st.selectbox("Selecciona un bucket:", buckets, index=buckets.index(st.session_state["bucket"]) if st.session_state["bucket"] in buckets else 0)
st.session_state["bucket"] = selected_bucket

# 2. Mostrar lista de archivos
st.subheader(f"Archivos en: {selected_bucket}")
files = get_files(selected_bucket)
if files:
    st.write(files)
else:
    st.info("No hay archivos en este bucket.")

# 3. Subir archivo
st.subheader("Subir nuevo archivo")
uploaded_file = st.file_uploader("Selecciona un archivo para subir", type=None)

if uploaded_file:
    if st.button("Guardar archivo en Supabase"):
        with st.spinner("Subiendo archivo..."):
            if upload_file(selected_bucket, uploaded_file):
                st.success(f"✅ Archivo '{uploaded_file.name}' subido correctamente.")
                st.rerun()  # Recargar para ver nueva lista

