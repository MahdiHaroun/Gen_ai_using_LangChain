import streamlit as st
import requests
import json

# Set page config
st.set_page_config(
    page_title="SQL Agent Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API URL
BACKEND_URL = "http://localhost:8000"

def setup_database(db_config):
    """Setup database connection via backend API"""
    try:
        response = requests.post(f"{BACKEND_URL}/db", json=db_config)
        if response.status_code == 201:
            return True, response.json()
        else:
            return False, response.json()
    except requests.exceptions.RequestException as e:
        return False, {"detail": f"Connection error: {str(e)}"}

def ask_question(question):
    """Ask question to SQL agent via backend API"""
    try:
        # Since the database is already configured via /db endpoint,
        # we only need to send the question
        question_data = {"question": question}
        
        response = requests.post(
            f"{BACKEND_URL}/ask", 
            json=question_data
        )
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, response.json()
    except requests.exceptions.RequestException as e:
        return False, {"detail": f"Connection error: {str(e)}"}

def main():
    st.title("🤖 SQL Agent Chat Interface")
    st.markdown("Ask questions about your database in natural language!")
    
    # Sidebar for database configuration
    st.sidebar.header("🔧 Database Configuration")
    
    with st.sidebar:
        st.markdown("### PostgreSQL Connection")
        
        postgres_host = st.text_input("Host", value="localhost", key="host")
        postgres_port = st.number_input("Port", value=5432, min_value=1, max_value=65535, key="port")
        postgres_user = st.text_input("Username", value="", key="user")
        postgres_password = st.text_input("Password", type="password", key="password")
        postgres_db = st.text_input("Database Name", value="", key="db")
        
        # Setup database button
        if st.button("🔗 Connect to Database", type="primary"):
            if all([postgres_host, postgres_user, postgres_password, postgres_db]):
                db_config = {
                    "postgres_host": postgres_host,
                    "postgres_port": postgres_port,
                    "postgres_user": postgres_user,
                    "postgres_password": postgres_password,
                    "postgres_db": postgres_db
                }
                
                with st.spinner("Connecting to database..."):
                    success, response = setup_database(db_config)
                
                if success:
                    st.success("✅ Database connected successfully!")
                    st.session_state.db_connected = True
                    st.session_state.db_config = db_config
                    st.json(response)
                else:
                    st.error(f"❌ Database connection failed: {response.get('detail', 'Unknown error')}")
                    st.session_state.db_connected = False
            else:
                st.error("Please fill in all database connection fields")
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat with your Database")
        
        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'db_connected' not in st.session_state:
            st.session_state.db_connected = False
        if 'db_config' not in st.session_state:
            st.session_state.db_config = None
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about your database...", disabled=not st.session_state.db_connected):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get response from backend
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    success, response = ask_question(prompt)
                
                if success:
                    answer = response.get("answer", "No answer provided")
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                    # Show additional info in expander
                    with st.expander("📊 Query Details"):
                        st.json({
                            "question": response.get("question", prompt),
                            "status": response.get("status", "unknown")
                        })
                else:
                    error_msg = f"❌ Error: {response.get('detail', 'Unknown error')}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        if not st.session_state.db_connected:
            st.info("👈 Please connect to your database using the sidebar first")
    
    with col2:
        st.header("📋 Connection Status")
        
        if st.session_state.db_connected:
            st.success("🟢 Database Connected")
            if st.session_state.db_config:
                st.markdown("**Current Connection:**")
                st.markdown(f"- Host: `{st.session_state.db_config['postgres_host']}`")
                st.markdown(f"- Port: `{st.session_state.db_config['postgres_port']}`")
                st.markdown(f"- Database: `{st.session_state.db_config['postgres_db']}`")
                st.markdown(f"- User: `{st.session_state.db_config['postgres_user']}`")
        else:
            st.warning("🔴 Database Not Connected")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Sample questions
        st.markdown("### 💡 Sample Questions")
        st.markdown("""
        Try asking questions like:
        - "What tables are in this database?"
        - "Show me the first 5 rows from the users table"
        - "How many records are in each table?"
        - "What's the schema of the products table?"
        - "Find all customers from New York"
        """)

if __name__ == "__main__":
    main()
