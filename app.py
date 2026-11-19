"""Streamlit interface for the ECE semantic matching prototype."""
import streamlit as st

from explanations import explain_matches
from input_processing import prepare_input
from matching import rank_specialties
from visualization import score_chart

TOP_K = 3
# Provisional value, to calibrate with Nils' evaluation (in-domain vs out-of-domain cases).
LOW_SIMILARITY_THRESHOLD = 0.30

DISCLAIMER = (
    "Educational NLP demonstration only. This prototype does not diagnose conditions, "
    "recommend treatment, assess urgency, or replace professional medical advice. "
    "Use fictional examples only."
)

st.set_page_config(page_title="Medical specialty orientation", page_icon="🩺")
st.title("Medical specialty orientation")
st.info(DISCLAIMER)

with st.form("questionnaire"):
    description = st.text_area(
        "Describe symptoms for a fictional example",
        placeholder="e.g. Red, itchy patches of skin keep coming back on my arms and get worse in winter.",
        help="Use your own words. This text is compared with the reference descriptions.",
    )
    location = st.text_input(
        "Where are the symptoms located?",
        placeholder="e.g. arms and hands",
        help="Optional. Added to the compared text.",
    )
    duration = st.text_input(
        "How long have they lasted?",
        placeholder="e.g. three weeks",
        help="Optional. Shown as context only; not used in the scoring.",
    )
    intensity = st.select_slider(
        "Reported intensity",
        ["Unspecified", "Mild", "Moderate", "Severe"],
        help="Shown as context only; not used in the scoring.",
    )
    submitted = st.form_submit_button("Find matching specialties", type="primary")


def show_match(rank: int, match: dict, explanation: dict | None) -> None:
    with st.container(border=True):
        title_col, score_col = st.columns([3, 1])
        title_col.subheader(f"{rank}. {match['specialty']}")
        score_col.metric("Cosine similarity", f"{match['score']:.3f}")

        st.markdown(f"**Closest reference pattern:** {match['symptom_category']}")
        st.markdown(f"> {match['symptom_description']}")
        st.caption(
            f"Paraphrase of the {match['source_publisher']} page on "
            f"*{match['source_condition']}* (source topic, not a predicted diagnosis), "
            f"accessed {match['accessed_date']} · reference {match['description_id']}"
        )

        if explanation:
            badge = "AI-generated explanation" if explanation["source"] == "llm" else "Template explanation"
            st.markdown(f"**Why this match** · :gray[{badge}]")
            st.write(explanation["text"])

        st.link_button(f"Open {match['source_publisher']} source", match["source_url"])


if submitted:
    try:
        text_to_embed = prepare_input(description, location)
    except ValueError as error:
        st.warning(str(error))
        st.stop()

    user_input = {
        "description": " ".join(description.split()),
        "location": " ".join(location.split()),
        "duration": duration.strip(),
        "intensity": intensity,
    }

    try:
        with st.spinner("Comparing symptom descriptions..."):
            ranked = rank_specialties(text_to_embed)
    except FileNotFoundError as error:
        st.error(f"Reference data is missing. {error}")
        st.stop()
    except (OSError, ValueError, KeyError) as error:
        st.error(f"Unable to match descriptions: {error}")
        st.stop()

    top_matches = ranked[:TOP_K]
    with st.spinner("Preparing explanations..."):
        explanations = explain_matches(user_input, top_matches)

    with st.expander("Your answers"):
        st.table(
            {
                "Field": ["Description", "Location", "Duration", "Intensity"],
                "Answer": [
                    user_input["description"],
                    user_input["location"] or "—",
                    user_input["duration"] or "—",
                    user_input["intensity"],
                ],
            }
        )
    with st.expander("Text compared with the references"):
        st.text(text_to_embed)

    st.header("Top matching specialties")
    st.info(DISCLAIMER)
    st.caption(
        "Each specialty is scored by its most similar reference description. "
        "Scores measure text similarity and are not medical probabilities."
    )

    if top_matches[0]["score"] < LOW_SIMILARITY_THRESHOLD:
        st.warning(
            f"All similarity scores are below {LOW_SIMILARITY_THRESHOLD:.2f}. "
            "The description may be outside the scope of the reference dataset, "
            "so these matches are weak."
        )

    for rank, match in enumerate(top_matches, start=1):
        show_match(rank, match, explanations.get(match["specialty_id"]))

    st.subheader("Score comparison across all specialties")
    st.altair_chart(score_chart(ranked, TOP_K), width="stretch")
