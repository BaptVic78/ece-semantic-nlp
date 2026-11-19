"""Explanations of the ranked specialties (RAG extension, owned by Axel).

Contract agreed between the interface (Thomas) and the LLM work (Axel):

    explain_matches(user_input, matches) -> dict[str, dict]

- user_input: {"description", "location", "duration", "intensity"} as entered.
- matches: the ranked matches displayed by the app (output of
  matching.rank_specialties, usually the top three). Field names are those of
  TEAM.md: specialty_id, specialty, description_id, symptom_description,
  source_url, score, plus the other CSV columns.
- returns, keyed by specialty_id:
      {
          "text": str,                        # explanation shown in the result card
          "source": "llm" | "template",       # displayed as a badge in the app
          "cited_description_ids": list[str], # references the text relies on
      }

Rules (TEAM.md / SCOPE.md):
- explain the existing scores and ranking; never re-rank or change scores;
- use only the supplied evidence (user text + retrieved descriptions) and cite it;
- never invent symptoms, diagnoses, treatment advice or urgency assessments;
- never raise: if the LLM is unavailable or its output fails the checks,
  fall back to the template explanation so the app still returns results.
"""
import logging

logger = logging.getLogger(__name__)


def template_explanation(user_input: dict, match: dict) -> str:
    """Deterministic explanation built only from the retrieved evidence."""
    location = user_input.get("location", "").strip()
    subject = (
        f"Your description and the location you gave ({location}) are"
        if location
        else "Your description is"
    )
    return (
        f"{subject} closest in wording to the {match['specialty']} reference "
        f"pattern \"{match['symptom_category']}\" (cosine similarity "
        f"{match['score']:.3f}). This reflects text similarity with a paraphrase "
        f"of a source page ({match['source_publisher']}), not a diagnosis."
    )


def template_explanations(user_input: dict, matches: list[dict]) -> dict[str, dict]:
    return {
        match["specialty_id"]: {
            "text": template_explanation(user_input, match),
            "source": "template",
            "cited_description_ids": [match["description_id"]],
        }
        for match in matches
    }


def generate_llm_explanations(user_input: dict, matches: list[dict]) -> dict[str, dict]:
    """LLM explanations grounded in the retrieved matches. TODO (Axel).

    Suggested steps:
    1. Model setup: read the provider/model/API key from environment variables
       and raise if not configured (the caller then uses the template).
    2. Prompt: pass the user text and, for each match, its description_id,
       specialty, symptom_description, score and source_url; ask for one short
       explanation per specialty that cites description IDs and adds nothing else.
    3. Parse the answer into the return format of this module (source="llm").
    4. Checks for unsupported claims: every specialty_id present, cited IDs belong
       to the supplied matches, no diagnosis/treatment/urgency wording; raise
       ValueError if a check fails.
    """
    raise NotImplementedError("LLM explanations are not implemented yet.")


def explain_matches(user_input: dict, matches: list[dict]) -> dict[str, dict]:
    """Return one explanation per match; LLM if available, otherwise template."""
    explanations = template_explanations(user_input, matches)
    try:
        llm_explanations = generate_llm_explanations(user_input, matches)
    except NotImplementedError:
        return explanations
    except Exception:  # any LLM failure must not break the results page
        logger.exception("LLM explanations failed; using template explanations.")
        return explanations

    # Keep the template for any specialty the LLM did not cover.
    for specialty_id, explanation in llm_explanations.items():
        if specialty_id in explanations:
            explanations[specialty_id] = explanation
    return explanations
