"""Charts for the results page."""
import altair as alt
import pandas as pd

SCORE_AXIS_TITLE = "Cosine similarity (text similarity, not a probability)"


def score_chart(matches: list[dict], top_k: int = 3) -> alt.Chart:
    """Horizontal bar chart of every specialty's best score, top k highlighted.

    matches must be sorted by descending score (as returned by rank_specialties).
    """
    data = pd.DataFrame(
        {
            "Specialty": [match["specialty"] for match in matches],
            "Score": [match["score"] for match in matches],
            "Closest pattern": [match["symptom_category"] for match in matches],
            "Group": [
                f"Top {top_k}" if rank < top_k else "Other"
                for rank in range(len(matches))
            ],
        }
    )
    return (
        alt.Chart(data)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("Score:Q", title=SCORE_AXIS_TITLE),
            y=alt.Y("Specialty:N", sort=None, title=None),
            color=alt.Color(
                "Group:N",
                scale=alt.Scale(domain=[f"Top {top_k}", "Other"], range=["#2563eb", "#9ca3af"]),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                "Specialty",
                alt.Tooltip("Score:Q", format=".3f"),
                "Closest pattern",
            ],
        )
        .properties(height=alt.Step(24))
    )
