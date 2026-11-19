def prepare_input(description: str, location: str = "") -> str:
    """Clean questionnaire text and prepare it for embedding."""
    description = " ".join(description.split())
    location = " ".join(location.split())

    if not description:
        raise ValueError("Enter a symptom description.")

    text = f"Symptoms: {description}"
    if location:
        text += f"\nLocation: {location}"

    return text


def prepare_detailed_input(
    description: str,
    location: str = "",
    *,
    duration: str = "",
    onset: str = "",
    symptoms: list[tuple[str, str]] | None = None,
) -> str:
    """Add supplied context, keeping each frequency attached to its symptom."""
    parts = [prepare_input(description, location)]
    duration = " ".join(duration.split())
    if duration:
        parts.append(f"Duration: {duration}")
    if onset and onset != "Unspecified":
        parts.append(f"Onset: {onset.lower()}")
    for symptom, frequency in symptoms or []:
        symptom = " ".join(symptom.split())
        if symptom and frequency and frequency != "Unspecified":
            parts.append(f"Frequency of {symptom}: {frequency.lower()}")
    return "\n".join(parts)
