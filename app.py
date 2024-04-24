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
    
st.set_page_config(page_title="Fastest Free AI Website Generator", page_icon="🚀", layout="wide")

st.title("Fastest Free AI Website Generator: Instant Html and CSS")
st.markdown("""
Welcome to the Fastest Free AI Website Generator! This app is designed to generate ready-to-use HTML and CSS code for your web projects in seconds.
- **How to Use:** Simply enter your API key, define your system prompt and user message, and click 'Create Website'.
- **API Key:** Obtain your free API key from [Groq API](https://console.groq.com/keys).
- **Open Source:** This tool is open-source, feel free to contribute or fork the repository on [GitHub](https://github.com/pacnimo/fast-ai-website-generator/).
- **Contact Us:** If you have any questions or suggestions, please feel free to [contact us](mailto:contact@example.com).
""")

col1, col2 = st.columns([0.3, 0.7])

with col1:
    st.title('Settings')
    api_key = st.text_input("Enter your Groq API key:", type="password")
    system_prompt = st.text_area("System Prompt:", "Your are an Expert in Planing and Website Design, html and css, you are aware of the latest trends like glassmorphism design and the 60 30 10 rule, when you create a website design you always create in one shot a well planed design where all elements are designed, for placeholder images you use placeholder.com, your planing is a inner monoglogue, your response always involves only the html and css code in this format: ```{language}(.*?)```! Include the css code as Inline css inside the html code! Make Sure you deliver a full website and not some Lazy response.")
    user_message = st.text_input("User Message:", "Create a modern, dark-themed website utilizing the glassmorphism design trend to showcase a futuristic photo portfolio. The website should be crafted using HTML and CSS, featuring demo content that exemplifies the aesthetic and functional capabilities of the design. The overall feel should be sleek and forward-thinking, with interactive elements that enhance user engagement. Ensure the site is responsive and accessible on various devices. Show me a Full Designed Index Site, give me your best Result and I give you a Bonus of $10.000.")
    send_button = st.button('Create Website')

with col2:
    st.title('Preview')
    if send_button and api_key:
        try:
            completion_content, directory, file_links = send_request_and_process(api_key, system_prompt, user_message)
            html_file_path = [file for file in file_links if file.endswith('.html')][0]
            html_content = open(html_file_path, 'r').read()
            base64_html = base64.b64encode(html_content.encode()).decode('utf-8')
            html_iframe = f'<iframe src="data:text/html;base64,{base64_html}" width="100%" height="600"></iframe>'
            st.markdown(html_iframe, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if send_button and api_key:
    st.markdown("### Download Created Files")
    try:
        for file_link in file_links:
            with open(file_link, "rb") as file:
                btn_label = f"Download {os.path.basename(file_link)}"
                st.markdown(f'<a href="data:file/{os.path.basename(file_link)};base64,{base64.b64encode(file.read()).decode()}" download="{os.path.basename(file_link)}" target="_blank">{btn_label}</a>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

    st.markdown("### API Response, CSS Code, and HTML Code")
    try:
        with st.expander("API Response"):
            st.text_area("API Response:", value=completion_content, height=300)

        with st.expander("CSS Code"):
            css_code = extract_code(completion_content, 'css')
            if css_code:
                st.code(css_code, language='css')
                if st.button("Copy CSS Code"):
                    st.text("CSS Code copied to clipboard!")
                    st.text(css_code)

        with st.expander("HTML Code"):
            html_code = extract_code(completion_content, 'html')
            if html_code:
                st.code(html_code, language='html')
                if st.button("Copy HTML Code"):
                    st.text("HTML Code copied to clipboard!")
                    st.text(html_code)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
