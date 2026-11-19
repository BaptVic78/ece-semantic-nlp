"""Local Streamlit demo for fictional symptom descriptions."""
import logging
from pathlib import Path

import altair as alt
import streamlit as st

from explanations import explain_matches
from input_processing import prepare_input
from matching import REBUILD, rank_specialties

PALETTE = ["#6543cf", "#087d76", "#b84478"]
STYLES = Path(__file__).resolve().parent / ".streamlit" / "app.css"

st.set_page_config(page_title="Medical specialty finder", layout="centered")
st.html(f"<style>{STYLES.read_text(encoding='utf-8')}</style>")
st.html("""
    <section class="match-hero" aria-labelledby="match-title">
        <h1 id="match-title">Medical specialty finder</h1>
        <p>Explore medical specialties by comparing your symptoms with published references.</p>
    </section>
""")
with st.form("example"):
    st.subheader("Describe your symptoms")
    description = st.text_area(
        "Symptoms (in English)", max_chars=600,
        placeholder="I have a dry cough and feel out of breath when walking uphill.",
    )
    left, right = st.columns(2)
    with left:
        location = st.text_input("Body area (optional)", max_chars=100, placeholder="e.g. chest")
    with right:
        duration = st.text_input("Duration (optional)", max_chars=100, placeholder="e.g. two days")
    intensity = st.selectbox("Symptom intensity", ["Unspecified", "Mild", "Moderate", "Severe"])
    submitted = st.form_submit_button("Find matches", type="primary")

if submitted:
    try:
        text = prepare_input(description, location)
    except ValueError as error:
        st.warning(str(error))
        st.stop()
    try:
        with st.spinner("Comparing reference descriptions..."):
            matches = rank_specialties(text)
    except Exception as error:
        logging.exception("Retrieval failed")
        message = f"Reference embeddings need to be generated or refreshed. {REBUILD}" if REBUILD in str(error) else (
            "The comparison could not run. Check the terminal and the setup instructions in the README."
        )
        st.error(message)
        st.stop()

    st.header("Closest specialty matches")
    st.caption("Scores indicate how closely your description matches the reference text. "
               "They do not indicate the likelihood of a medical condition.")
    st.caption(f'Duration: {duration.strip() or "unspecified"} · Reported intensity: {intensity}. '
               "These fields are shown for context only.")
    specialty_order = [m["specialty"] for m in matches]
    chart = alt.Chart(alt.Data(values=matches)).mark_bar(cornerRadiusEnd=6, size=27).encode(
        x=alt.X("score:Q", title="Cosine similarity", axis=alt.Axis(tickCount=6, format=".2f")),
        y=alt.Y("specialty:N", title=None, sort=specialty_order,
                axis=alt.Axis(labelLimit=235, labelOverlap=False)),
        color=alt.Color("specialty:N", scale=alt.Scale(domain=specialty_order, range=PALETTE), legend=None),
        tooltip=[alt.Tooltip("specialty:N", title="Specialty"),
                 alt.Tooltip("score:Q", title="Cosine similarity", format=".3f")],
    ).properties(height=170)
    with st.container(border=True, key="score_chart"):
        st.altair_chart(chart, width="stretch")
    with st.spinner("Preparing evidence notes..."):
        notes = explain_matches(text, matches)

    for rank, (match, (note, selected)) in enumerate(zip(matches, notes), 1):
        with st.container(border=True, key=f"match_{rank}"):
            st.subheader(f'{rank}. {match["specialty"]}')
            st.caption(f'Cosine similarity: {match["score"]:.3f}')
            st.caption("Matching excerpts" if selected else "About this match")
            st.text(note)
            st.write(match["symptom_description"])
            st.link_button(f'Source: {match["source_publisher"]}', match["source_url"])

