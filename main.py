import streamlit as st
from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError
from utils import add_punctuation, transcribe

PAGE_CONFIG = dict(
    page_title="Youtube Transcriber",
    page_icon=":material/smart_display:",
    menu_items={
        "About": "https://github.com/hoishing/youtube-transcriber/issues",
        "Get help": "https://github.com/hoishing/youtube-transcriber/issues",
    },
)

st.set_page_config(**PAGE_CONFIG)
st.markdown("### 🎬 &nbsp; Youtube Transcriber")
st.caption("Extract captions from Youtube if available, transcribe with AI otherwise")
st.text("")

url = st.text_input("Enter the Youtube URL")
if not url:
    st.stop()

yt = YouTube(url)

try:
    yt.check_availability()
except RegexMatchError:
    st.error("Invalid URL")
    st.stop()

langs = [c.code for c in yt.captions]

if not langs:
    st.warning("No captions found, enter Groq API key to generate captions")
    groq_api_key = st.text_input(
        "Enter the Groq API key",
        help="visit https://console.groq.com/login to get the API key",
    )
    if not groq_api_key:
        st.stop()
    if st.button("Generate captions"):
        transcript = transcribe(groq_api_key, url)
        output = add_punctuation(groq_api_key, transcript)
        st.text_area(label="Transcript", value=output, height=400)
    st.stop()

lang = st.selectbox(
    label="Select the language",
    options=langs,
    index=None,
    format_func=lambda x: x.split(".")[-1],
)

if not lang:
    st.stop()


format = st.radio(
    label="Select the format",
    options=["SRT", "TXT"],
    index=0,
    horizontal=True,
)

if format == "SRT":
    transcript = yt.captions[lang].generate_srt_captions()
else:
    transcript = yt.captions[lang].generate_txt_captions()

st.text_area(label="Transcript", value=transcript, height=400)
