import streamlit as st
import logging
import sys
from pathlib import Path

# Adiciona o diretório ao path para importar o módulo
sys.path.insert(0, str(Path(__file__).parent))
from organizador_arquivos import extrair_e_organizar_zip, organizar_arquivos_upload

class StreamlitHandler(logging.Handler):
    """Handler customizado para exibir os logs na tela do Streamlit"""
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.log_text = ""

    def emit(self, record):
        msg = self.format(record)
        self.log_text += f"{msg}\n"
        self.placeholder.text(self.log_text)

def main():
    st.set_page_config(page_title="Organizador de NFs", page_icon="📁", layout="centered")

    st.title("📁 Organizador de Notas Fiscais e Boletos")
    st.write("Esta ferramenta organiza arquivos XML e PDF, agrupando-os por Chave da Nota Fiscal em pastas correspondentes.")

    # Abas para escolher o tipo de upload
    tab1, tab2 = st.tabs(["📦 Upload de Pasta (ZIP)", "📄 Upload Individual"])

    with tab1:
        st.subheader("Como usar:")
        st.markdown("""
        1. **Compacte sua pasta** com os documentos:
           - Windows: clique direito → Compactar em ZIP
           - Mac: clique direito → Compactar
        2. **Faça upload do ZIP** abaixo
        3. **Baixe o resultado** com os arquivos organizados
        """)

        uploaded_zip = st.file_uploader(
            "Selecione o arquivo ZIP com os documentos",
            type=["zip"],
            key="zip_upload"
        )

        if uploaded_zip:
            st.info(f"✅ Arquivo ZIP selecionado: {uploaded_zip.name}")

        if st.button("Organizar Arquivos do ZIP", type="primary", disabled=not uploaded_zip, key="btn_zip"):
            if not uploaded_zip:
                st.warning("Por favor, faça upload de um arquivo ZIP.")
                return

            st.success("Iniciando organização...")

            # Container para os logs
            st.subheader("📋 Logs da Execução")
            log_placeholder = st.empty()

            # Configura o logger
            logger = logging.getLogger("streamlit_logger_zip")
            logger.setLevel(logging.INFO)

            # Limpa os handlers antigos
            if logger.hasHandlers():
                logger.handlers.clear()

            sl_handler = StreamlitHandler(log_placeholder)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
            sl_handler.setFormatter(formatter)
            logger.addHandler(sl_handler)

            with st.spinner("Organizando os arquivos..."):
                try:
                    # Processa o ZIP e gera novo ZIP organizado
                    zip_content = extrair_e_organizar_zip(uploaded_zip, logger)

                    st.balloons()
                    st.success("✅ Organização concluída com sucesso!")

                    # Botão para download
                    st.subheader("📥 Download")
                    st.download_button(
                        label="⬇️ Baixar Arquivos Organizados (ZIP)",
                        data=zip_content,
                        file_name="arquivos_organizados.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

                except ValueError as e:
                    st.error(f"❌ Erro: {e}")
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro durante a organização: {e}")

    with tab2:
        st.subheader("Upload Individual")
        st.markdown("Para casos em que você prefere selecionar arquivos um a um.")

        uploaded_files = st.file_uploader(
            "Selecione os arquivos XML e PDF",
            type=["xml", "pdf"],
            accept_multiple_files=True,
            key="individual_upload"
        )

        if uploaded_files:
            st.info(f"✅ {len(uploaded_files)} arquivo(s) selecionado(s)")

        if st.button("Organizar Arquivos", type="primary", disabled=not uploaded_files, key="btn_individual"):
            if not uploaded_files:
                st.warning("Por favor, faça upload de pelo menos um arquivo.")
                return

            st.success("Iniciando organização...")

            # Container para os logs
            st.subheader("📋 Logs da Execução")
            log_placeholder = st.empty()

            # Configura o logger
            logger = logging.getLogger("streamlit_logger_individual")
            logger.setLevel(logging.INFO)

            # Limpa os handlers antigos
            if logger.hasHandlers():
                logger.handlers.clear()

            sl_handler = StreamlitHandler(log_placeholder)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
            sl_handler.setFormatter(formatter)
            logger.addHandler(sl_handler)

            with st.spinner("Organizando os arquivos..."):
                try:
                    # Processa os arquivos e gera ZIP
                    zip_content = organizar_arquivos_upload(uploaded_files, logger)

                    st.balloons()
                    st.success("✅ Organização concluída com sucesso!")

                    # Botão para download
                    st.subheader("📥 Download")
                    st.download_button(
                        label="⬇️ Baixar Arquivos Organizados (ZIP)",
                        data=zip_content,
                        file_name="arquivos_organizados.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error(f"❌ Ocorreu um erro durante a organização: {e}")

if __name__ == "__main__":
    main()
