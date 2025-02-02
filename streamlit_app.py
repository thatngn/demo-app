import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="🦙💬 Llama AI Chatbot")

# Replicate Credentials
with st.sidebar:
    st.title('🦙💬 Llama AI Chatbot')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('Let\'s exploring the AI Chatbot', icon='✨')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Exploring the AI Chatbot!', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
    os.environ['REPLICATE_API_TOKEN'] = replicate_api

    st.subheader('Models and parameters')
    selected_model = st.sidebar.selectbox('Choose a Llama2 model', ['Llama2-70B', 'Llama2-13B'], key='selected_model')
    if selected_model == 'Llama2-70B':
        llm = 'meta/llama-2-70b-chat'
    elif selected_model == 'Llama2-13B':
        llm = 'meta/llama-2-13b-chat'
    else:
        llm = 'meta/llama-2-13b-chat'
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01,  help="Kiểm soát mức độ ngẫu nhiên khi tạo văn bản. Giá trị thấp giúp văn bản tập trung hơn, giá trị cao giúp sáng tạo hơn.")
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01,help="Kiểm soát tập hợp từ có xác suất tích lũy được mô hình xem xét. Giá trị thấp giúp tạo văn bản tập trung hơn, giá trị cao tăng tính đa dạng.")
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=128, value=120, step=8, help="Độ dài tối đa của văn bản được tạo. Giới hạn số lượng từ/ký tự để tránh tạo văn bản quá dài.")


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "👋 Hello. How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "👋 Hello. How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response. 
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run(llm, 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":temperature, "top_p":top_p, "max_length":max_length, "repetition_penalty":1})
    return output

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)
