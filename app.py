import streamlit as st
from script_generator import generate

st.set_page_config(
    page_title="Script Bench",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Script Bench")
st.write("AI-powered short-form video script generator")

niche = st.text_input(
    "Niche",
    placeholder="e.g. Personal Finance"
)

topic = st.text_area(
    "Topic",
    placeholder="e.g. I automated my savings and forgot about it for two years"
)

target_seconds = st.number_input(
    "Target Runtime (seconds)",
    min_value=15,
    max_value=180,
    value=45,
    step=5
)

if st.button("Generate Script", type="primary"):

    if not niche.strip() or not topic.strip():
        st.error("Please enter both a niche and topic.")

    else:
        with st.spinner("Writing your script..."):

            try:
                result = generate(
                    niche.strip(),
                    topic.strip(),
                    int(target_seconds)
                )

                st.subheader("🎯 Hook")
                st.write(result["hook"])

                st.subheader("📝 Body")
                st.write(result["body"])

                st.subheader("📢 CTA")
                st.write(result["cta"])

            except Exception as e:
                st.error(f"Generation failed: {e}")
