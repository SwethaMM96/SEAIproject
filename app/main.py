import streamlit as st
from langchain_community.document_loaders import WebBaseLoader

from chains import Chain
from portfolio import Portfolio
from utils import clean_text


def create_streamlit_app(llm, portfolio, clean_text):
    st.title("📧 Cold Mail Generator")

    mode = st.radio("Choose input method:", ["URL", "Paste job description"])

    if mode == "URL":
        url_input = st.text_input("Enter the job URL:", value="https://jobs.nike.com/job/R-33460")
    else:
        pasted_text = st.text_area("Paste the job description below:")

    submit_button = st.button("Generate Cold Email")

    if submit_button:
        try:
            if mode == "URL":
                st.info("Fetching job description from URL...")
                loader = WebBaseLoader([url_input])
                raw_text = loader.load().pop().page_content
            else:
                raw_text = pasted_text

            if not raw_text:
                st.warning("No job description content found. Please check your input.")
                return

            data = clean_text(raw_text)
            portfolio.load_portfolio()
            jobs = llm.extract_jobs(data)

            for job in jobs:
                skills = job.get('skills', [])
                links = portfolio.query_links(skills)
                email = llm.write_mail(job, links)
                st.code(email, language='markdown')

        except Exception as e:
            st.error(f"An error occurred while processing the input:\n\n{e}")
            st.info("Tip: Some job sites block scraping. Try pasting the job description manually.")


if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)
