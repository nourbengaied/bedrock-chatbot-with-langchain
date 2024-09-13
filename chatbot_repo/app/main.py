import streamlit as st
from app.chatbot import chat, clear_session_state, format_messages
from app.config import render_sidebar

def main():
    st.title("Chatbot with Bedrock")

    # Initialize session state
    if 'messages_list' not in st.session_state:
        st.session_state['messages_list'] = []

    tool_config, model_id, customer_id, session_id = render_sidebar()
    
    user_msg = st.text_input("Your message")

    if st.button("Send"):
        if user_msg:
            response, messages_list = chat(session_id, user_msg, model_id, customer_id, tool_config)
            if response:
                formatted_messages = format_messages(messages_list)
                st.text_area("Assistant Response", value=response, height=300)
                st.text_area("Conversation History", value=formatted_messages, height=300)

    if st.button("Clear Chat"):
        clear_session_state()
        st.write("Chat history cleared.")

if __name__ == "__main__":
    main()
