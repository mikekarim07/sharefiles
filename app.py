import streamlit as st
from supabase import create_client, Client
import os
from datetime import datetime

# Configuración de Supabase (usa secrets en producción)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "TU_SUPABASE_URL_AQUI")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "TU_ANON_KEY_AQUI")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Nombre del bucket en Supabase
BUCKET_NAME = "mars"

# Título de la app
st.title("🚀 Subir Archivos Seguros a Supabase")
st.write("Sube tus archivos aquí (máx. ~40MB). Una vez cargados, verás la lista abajo para confirmar qué se ha subido.")

# Widget de upload múltiple (para varios archivos a la vez)
uploaded_files = st.file_uploader(
    "Elige archivos para subir",
    type=["csv", "xlsx", "txt"],  # Ajusta los tipos si necesitas otros
    accept_multiple_files=False,
)

# Subir archivos si hay uploads
if uploaded_files:
    with st.spinner("Subiendo archivos a Supabase..."):
        for uploaded_file in uploaded_files:
            # Guardar archivo temporalmente
            file_path = f"/tmp/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Subir a Supabase Storage
            with open(file_path, "rb") as f:
                res = supabase.storage.from_(BUCKET_NAME).upload(
                    path=uploaded_file.name,  # Nombre del archivo en el bucket
                    file=f
                )
            
            # Limpiar archivo temporal
            os.remove(file_path)
            
            if res.status_code == 200:
                st.success(f"✅ {uploaded_file.name} subido correctamente.")
            else:
                st.error(f"❌ Error subiendo {uploaded_file.name}: {res.text}")
    
    st.rerun()  # Recarga la página para actualizar la lista

# Listar archivos en el bucket
st.subheader("📁 Archivos Subidos")
try:
    # Obtener lista de archivos del bucket
    files = supabase.storage.from_(BUCKET_NAME).list()
    
    if not files:
        st.info("Aún no hay archivos subidos. ¡Sube el primero!")
    else:
        # Preparar datos para la tabla
        file_data = []
        for file_info in files:
            if file_info['name'] != '.gitkeep':  # Ignora archivos dummy si los hay
                # Obtener metadata del archivo
                metadata = supabase.storage.from_(BUCKET_NAME).download(file_info['name'])
                size_mb = len(metadata) / (1024 * 1024)  # Tamaño en MB
                created_at = datetime.fromisoformat(file_info.get('created_at', '1970-01-01T00:00:00Z').replace('Z', '+00:00'))
                
                file_data.append({
                    'Nombre': file_info['name'],
                    'Tamaño (MB)': f"{size_mb:.2f}",
                    'Fecha de Carga': created_at.strftime("%d/%m/%Y %H:%M")
                })
        
        # Mostrar en tabla
        st.table(file_data)
        
        # Botón para descargar todos (opcional, para ti)
        if st.button("📥 Descargar Todos los Archivos (para el admin)"):
            st.warning("En producción, usa el dashboard de Supabase para descargar. Este botón es solo un ejemplo.")
            # Aquí podrías agregar lógica para generar un ZIP, pero para simplicidad, redirige al dashboard
            st.markdown(f"[Descargar desde Supabase Dashboard](https://supabase.com/dashboard/project/{SUPABASE_URL.split('//')[1].split('.')[0]}/storage/buckets/{BUCKET_NAME})")
            
except Exception as e:
    st.error(f"Error al listar archivos: {str(e)}. Verifica que el bucket '{BUCKET_NAME}' exista y sea público.")

# Pie de página
st.markdown("---")
st.caption("App creada con ❤️ por Grok. Contacta si necesitas ajustes.")
