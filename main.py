import streamlit as st
import openai
import os
from dotenv import load_dotenv

load_dotenv()

try:
    client = openai.OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.groq.com/openai/v1/"
        )
except Exception as e:
    st.error(f"Error initializing Groq client: {e}")
    st.error("Please check your API key, base URL, and internet connection.")
    st.stop() 

st.set_page_config(page_title="AI Email Draft Generator", layout="centered")

defaults = {
    'name':"",
    'recipient':"",
    'purpose': "",
    'key_points': "",
    'tone': "",
    'email_draft': ""
}
for key, default_value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default_value

#ask user for info
def get_email_details():
    st.header("Generate Your Email Draft")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("From:", key="name")
    with col2:
        st.text_input("To:", key="recipient")

    st.text_input("Purpose Of Email:", key="purpose")

    st.text_area("State 2-3 Key Points (Key Point 1, Key Point 2, ...): ", key="key_points")
    key_points_list = [point.strip() for point in st.session_state.key_points.split(",") if point.strip()]

    tone_options = ["formal", "professional", "informal", "friendly"]
    st.selectbox("Choose A Tone:", options=tone_options, key="tone")
        
    return st.session_state.name, st.session_state.recipient, st.session_state.purpose, key_points_list, st.session_state.tone

#generate email draft
def generate_email_draft(name, recipient, purpose, key_points_list, tone):
    max_tokens = 250

    temp_map = {
        "formal": 0.4,
        "professional": 0.5,
        "informal": 0.6,
        "friendly": 0.7
    }
    temp = temp_map.get(tone, 0.5)

    prompt = [
        {"role": "system", 
         "content": (
            "You are an AI assistant specialized in drafting professional and effective emails."
             "You will generate an email based on the user's specified name, recipient, purpose, key points and tone."
             "Do not include information which is not provided, for example displaying [Your Name]."
             "Include a concise subject line, a clear greeting, the main body incorporating all key points, and a suitable closing signature."
             "Ensure the email flows naturally and is easy to read."
             "Use appropriate paragraph breaks and blank lines for standard email formatting."
             "NO PREAMBLE."
        )},
        {"role": "user",
         "content": (
             f"My name is {name}. "
             f"The recipient of the email is {recipient}. "
             f"Draft an email that has the following purpose: {purpose}. "
             f"It should include these key points: {key_points_list}. "
             f"Write the email using a {tone} tone. "
             )}
    ]

    try:
        with st.spinner("Generating email draft..."):
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=prompt,
                max_tokens=max_tokens,
                temperature=temp
            )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An unexpected error occurred with the Groq API: {e}")
        return "Failed to generate email draft due to an API error."

def main():
    name, recipient, purpose, key_points_list, tone = get_email_details()
    
    if st.button("Generate Email"):
        if not purpose or not key_points_list:
            st.warning("Please provide a purpose and at least one key point to generate the email.")
        else:
            email_draft_content = generate_email_draft(name, recipient, purpose, key_points_list, tone)
            st.session_state.email_draft = email_draft_content
    
    if st.session_state.email_draft:
        st.subheader("Generated Email Draft:")
        st.text_area("Email Content", st.session_state.email_draft, height=300)

        st.download_button(
            label="Download Email Draft",
            data=st.session_state.email_draft,
            file_name="email_draft.txt",
            mime="text/plain" #specifies the file’s content type (.txt)
        )

if __name__ == "__main__":
    main()
