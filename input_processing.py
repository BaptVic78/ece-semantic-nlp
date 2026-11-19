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