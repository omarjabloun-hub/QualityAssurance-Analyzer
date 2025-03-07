from bs4 import BeautifulSoup

def clean_html(html_content: str) -> str:
    """
    Cleans unnecessary elements from HTML content for QA testing.
    
    Removes:
    - Ads, third-party scripts, social media widgets
    - Comments, whitespace, hidden elements
    - Non-functional scripts and styles
    - Print-specific styles, noscript content, and decorative elements
    """
    
    soup = BeautifulSoup(html_content, "html.parser")

    # Remove unwanted tags
    for tag in soup(["iframe", "script", "noscript", "style", "meta", "link"]):
        tag.decompose()

    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.startswith("<!--")):
        comment.extract()

    # Remove empty divs and spans
    for tag in soup.find_all(["div", "span"]):
        if not tag.text.strip():
            tag.decompose()

    # Remove hidden elements
    for tag in soup.find_all(style=True):
        if "display: none" in tag["style"] or "visibility: hidden" in tag["style"]:
            tag.decompose()

    return str(soup.prettify())
