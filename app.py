import time
from pathlib import Path
from advanced_chatbot.config import DATA_PATH

import streamlit as st
from streamlit_extras.bottom_container import bottom

from llama_index.core.llms import ChatMessage, MessageRole
from advanced_chatbot.services.rag_service import RagService


# Functions
# Display chatbot response in streaming mode
def stream_echo(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


# Summarize the content of a document
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
    st.session_state.messages.append(
        ChatMessage(
            role=MessageRole.USER,
            content=f"Peux-tu résumer en quelques mots le document {document_name} ?",
        )
    )

    # Add assistant response (summarized content) to chat history
    st.session_state.messages.append(
        ChatMessage(role=MessageRole.ASSISTANT, content=summarized_document)
    )

    return


# Save an uploaded file into the knowledge base
def save_uploaded_file(DATA_PATH, uploaded_file, RagService):
    try:
        # Ensure DATA_PATH directory exists or create it
        data_dir = Path(DATA_PATH)
        data_dir.mkdir(parents=True, exist_ok=True)

        # Construct full file path within DATA_PATH
        file_path = data_dir / uploaded_file.name
        index_configs = RagService.list_vector_store_index()
        for i, index_config in enumerate(index_configs):
            # Get document name
            document_path = Path(index_config["document_path"])
            document_name = document_path.name
            if uploaded_file.name == document_name:
                st.toast("Un fichier de même nom existe déjà dans la base de données !")
                return 
        # Write the uploaded file's content to the specified file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Call RagService to create an index or perform other operations
        RagService.create_vector_store_index(file_path)
        # Notify user of successful file save
        st.toast("Fichier sauvegardé !")

    except Exception as e:
        # Handle any errors and show error message to user
        st.error(f"Error saving file: {e}")


# Delete a document from the knowledge base
def delete_document(RagService, index_id):
    RagService.delete_vector_store_index(index_id)
    st.toast("Fichier supprimé avec succès !")


# App content
# App logo
st.logo("images/logo.png")

# App title
st.title("Résumez et questionnez vos docs")

# Define maximum file size in bytes (200 MB)
MAX_FILE_SIZE_MB = 200
MAX_FILE_SIZE = 200 * 1024 * 1024

# Sidebar
st.markdown(
    """
	<style>
        * {
			color: #444 !important;
		}

        body, div[data-testid="stApp"], header {
			background-color: #DDD !important;
		}
        
        section[data-testid="stSidebar"] {
			background-color: #509A8E !important;
		}
        
        div[data-testid="stExpander"] details summary * {
			font-weight: bold !important;
			color: #DDD !important;
		}

        div[data-testid="stExpander"] details summary:hover * {
            color: #FF6C6C !important;
            font-weight: normal !important;
        }

        section[data-testid="stFileUploaderDropzone"] {
			background-color: #444 !important;
		}

        div[data-testid="stFileUploaderDropzoneInstructions"] div * {
			color: #DDD !important;
		}
		
		section[data-testid="stFileUploaderDropzone"] button {
			background-color: #509A8E !important;
			color: #DDD !important;
		}

        div[data-testid="stExpanderDetails"] div[data-testid="stCheckbox"] label div:first-child {
            background-color: rgba(255, 108, 108, 0.8) !important;
        }

        div[data-testid="stExpanderDetails"] div[data-testid="stCheckbox"] label div:first-child div {
            background-color: rgba(68, 68, 68, 0.8) !important;
        }

        div[data-testid="stExpanderDetails"] div[data-testid="stCheckbox"] label div:nth-child(3) * {
            background-color: #509A8E !important;
            color: #DDD !important;
        }

        div[data-testid="stButton"] button {
            background-color: rgba(50, 154, 142, 1) !important;
        }
        
        div[data-testid="chatAvatarIcon-assistant"] {
            background-color: #FF6C6C !important;
        }

        div[data-testid="chatAvatarIcon-user"] {
            background-color: #509A8E !important;
        }

        div[data-testid="stBottom"] div {
            background-color: #DDD;
        }

        div[data-testid="stBottom"] div div {
            background-color: rgba(0, 0, 0, 0);
        }

        textarea[data-testid="stChatInputTextArea"] {
            color: rgba(68, 68, 68, 0.8) !important;
            caret-color: #444 !important;
        }

        textarea[data-testid="stChatInputTextArea"]::placeholder {
            color: rgba(68, 68, 68, 0.4) !important;
        }

        div[data-testid="stChatMessage"] {
            background-color: rgba(80, 154, 142, 0.1);
        }

        div[data-testid="stChatMessage"] div svg path {
            color: #444 !important;
        }

        div[data-testid="stTooltipContent"] {
            background-color: #DDD !important;
            border-radius: 8px;
        }
    </style>
	""",
    unsafe_allow_html=True,
)

with st.sidebar:
    # Upload a file
    with st.expander("Charger des documents"):
        uploaded_files = st.file_uploader(
            "Charger des documents",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        for file in uploaded_files:
            if file.size > MAX_FILE_SIZE:
                st.toast(
                    f"Le fichier {file.name} dépasse la taille maximale qui est {MAX_FILE_SIZE_MB} MB, nous sommes dans l'impossibilité de le charger dans notre base de données."
                )
            else:
                save_uploaded_file(DATA_PATH, file, RagService)

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
            is_in_search_area[i] = add_in_search_area.toggle(
                label=label, value=True, help=help
            )

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
            delete.button(
                label=":x:",
                key=f"delete_{document_name}",
                help="Supprimer ce document",
                on_click=delete_document,
                args=(
                    RagService,
                    index_config["index_id"],
                ),
                use_container_width=True,
            )

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

    prompt = st.chat_input(
        "Posez une question sur le.s document.s sélectionné.s",
        disabled=is_prompt_disabled,
    )

if prompt:
    # Display user message
    st.chat_message("user").markdown(prompt)

    # Add user message to chat history
    st.session_state.messages.append(ChatMessage(role=MessageRole.USER, content=prompt))

    # Get response (return user prompt for the moment)
    response, _ = RagService.complete_chat(
        query=prompt,
        conversation_history=st.session_state.messages,
        index_ids=search_area,
    )

    # Append all token together to have a unified text
    response = "".join(response)

    # Display assistant response
    st.chat_message("assistant").write_stream(stream_echo(response))

    # Add assistant response to chat history
    st.session_state.messages.append(
        ChatMessage(role=MessageRole.ASSISTANT, content=response)
    )
