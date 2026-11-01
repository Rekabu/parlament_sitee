import markdown as md


def render_markdown(text: str) -> str:
    """
    Превращает Markdown-текст в HTML.
    """
    return md.markdown(
        text,
        extensions=["extra", "nl2br", "sane_lists"],
    )