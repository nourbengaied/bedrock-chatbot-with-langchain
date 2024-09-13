import streamlit as st
from typing import Dict, Tuple

def render_sidebar() -> Tuple[Dict, str, str, str]:
    with st.sidebar:
        model_id = st.text_input("Model ID", "default_model")
        customer_id = st.text_input("Customer ID", "default_customer")
        session_id = st.text_input("Session ID", "default_session")
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.01
        )
        
        top_p = st.slider(
            "Top-P",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01
        )
        
        top_k = st.slider(
            "Top-K",
            min_value=1,
            max_value=100,
            value=50,
            step=1
        )
        
        max_tokens = st.slider(
            "Max Tokens",
            min_value=1,
            max_value=4096,
            value=4000,
            step=1
        )

    tool_config = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_tokens": max_tokens
    }

    return tool_config, model_id, customer_id, session_id
