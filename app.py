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

def summarize_document(RagService, index_id):
	# Get document name
	index_config = RagService.load_index_config(index_id)
	document_path = Path(index_config["document_path"])
	document_name = document_path.name

	# Retrieve the document language
	document_language = RagService.detect_document_language(index_id)
	
	if document_language != "fr":
		# Summarize the first page only if the document is not in French
		summarized_document = RagService.translate_and_summarize_first_page_fr(index_id)
	else:
		# Summarize the entire document otherwise
		summarized_document = RagService.summarize_document_index(index_id)

	# Initialize chat history if it doesn't exist
	if "messages" not in st.session_state:
		st.session_state.messages = []

	# Define user message and add it to chat history
	st.session_state.messages.append(ChatMessage(role=MessageRole.USER, content=f"Peux-tu résumer en quelques mots le document {document_name} ?"))

	# Add assistant response (summarized content) to chat history
	st.session_state.messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=summarized_document))

	return

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

		# List to check if documents are in search area
		is_in_search_area = [None] * len(index_configs)
		
		for i, index_config in enumerate(index_configs):
			# Get document name
			document_path = Path(index_config["document_path"])
			document_name = document_path.name
			document_extension = document_name.split(".")[-1]

			# Get document id (index_id)
			index_id = index_config["index_id"]

			# Display document name, allow selection in user question search area,
			# and add document summarization and file deletion buttons
			add_in_search_area, summarize, delete = st.columns([8, 1, 1])

			# Column 1: Add document in search area
			label = document_name[:8] + "..." + document_extension
			help = "Inclure ce document dans le domaine de recherche de la réponse"
			is_in_search_area[i] = add_in_search_area.toggle(label=label, value=True, help=help)

			# Column 2: Summarize document
			summarize.button(
				label=":memo:",
				key=f"summarize_{document_name}",
				help="Résumer ce document",
				on_click=summarize_document,
				args=(RagService, index_id),
				use_container_width=True,
			)
			
			# Column 3: Delete document
			delete.button(label=":x:", key=f"delete_{document_name}", help="Supprimer ce document", on_click=None, args=None, use_container_width=True)
			
# Chat interface
# Initialize chat history if it doesn't exist
if "messages" not in st.session_state:
	st.session_state.messages = []

# Ids of documents in search area
search_area = [
	index_config["index_id"]
	for index_config, include in zip(index_configs, is_in_search_area)
	if include == 1
]

# Display chat messages from history
for i, message in enumerate(st.session_state.messages):
	st.chat_message(message.dict()["role"]).markdown(message.dict()["content"])

# Prompt input at the bottom of the page
with bottom():
	# Disable prompt input if no document in search area
	is_prompt_disabled = len(search_area) == 0
	prompt = st.chat_input("Posez une question sur le.s document.s sélectionné.s", disabled=is_prompt_disabled)

if prompt:
	# Display user message
	st.chat_message("user").markdown(prompt)

	# Add user message to chat history
	st.session_state.messages.append(ChatMessage(role=MessageRole.USER, content=prompt))

	# Get response (return user prompt for the moment)
	response, _ = RagService.complete_chat(query=prompt, conversation_history=st.session_state.messages, index_ids=search_area)
	
	# Append all token together to have a unified text
	response = "".join(response)

	# Display assistant response
	st.chat_message("assistant").write_stream(stream_echo(response))

	# Add assistant response to chat history
	st.session_state.messages.append(ChatMessage(role=MessageRole.ASSISTANT, content=response))