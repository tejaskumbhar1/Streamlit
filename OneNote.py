import streamlit as st
from pymongo import MongoClient
import json

# MongoDB connection
MONGO_URI = "mongodb+srv://tejaskumbhar1503:tejas2004@cluster0.csmz1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0v"  # Change this if needed
client = MongoClient(MONGO_URI)

# Fetch all databases
db_names = client.list_database_names()

# Streamlit UI
st.title("MongoDB Explorer")

# Sidebar for database and collection selection
with st.sidebar:
    st.header("Select Database & Collection")
    selected_db = st.selectbox("Select Database", db_names, index=0)

    # Fetch collections for the selected database
    if selected_db:
        db = client[selected_db]
        collections = db.list_collection_names()
        selected_collection = st.selectbox("Select Collection", collections, index=0)

    # Button to show data, use session state to track if it was clicked
    if st.button("Show Data"):
        st.session_state.show_data = True
        st.session_state.page = 1  # Reset page when loading new data

# Ensure session state variables exist
if "show_data" not in st.session_state:
    st.session_state.show_data = False

if "page" not in st.session_state:
    st.session_state.page = 1

# Display documents if data is to be shown
if st.session_state.show_data and selected_collection:
    collection = db[selected_collection]

    # Pagination setup
    docs_per_page = 5
    total_docs = collection.count_documents({})
    total_pages = (total_docs // docs_per_page) + (1 if total_docs % docs_per_page else 0)

    col1, col2 = st.columns([4, 1])

    with col1:
        st.subheader(f"Displaying Documents from {selected_collection} (Page {st.session_state.page}/{total_pages})")

    with col2:
        prev_col, next_col = st.columns(2)

        if st.session_state.page > 1:
            if prev_col.button("Previous"):
                st.session_state.page -= 1
                st.rerun()

        if st.session_state.page < total_pages:
            if next_col.button("Next"):
                st.session_state.page += 1
                st.rerun()

    # Fetch documents for the current page
    skip_count = (st.session_state.page - 1) * docs_per_page
    documents = collection.find().skip(skip_count).limit(docs_per_page)

    for i, doc in enumerate(documents):
        with st.expander(f"Document {skip_count + i + 1}"):
            formatted_doc = json.loads(json.dumps(doc, default=str))  # Convert ObjectId to string
            for key, value in formatted_doc.items():
                st.write(f"**{key}**: {value}")
