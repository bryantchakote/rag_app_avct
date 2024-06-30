import time
import streamlit as st
from pathlib import Path
from streamlit_extras.bottom_container import bottom
from llama_index.core.llms import ChatMessage, MessageRole
from advanced_chatbot.services.rag_service import RagService

# Functions
def stream_echo(response):
	for word in response.split():
		yield word + " "
		time.sleep(0.05)

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
			
# Chat interface
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
	st.session_state.messages = []

# Display chat messages from history
for i, message in enumerate(st.session_state.messages):
	st.chat_message(message.dict()["role"]).markdown(message.dict()["content"])

# Prompt input at the bottom of the page
with bottom():
	prompt = st.chat_input("Posez une question sur le.s document.s sélectionné.s")

if prompt:
	# Display user message
	st.chat_message("user").markdown(prompt)

	# Add user message to chat history
	st.session_state.messages.append(ChatMessage(role=MessageRole.USER, content=prompt))

	# Get response (return user prompt for the moment)
	response = prompt

	# Display assistant response
	st.chat_message("assistant").write_stream(stream_echo(response))

	# Add assistant response to chat history
	st.session_state.messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=response))