MIN_DESCRIPTION_WORDS = 3


def prepare_input(description: str, location: str = "") -> str:
    """Clean questionnaire text and prepare it for embedding.

    Only the description and location are embedded; duration and intensity are
    displayed as context.
    """
    description = " ".join(description.split())
    location = " ".join(location.split())

    if not description:
        raise ValueError("Enter a symptom description.")
    if len(description.split()) < MIN_DESCRIPTION_WORDS:
        raise ValueError(
            f"Describe the symptoms in at least {MIN_DESCRIPTION_WORDS} words "
            "so the comparison has enough text to work with."
        )

    text = f"Symptoms: {description}"
    if location:
        text += f"\nLocation: {location}"

    return text
