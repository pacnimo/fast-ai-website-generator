# this is the localhost version to run the code localy.
# streamlit run local_app.py

import streamlit as st
import requests
import re
import os
import uuid
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

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

def serve_files(directory):
    os.chdir(directory)  # Change working directory to the static files directory
    handler = SimpleHTTPRequestHandler
    server = HTTPServer(('localhost', 0), handler)  # Serve on any available port
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    return server.server_address[1]  # Return the port number where the server is listening

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

    port = serve_files(directory)
    return completion_content, directory, file_links, port

st.set_page_config(layout="wide")

col1, col2 = st.columns([0.3, 0.68])

with col1:
    st.title('Settings')
    api_key = st.text_input("Enter your API key:", type="password")
    system_prompt = st.text_area("System Prompt:", "Your are an Expert in Planing and Website Design, html and css, you are aware of the latest trends like glassmorphism design and the 60 30 10 rule, when you create a website design you always create in one shot a well planed design where all elements are designed, for placeholder images you use placeholder.com, your planing is a inner monoglogue, your response always involves only the html and css code in this format: ```{language}(.*?)```! You Always resonse with Full Designs without any <!-- Placeholders.")
    user_message = st.text_input("User Message:", "Create a modern, dark-themed website utilizing the glassmorphism design trend to showcase a futuristic photo portfolio. The website should be crafted using HTML and CSS, featuring demo content that exemplifies the aesthetic and functional capabilities of the design. The overall feel should be sleek and forward-thinking, with interactive elements that enhance user engagement. Ensure the site is responsive and accessible on various devices. Show me a Full Designed Index Site, give me your best Result and I give you a Bonus of $10.000.")
    send_button = st.button('Send Request')

with col2:
    st.title('Preview')
    if send_button and api_key:
        try:
            completion_content, directory, file_links, port = send_request_and_process(api_key, system_prompt, user_message)
            st.markdown(f'<iframe src="http://localhost:{port}/website.html" width="100%" height="400"></iframe>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if send_button and api_key:
    st.markdown("### Download Created Files")
    try:
        for file_link in file_links:
            # Generating correct URLs for downloading the files
            local_path = f"/{os.path.relpath(file_link, start=os.getcwd())}"
            download_link = f"http://localhost:8501{local_path}"
            st.markdown(f"[Download {os.path.basename(file_link)}]({download_link})")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

    st.markdown("### API Response")
    try:
        st.text_area("API Response:", value=completion_content, height=300)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
