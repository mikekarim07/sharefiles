import streamlit as st
from supabase import create_client, Client
import os
from datetime import datetime
import tempfile

# Configuración de Supabase (usa secrets en producción)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "TU_SUPABASE_URL_AQUI")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "TU_ANON_KEY_AQUI")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Nombre del bucket en Supabase
BUCKET_NAME = "uploads"

# Título de la app
st.title("🚀 Subir Archivos Seguros a Supabase")
st.write("Sube tus archivos aquí (máx. ~40MB). Una vez cargados, verás la lista abajo para confirmar qué se ha subido.")

# Widget de upload múltiple
uploaded_files = st.file_uploader(
    "Elige archivos para subir",
    type=["pdf", "docx", "xlsx", "txt", "jpg", "png"],
    accept_multiple_files=True,
    help="Archivos entre 20-40MB. Puedes subir varios a la vez."
)

# Subir archivos si hay uploads
if uploaded_files:
    with st.spinner("Subiendo archivos a Supabase..."):
        for uploaded_file in uploaded_files:
            if uploaded_file is not None:  # Verifica que el archivo no sea None
                try:
                    # Usar directorio temporal seguro
                    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_file_path = tmp_file.name

                    # Subir a Supabase Storage
                    with open(tmp_file_path, "rb") as f:
                        res = supabase.storage.from_(BUCKET_NAME).upload(
                            path=uploaded_file.name,
                            file=f
                        )

                    # Limpiar archivo temporal
                    os.unlink(tmp_file_path)

                    if res.status_code == 200:
                        st.success(f"✅ {uploaded_file.name} subido correctamente.")
                    else:
                        st.error(f"❌ Error subiendo {uploaded_file.name}: {res.text}")
                except Exception as e:
                    st.error(f"❌ Error procesando {uploaded_file.name}: {str(e)}")
            else:
                st.warning("⚠️ Uno de los archivos no es válido. Por favor, revisa la selección.")
    
    st.rerun()  # Recarga para actualizar la lista

# Listar archivos en el bucket
st.subheader("📁 Archivos Subidos")
try:
    files = supabase.storage.from_(BUCKET_NAME).list()
    
    if not files:
        st.info("Aún no hay archivos subidos. ¡Sube el primero!")
    else:
        file_data = []
        for file_info in files:
            if file_info.get('name') and file_info['name'] != '.gitkeep':
                try:
                    # Obtener metadata del archivo
                    metadata = supabase.storage.from_(BUCKET_NAME).download(file_info['name'])
                    size_mb = len(metadata) / (1024 * 1024)
                    created_at = datetime.fromisoformat(
                        file_info.get('created_at', '1970-01-01T00:00:00Z').replace('Z', '+00:00')
                    )
                    
                    file_data.append({
                        'Nombre': file_info['name'],
                        'Tamaño (MB)': f"{size_mb:.2f}",
                        'Fecha de Carga': created_at.strftime("%d/%m/%Y %H:%M")
                    })
                except Exception as e:
                    st.warning(f"⚠️ No se pudo obtener info de {file_info['name']}: {str(e)}")
        
        if file_data:
            st.table(file_data)
        else:
            st.info("No hay archivos válidos para mostrar.")
            
        # Botón para descargar todos (admin)
        if st.button("📥 Descargar Todos los Archivos (para el admin)"):
            st.warning("En producción, usa el dashboard de Supabase para descargar.")
            st.markdown(f"[Descargar desde Supabase Dashboard](https://supabase.com/dashboard/project/{SUPABASE_URL.split('//')[1].split('.')[0]}/storage/buckets/{BUCKET_NAME})")
            
except Exception as e:
    st.error(f"Error al listar archivos: {str(e)}. Verifica que el bucket '{BUCKET_NAME}' exista y sea público.")

# Pie de página
st.markdown("---")
st.caption("App creada con ❤️ por Grok. Contacta si necesitas ajustes.")
