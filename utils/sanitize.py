import html


def safe_text(text: str) -> str:
    """
    Échappe les caractères HTML dangereux tout en préservant le texte.
    Convertit les caractères spéciaux en entités HTML (&lt;, &gt;, etc.)
    pour éviter les injections XSS.

    Paramètres
    ----------
    text : str
        Texte brut (potentiellement dangereux)

    Retour
    ------
    str
        Texte échappé, sûr à afficher dans du HTML
    """
    if text is None:
        return ""

    # Conversion explicite en str (sécurité)
    text = str(text)

    # Échappe les caractères HTML dangereux
    return html.escape(text.strip())