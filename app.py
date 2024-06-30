import streamlit as st
from pathlib import Path
from advanced_chatbot.services.rag_service import RagService

# App logo
st.logo("images/logo.png")

# App title
st.title("Résumez et questionnez vos docs")

# Sidebar
with st.sidebar:
  # View the saved docs
	with st.expander("Consulter la base de connaissances"):
	  # Retrieve the list of saved docs
		index_configs = RagService.list_vector_store_index()
		
		for i, index_config in enumerate(index_configs):
			# Get document name
			document_path = Path(index_config["document_path"])
			document_name = document_path.name
			st.markdown(document_name)