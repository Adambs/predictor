import re
import random
import json
import streamlit as st
import os

file_path = os.path.join(os.path.dirname(__file__), 'responses.json')
with open(file_path, 'r') as file:
    responses = json.load(file)


# Define keyword patterns
negation_pattern = re.compile(r"\b(no|not|never)\b", re.IGNORECASE)
affirmation_pattern = re.compile(r"\b(yes|absolutely)\b", re.IGNORECASE)
question_pattern = re.compile(r".*\?$")
repetition_pattern = re.compile(r"\b(yes it is|no it isn't)\b", re.IGNORECASE)
personal_statement_pattern = re.compile(r"\b(I am|I think)\b", re.IGNORECASE)
absolute_pattern = re.compile(r"\b(always|never|impossible)\b", re.IGNORECASE)

# Track recent responses to avoid repetition
if "recent_responses" not in st.session_state:
    st.session_state.recent_responses = {
        "negation": [],
        "affirmation": [],
        "question": [],
        "repetition": [],
        "personal_statement": [],
        "absolute": [],
        "default": []
    }

def get_response(user_input):
    category = "default"
    if negation_pattern.search(user_input):
        category = "negation"
    elif affirmation_pattern.search(user_input):
        category = "affirmation"
    elif question_pattern.search(user_input):
        category = "question"
    elif repetition_pattern.search(user_input):
        category = "repetition"
    elif personal_statement_pattern.search(user_input):
        category = "personal_statement"
    elif absolute_pattern.search(user_input):
        category = "absolute"

    available_responses = [response for response in responses[category] if response not in st.session_state.recent_responses[category]]
    if not available_responses:
        available_responses = responses[category]

    selected_response = random.choice(available_responses)
    st.session_state.recent_responses[category].append(selected_response)
    if len(st.session_state.recent_responses[category]) > 4:
        st.session_state.recent_responses[category].pop(0)

    return selected_response

def main():
    st.title("Welcome to the Argument Clinic!")
    st.write("Type your statement below and engage in a playful argument. Type 'exit' to leave.")

    if "conversation" not in st.session_state:
        st.session_state.conversation = []
        st.session_state.exchanges = 0

    num_exchanges = st.number_input("How many exchanges would you like to have?", min_value=1, max_value=100, value=10, key="num_exchanges")

    if st.session_state.exchanges < num_exchanges:
        with st.form(key='input_form', clear_on_submit=True):
            user_input = st.text_input("You: ")
            submit_button = st.form_submit_button(label='Send')

        if submit_button and user_input:
            if user_input.lower() == 'exit':
                st.session_state.conversation.append(("Clinic", "I'm glad we settled that. Goodbye!"))
            else:
                clinic_response = get_response(user_input)
                st.session_state.conversation.append(("You", user_input))
                st.session_state.conversation.append(("Clinic", clinic_response))
                st.session_state.exchanges += 1

    for speaker, text in st.session_state.conversation:
        st.write(f"**{speaker}:** {text}")

    if st.session_state.exchanges >= num_exchanges:
        st.markdown(
            '<div style="color: #2E8B57; font-size: large; text-align: center;">'
            '😂 The argument session has ended. Thank you for participating! 😂'
            '</div>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()
