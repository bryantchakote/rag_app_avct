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
			document_extension = document_name.split(".")[-1]

			# Display document name, allow selection in user question search area,
			# and add document summarization and file deletion buttons
			add_in_search_area, summarize, delete = st.columns([8, 1, 1])

			# Column 1: Add document in search area
			label = document_name[:8] + "..." + document_extension
			help = "Inclure ce document dans le domaine de recherche de la réponse"
			add_in_search_area.toggle(label=label, value=True, help=help)

			# Column 2: Summarize document
			summarize.button(label=":memo:", key=f"summarize_{document_name}", help="Résumer ce document", on_click=None, args=None, use_container_width=True)
			
			# Column 3: Delete document
			delete.button(label=":x:", key=f"delete_{document_name}", help="Supprimer ce document", on_click=None, args=None, use_container_width=True)
			