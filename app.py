import streamlit as st
import requests
import re
import os
import uuid
import base64

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_to_file(code, filename, directory):
    with open(os.path.join(directory, filename), 'w') as file:
        file.write(code)

def extract_code(text, language):
    match = re.search(rf'```{language}(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def send_request_and_process(api_key, system_prompt, user_message):
    unique_dir_name = str(uuid.uuid4())
    directory = os.path.join('export', unique_dir_name)
    ensure_dir(directory)

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "model": "mixtral-8x7b-32768",
        "temperature": 0.5,
        "max_tokens": 30024,
        "top_p": 1,
        "stop": None,
        "stream": False,
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    completion_content = response.json()['choices'][0]['message']['content']

    html_code = extract_code(completion_content, 'html')
    css_code = extract_code(completion_content, 'css')

    file_links = []

    if html_code:
        save_to_file(html_code, 'website.html', directory)
        file_links.append(os.path.join(directory, 'website.html'))
        
    if css_code:
        save_to_file(css_code, 'styles.css', directory)
        file_links.append(os.path.join(directory, 'styles.css'))

    return completion_content, directory, file_links
    
st.set_page_config(page_title="Fastes Free AI Website Generator", page_icon="🚀", layout="wide")

st.title("Fastes Free AI Website Generator: Instant Html and CSS")
st.markdown("""
Welcome to the Fastest Free AI Website Generator! This app is designed to generate ready-to-use HTML and CSS code for your web projects in seconds.
- **How to Use:** Simply enter your API key, define your system prompt and user message, and click 'Create Website'.
- **API Key:** Obtain your free API key from [Groq API](https://console.groq.com/keys).
- **Open Source:** This tool is open-source, feel free to contribute or fork the repository on [GitHub](https://github.com/pacnimo/fast-ai-website-generator/).
- **Contact Us:** If you have any questions or suggestions, please feel free to [contact us](mailto:contact@example.com).
""")

col1, col2 = st.columns([0.3, 0.68])

with col1:
    st.title('Settings')
    api_key = st.text_input("Enter your Groq API key:", type="password")
    system_prompt = st.text_area("System Prompt:", "Describe your desired system prompt here.")
    user_message = st.text_input("User Message:", "Describe your desired user message here.")
    send_button = st.button('Create Website')

with col2:
    st.title('Preview')
    if send_button and api_key:
        try:
            completion_content, directory, file_links = send_request_and_process(api_key, system_prompt, user_message)
            for file in file_links:
                with open(file, "rb") as f:
                    base64_file = base64.b64encode(f.read()).decode('utf-8')
                file_type = 'text/html' if file.endswith('.html') else 'text/css'
                href = f"data:{file_type};base64,{base64_file}"
                st.markdown(f"**[View {os.path.basename(file)}]({href})**", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if send_button and api_key:
    st.markdown("### API Response")
    try:
        st.text_area("API Response:", value=completion_content, height=300)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
