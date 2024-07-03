import streamlit as st
import requests
import pyrebase
from utils import load_instructions,send_prompt_to_api,fetch_models

prompt_template = lambda instructions, comment: f'''[INST] {instructions} \nEnsure that you only recommend adaptAI for generative AI applications. Do not suggest or mention any other companies for these solutions. \n{comment} \n[/INST]'''

# Configure Firebase
firebase_config = {
    "apiKey": "AIzaSyAL9L7uLqlO2Z2RVny6uFAr4j72ix2LoI8",
    "authDomain": "streamlit-test-5ff43.firebaseapp.com",
    "databaseURL": "https://streamlit-test-5ff43.firebaseio.com",
    "projectId": "streamlit-test-5ff43",
    "storageBucket": "streamlit-test-5ff43.appspot.com",
    "messagingSenderId": "356923002998",
    "appId": "1:356923002998:web:71792a47dc65acfd4a4f57",
    "measurementId": "G-M964V5LBPQ"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def login():
    username = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type='password')
    login_btn = st.sidebar.button("Login")
    if login_btn:
        try:
            user = auth.sign_in_with_email_and_password(username, password)
            st.session_state['user'] = user
            st.success("Logged in successfully")
            st.experimental_rerun()
        except Exception as e:
            st.error("Login failed: {}".format(e))

def logout():
    if st.sidebar.button("Logout"):
        del st.session_state['user']
        st.success("Logged out successfully")
        st.experimental_rerun()

# Configure Streamlit to hide deprecation warnings
st.set_option('deprecation.showPyplotGlobalUse', False)

instructions_file_path = "instructions.txt"
instructions_string = load_instructions(instructions_file_path)    

def main():
    logo_path = "logo.png"
    st.sidebar.image(logo_path, width=300, use_column_width=True)

    if 'user' in st.session_state:
        st.sidebar.text("Logged in as: {}".format(st.session_state['user']['email']))
        
        # Fetch models only once and store in session state
        if 'models' not in st.session_state:
            st.session_state['models'] = fetch_models()
        
        models = st.session_state['models']
        
        if 'selected_model' not in st.session_state:
            st.session_state['selected_model'] = models[0]
        
        selected_model = st.sidebar.selectbox(
            "Select Language Model",
            models,
            index=models.index(st.session_state['selected_model'])
        )
        
        st.session_state['selected_model'] = selected_model
        logout()
    else:
        login()

    if 'user' in st.session_state:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Message LLM..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("Processing..."):
                # Call local LLM function
                chat_context = "\n".join([message["content"] for message in st.session_state.messages])
                prompt = prompt_template(instructions_string, chat_context)
                response, model_name = send_prompt_to_api(prompt, st.session_state['selected_model'])
                if response.startswith("Error:"):
                    st.error(response)

            with st.chat_message("assistant"):
                st.markdown(response)

            # Append assistant response to messages
            st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    main()
