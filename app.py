"""Questionnaire for the ECE semantic matching prototype."""
import streamlit as st
from input_processing import prepare_input
from embedding import embed
from matching import (
    load_reference_embeddings,
    cosine_similarity,
    best_match_per_specialty,
)

st.title("Medical specialty orientation")
st.info("Educational NLP demonstration only. This prototype does not diagnose conditions, recommend treatment, assess urgency, or replace professional medical advice.")
with st.form("example"):
    description = st.text_area("Describe symptoms for a fictional example")
    location = st.text_input("Where are the symptoms located?")
    duration = st.text_input("How long have they lasted?")
    intensity = st.select_slider("Reported intensity", ["Unspecified", "Mild", "Moderate", "Severe"])
    submitted = st.form_submit_button("Find matching specialties")

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

        try:
            with st.spinner("Comparing symptom descriptions..."):
                user_embedding = embed(text_to_embed)
                reference_embeddings, description_ids = load_reference_embeddings()
                scores = cosine_similarity(reference_embeddings, user_embedding)
                matches = best_match_per_specialty(scores, description_ids)
                top_matches = sorted(
                    matches, key=lambda match: match["score"], reverse=True
                )[:3]
        except (OSError, ValueError, KeyError) as error:
            st.error(f"Unable to match descriptions: {error}")
        else:
            st.subheader("Top matching specialties")
            st.caption("Scores measure text similarity and are not medical probabilities.")
            for match in top_matches:
                st.subheader(match["specialty"])
                st.write(f"Cosine similarity: {match['score']:.3f}")
                st.write("Closest reference description:")
                st.write(match["symptom_description"])
                st.link_button("NHS source", match["source_url"])
