import streamlit as st
from dotenv import load_dotenv
import os
import requests
import csv
import pandas as pd
from datetime import datetime


load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

st.set_page_config(page_title="German Visa Assistant", page_icon="🇩🇪")

with st.sidebar:
    st.title("🇩🇪 Visa Assistant")
    st.info("Ask questions about:\n\n• Job Seeker Visa\n• Blue Card\n• Anmeldung")
    st.markdown("---")
    st.markdown("**Model:** `Mistral 7B Instruct (free)`")
    st.caption("Powered by [OpenRouter](https://openrouter.ai)")
    st.markdown("---")
    st.write("🔧 **Need help?**")
    st.markdown("[Visit Auswärtiges Amt 🇩🇪](https://www.auswaertiges-amt.de/en)")


st.markdown("""
# 🇩🇪 German Visa Assistant
Welcome! Ask me anything about German visas or the Anmeldung process.
---
""")


def get_faq_prompt():
    return """
You are a helpful assistant that answers questions about German visas and residency. Here are some FAQs:

1. What is the Job Seeker Visa?
It allows skilled non-EU citizens to stay in Germany for 6 months to find a job.

2. What documents are needed for the Blue Card?
You need a valid job offer, recognized university degree, passport, biometric photo, and proof of health insurance.

3. How do I register address (Anmeldung) in Berlin?
Book an appointment at the Bürgeramt and bring your passport and a signed Wohnungsgeberbestätigung (landlord form).

4. Can I convert a Job Seeker Visa to a work visa?
Yes, if you find a job during your Job Seeker Visa period, you can apply for a work visa or Blue Card.

5. How long does the Blue Card process take?
It usually takes 4 to 6 weeks, depending on the local immigration office.

6. What is a blocked account?
A blocked account is a special bank account required to prove you have enough funds to live in Germany as a student or job seeker.

7. Do I need health insurance for a Job Seeker Visa?
Yes, you need valid travel or private health insurance for the duration of your stay.

8. How much does Anmeldung cost?
Anmeldung is free, but late registration may incur a fine.

9. What is the difference between the Blue Card and regular work visa?
The Blue Card is for highly qualified workers with higher salaries, while regular work visas apply to other skilled professionals.

Answer only if the question is about these topics. If not, say you can only answer visa-related questions.
"""

def log_interaction(question, answer):
    with open("chat_log.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now(), question, answer])

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.subheader("💬 Ask a Visa Question")

with st.form(key="visa_form"):
    question = st.text_input("Your question", placeholder="e.g., What documents do I need for a Blue Card?")
    submitted = st.form_submit_button("Ask")

if submitted and question:
    with st.spinner("Thinking..."):
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Referer": "http://localhost",
            "X-Title": "German Visa Assistant"
        }

        data = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [
                {"role": "system", "content": get_faq_prompt()},
                {"role": "user", "content": question}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)

        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            st.session_state["messages"].append((question, answer))

            st.success("✅ Answer received!")
            for q, a in st.session_state["messages"]:
                st.markdown(f"**🧑 You:** {q}")
                st.markdown(f"**🤖 Assistant:** {a}")
                st.markdown("---")

            log_interaction(question, answer)
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")


with st.expander("🗂️ View Previous Questions and Answers", expanded=False):
    if os.path.exists("chat_log.csv"):
        with open("chat_log.csv", "r", encoding="utf-8") as f:
            for line in list(f.readlines())[1:]:
                line = line.strip()
                if not line or "," not in line:
                    continue
                q, a = line.split(",", 1)
                st.markdown(f"**Q:** {q}")
                st.markdown(f"**A:** {a}")
                st.markdown("---")
    else:
        st.info("No previous chat history found.")


st.markdown("---")
with st.expander("📜 View Complete Chat Log"):
    try:
        df = pd.read_csv("chat_log.csv")
        st.dataframe(df, use_container_width=True)
    except FileNotFoundError:
        st.info("No chat history yet. Ask a question to get started!")

    if st.button("🧹 Clear Chat History"):
        with open("chat_log.csv", "w", encoding="utf-8") as f:
            f.write("question,answer\n")
        st.success("Chat history cleared!")


st.markdown("Made with ❤️ using [OpenRouter](https://openrouter.ai/) + Streamlit")
