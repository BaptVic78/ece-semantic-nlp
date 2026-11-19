"""Local Streamlit demo for fictional symptom descriptions."""
import logging
from pathlib import Path

import altair as alt
import streamlit as st

from explanations import explain_matches
from input_processing import prepare_detailed_input, prepare_input
from matching import REBUILD, rank_queries

PALETTE = ["#6543cf", "#087d76", "#b84478"]
STYLES = Path(__file__).resolve().parent / ".streamlit" / "app.css"
UNSPECIFIED = "Unspecified"
INTENSITIES = [UNSPECIFIED, "Mild", "Moderate", "Severe"]
FREQUENCIES = [UNSPECIFIED, "Once", "Constant", "Comes and goes", "Recurring"]
MAX_SYMPTOMS = 8


def show_comparison(description_only, with_details, has_details):
    simple = {row["specialty_id"]: (rank, row["score"])
              for rank, row in enumerate(description_only, 1)}
    all_rows = [
        {"Specialty": row["specialty"], "Description rank": simple[row["specialty_id"]][0],
         "Description score": simple[row["specialty_id"]][1], "With details rank": rank,
         "With details score": row["score"]}
        for rank, row in enumerate(with_details, 1)
    ]
    if has_details:
        st.subheader("How the details change the matches")
        st.caption("The chart includes specialties that appear in either top three. "
                   "A change in score shows a change in text similarity.")
        shown = [row for row in all_rows if min(row["Description rank"], row["With details rank"]) <= 3]
        variants = ["Description only", "With symptom details"]
        bars = [
            {"Specialty": row["Specialty"], "Input": label, "Rank": row[f"{prefix} rank"],
             "Score": row[f"{prefix} score"]}
            for row in shown for label, prefix in zip(variants, ("Description", "With details"))
        ]
        chart = alt.Chart(alt.Data(values=bars)).mark_bar(cornerRadiusEnd=4).encode(
            x=alt.X("Score:Q", title="Cosine similarity", axis=alt.Axis(tickCount=5, format=".2f")),
            y=alt.Y("Specialty:N", title=None, sort=[r["Specialty"] for r in shown],
                    axis=alt.Axis(labelLimit=190, labelOverlap=False)),
            yOffset=alt.YOffset("Input:N", sort=variants),
            color=alt.Color("Input:N", title=None, scale=alt.Scale(
                domain=variants, range=["#6a6380", "#6543cf"]
            ), legend=alt.Legend(orient="top")),
            tooltip=["Specialty:N", "Input:N", "Rank:Q", alt.Tooltip("Score:Q", format=".3f")],
        ).properties(height=140 + 36 * len(shown))
        with st.container(border=True, key="comparison_chart"):
            st.altair_chart(chart, width="stretch")
    else:
        st.caption("Add a body area, duration, onset or symptom frequency to compare the two rankings.")

    with st.expander(f"View all {len(all_rows)} specialties"):
        if not has_details:
            all_rows = [{"Rank": r["Description rank"], "Specialty": r["Specialty"],
                         "Score": r["Description score"]} for r in all_rows]
        st.dataframe(
            all_rows, hide_index=True, width="stretch", height=35 * (len(all_rows) + 1),
            column_config={
                "Specialty": st.column_config.TextColumn(width=205),
                **{column: st.column_config.NumberColumn(format="%.3f")
                   for column in ("Description score", "With details score", "Score")
                   if column in all_rows[0]},
            },
        )

st.set_page_config(page_title="Medical specialty finder", layout="centered")
st.html(f"<style>{STYLES.read_text(encoding='utf-8')}</style>")
st.html("""
    <section class="match-hero" aria-labelledby="match-title">
        <h1 id="match-title">Medical specialty finder</h1>
        <p>Explore medical specialties by comparing your symptoms with published references.</p>
    </section>
""")
st.session_state.setdefault("symptom_count", 1)
with st.container(border=True, key="symptom_form"):
    st.subheader("Describe your symptoms")
    description = st.text_area(
        "Symptoms (in English)", max_chars=600,
        placeholder="I have a dry cough and feel out of breath when walking uphill.",
    )
    left, middle, right = st.columns(3)
    with left:
        location = st.text_input("Body area (optional)", max_chars=100, placeholder="e.g. chest")
    with middle:
        duration = st.text_input("Duration (optional)", max_chars=100, placeholder="e.g. two days")
    with right:
        onset = st.selectbox("Onset (optional)", [UNSPECIFIED, "Sudden", "Gradual"])
    symptom_rows = []
    with st.expander("Add symptom details", expanded=st.session_state.symptom_count > 1):
        st.caption("Frequency can affect matching. Intensity is shown for context.")
        for index in range(st.session_state.symptom_count):
            name_col, intensity_col, frequency_col = st.columns([1.4, 1, 1])
            with name_col:
                symptom = st.text_input(f"Symptom {index + 1}", max_chars=80,
                                        placeholder="e.g. abdominal cramps", key=f"symptom_{index}")
            with intensity_col:
                intensity = st.selectbox("Intensity", INTENSITIES, key=f"intensity_{index}")
            with frequency_col:
                frequency = st.selectbox("Frequency", FREQUENCIES, key=f"frequency_{index}")
            symptom_rows.append((" ".join(symptom.split()), intensity, frequency))
        if st.session_state.symptom_count < MAX_SYMPTOMS and st.button("Add another symptom"):
            st.session_state.symptom_count += 1
            st.rerun()
    submitted = st.button("Find matches", type="primary")

if submitted:
    try:
        base_text = prepare_input(description)
        if any(not name and (intensity != UNSPECIFIED or frequency != UNSPECIFIED)
               for name, intensity, frequency in symptom_rows):
            raise ValueError("Enter a symptom name for each intensity or frequency you select.")
        text = prepare_detailed_input(
            description, location, duration=duration, onset=onset,
            symptoms=[(name, frequency) for name, _, frequency in symptom_rows],
        )
    except ValueError as error:
        st.warning(str(error))
        st.stop()
    try:
        with st.spinner("Comparing reference descriptions..."):
            has_details = text != base_text
            rankings = rank_queries([base_text, text] if has_details else [base_text])
            description_only, with_details = rankings[0], rankings[-1]
            matches = with_details[:3]
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
    if any(name for name, _, _ in symptom_rows):
        with st.expander("Reported symptom details"):
            st.dataframe(
                [{"Symptom": name, "Intensity": intensity, "Frequency": frequency}
                 for name, intensity, frequency in symptom_rows if name],
                hide_index=True, width="stretch",
            )
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
    show_comparison(description_only, with_details, has_details)
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

