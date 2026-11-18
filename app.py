"""Questionnaire for the ECE semantic matching prototype."""
import streamlit as st
from input_processing import prepare_input

st.title("Medical specialty orientation")
st.info("Educational NLP demonstration only. This prototype does not diagnose conditions, recommend treatment, assess urgency, or replace professional medical advice.")
with st.form("example"):
    description = st.text_area("Describe symptoms for a fictional example")
    location = st.text_input("Where are the symptoms located?")
    duration = st.text_input("How long have they lasted?")
    intensity = st.select_slider("Reported intensity", ["Unspecified", "Mild", "Moderate", "Severe"])
    submitted = st.form_submit_button("Preview example")

if submitted:
    try:
        text_to_embed = prepare_input(description, location)
    except ValueError as error:
        st.warning(str(error))
    else:
        st.subheader("Questionnaire response")
        st.json({
            "description": description.strip(),
            "location": location.strip(),
            "duration": duration,
            "intensity": intensity,
        })

        st.subheader("Text prepared for embedding")
        st.text(text_to_embed)