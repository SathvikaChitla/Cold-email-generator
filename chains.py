import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()


class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama3-8b-8192",  # or "llama3-70b-8192" if you need
            temperature=0,
            groq_api_key=os.getenv('GROQ_API_KEY')
        )

    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}

            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing
            the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.

            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={'page_data': cleaned_text})

        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs")

        return res if isinstance(res, list) else [res]

    def write_mail(self, job, link_list,sender_name, sender_designation, company_name):
        prompt_email = PromptTemplate.from_template(
            """
         ### JOB DESCRIPTION:
    {job_description}

    ### SENDER INFO:
    - Name: {sender_name}
    - Designation: {sender_designation}
    - Company: {company_name}

    ### INSTRUCTION:
    Write a cold outreach email to the hiring manager regarding the job described above.

    The email must follow this structure:
    1. Start with: **"Dear Hiring Manager,"**
    2. Next line: **"I'm {sender_name}, {sender_designation} at {company_name}."**
    3. Then: **"We came across your job opening for [job role] and believe we can support your goals..."**
    4. Describe how {company_name} offers services relevant to the job in a professional and polite way do not order 
    5. Add 1–2 portfolio links from: {link_list}
    6. End with a soft, polite CTA

    Use contractions (e.g., **I'm** not "I am") and keep the tone warm, human, and professional.

    ❌ Do not include:
    - "Here is the email"
    - Email addresses or contact info
    - Markdown, bullets, or formatting — plain text only

    Just return the email body text.

    ### EMAIL (NO PREAMBLE):
    """
        )

        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_description": str(job),
            "link_list": link_list,
            "sender_name": sender_name,
            "sender_designation": sender_designation,
            "company_name": company_name
        })
        return res.content

if __name__ == "__main__":
    print("GROQ_API_KEY from .env:", os.getenv('GROQ_API_KEY'))
