import re
import random
import json
import streamlit as st
import os

# Load responses from JSON file
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

# List of common grammar words to exclude
common_words = set([
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their",
    "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and",
    "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off",
    "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any",
    "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so",
    "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", '?', '!'
])

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

# Track recent user words used to avoid repetition
if "recent_user_words" not in st.session_state:
    st.session_state.recent_user_words = []

def get_random_word(user_input):
    words = user_input.split()
    filtered_words = [word for word in words if word.lower() not in common_words]
    if filtered_words:
        return random.choice(filtered_words)
    return None

def echo_user_statement(user_input):
    random_word = get_random_word(user_input)
    if random_word and random_word not in st.session_state.recent_user_words:
        variations = [
            f"Did you just say '{random_word}'? How interesting!",
            f"'{random_word}', really? Why do you think so?",
            f"So you think '{random_word}' is the key point here?",
            f"Let's talk more about '{random_word}', shall we?"
        ]
        st.session_state.recent_user_words.append(random_word)
        if len(st.session_state.recent_user_words) > 5:
            st.session_state.recent_user_words.pop(0)
        return random.choice(variations)
    return ""

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

    # Integrate user's words randomly every few feedbacks
    if random.random() < 0.3:  # 30% chance to integrate user's words
        dynamic_response = echo_user_statement(user_input)
        if dynamic_response:
            return f"{selected_response} {dynamic_response}"
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
