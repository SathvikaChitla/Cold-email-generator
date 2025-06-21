import os
os.environ["USER_AGENT"] = os.getenv("USER_AGENT", "Mozilla/5.0")

import streamlit as st
from utils import clean_text, fetch_text_from_url
from chains import Chain
from portfolio import Portfolio


def create_streamlit_app(llm, portfolio):
    st.title("📧 Cold Mail Generator")

    url_input = st.text_input(
        "Enter a job posting URL:",
        value="https://careers.nike.com/director-engineering-data-integration-tech-foundation-itc/job/R-61663"
    )

    sender_name = st.text_input("Enter Name", value="Sathvika")
    sender_designation = st.text_input("Enter Designation", value="Founder")
    company_name = st.text_input("Enter Company Name", value="VibeTech Studio")

    submit_button = st.button("Generate Email")

    if submit_button:
        st.write("✅ Button clicked!")

        with st.spinner("Generating email..."):
            try:
                # Fetch and clean job description
                raw_text = fetch_text_from_url(url_input)
                if not raw_text.strip():
                    st.error("❌ Could not fetch job description.")
                    return
                cleaned_data = clean_text(raw_text)

                # Extract job roles
                jobs = llm.extract_jobs(cleaned_data)
                if not jobs:
                    st.warning("No jobs found.")
                    return

                # Generate cold emails
                for job in jobs:
                    skills = job.get('skills', [])

                    job_desc = job.get("description", "")
                    results = portfolio.collection.query(
                        query_texts=[job_desc],
                        n_results=1,
                        include=["distances", "metadatas"]
                    )

                    # 🎯 Step 2: Check semantic similarity score
                    score = results["distances"][0][0]
                    if score > 0.45:  # You can tweak this threshold
                        st.warning("No relevant match found based on company services. Email not generated.")
                        return

                    # ✅ Step 3: Extract matching portfolio links
                    matched_metadata = results["metadatas"][0]
                    link_list_str = matched_metadata.get("links", "")

                    email = llm.write_mail(job, link_list_str, sender_name, sender_designation, company_name)

                    st.subheader(f"Role: {job.get('role', 'N/A')}")
                    st.markdown("### Cold Email:")
                    st.code(email, language='markdown')

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Cold Email Generator", page_icon="📧")
    chain = Chain()
    portfolio = Portfolio()
    create_streamlit_app(chain, portfolio)
