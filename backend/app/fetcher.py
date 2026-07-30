"""URL -> policy text. Separate layer, on purpose.

specs/2_spec.md §11.1 flags this as the SSRF surface of the project: it follows a
URL given by the user and downloads a remote page. That is why it lives in its own
module with its own guards, instead of inside the analyze flow.

What it does NOT do: execute JavaScript. Pages that render their text client-side
will come back empty, and that is reported as a readable error rather than silently
producing a bad analysis. Policy pages are usually plain HTML (they must be
accessible, printable and indexable), so the simple path covers most of them. If a
target page needs a real browser, the escalation is Playwright — a separate decision,
because it adds ~300 MB and seconds per request.
"""

import ipaddress
import socket
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from .config import MAX_TEXT_LENGTH
from .errors import BackendError

TIMEOUT_SECONDS = 10.0
MAX_DOWNLOAD_BYTES = 5_000_000
MAX_REDIRECTS = 3
MIN_USEFUL_CHARS = 500

# A real browser UA: many sites reject the default python-httpx one outright.
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
)

# Stripped before extracting text: they carry no policy content and would pollute
# the fragments with menus and cookie banners.
NOISE_TAGS = ("script", "style", "nav", "footer", "header", "form", "noscript", "svg")


def _guard_url(url: str) -> str:
    """Reject anything that is not a public http(s) address.

    This is the SSRF mitigation and it is not optional: without resolving the
    hostname first, a request to http://169.254.169.254/ or http://localhost:8000/
    would make the backend fetch its own internal network on the user's behalf.
    """
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise BackendError(400, "Only http and https URLs are supported.")
    if not parsed.hostname:
        raise BackendError(400, "That does not look like a valid URL.")

    try:
        # getaddrinfo resolves the name the same way the request will, so we check
        # the address that is actually going to be contacted.
        infos = socket.getaddrinfo(parsed.hostname, None)
    except socket.gaierror:
        raise BackendError(400, f"Could not resolve the domain '{parsed.hostname}'.")

    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if (
            address.is_private
            or address.is_loopback
            or address.is_link_local
            or address.is_reserved
        ):
            raise BackendError(400, "That URL points to a private address.")

    return url


def _download(url: str) -> str:
    """Fetch the page, following a bounded number of redirects, revalidating each hop."""
    current = _guard_url(url)

    with httpx.Client(
        timeout=TIMEOUT_SECONDS,
        follow_redirects=False,  # each hop is revalidated by _guard_url
        headers={"User-Agent": USER_AGENT, "Accept-Language": "es,en;q=0.8"},
    ) as client:
        for _ in range(MAX_REDIRECTS + 1):
            try:
                response = client.get(current)
            except httpx.TimeoutException:
                raise BackendError(
                    504, "The page took too long to respond. Try again or paste the text."
                )
            except httpx.HTTPError:
                raise BackendError(502, "Could not reach that page.")

            if response.is_redirect:
                location = response.headers.get("location")
                if not location:
                    break
                current = _guard_url(str(response.url.join(location)))
                continue

            if response.status_code == 403:
                raise BackendError(
                    502,
                    "That site blocked our request. Try the browser extension, which "
                    "reads the page you are already viewing.",
                )
            if response.status_code >= 400:
                raise BackendError(
                    502, f"The page returned an error ({response.status_code})."
                )

            if len(response.content) > MAX_DOWNLOAD_BYTES:
                raise BackendError(400, "That page is too large to analyse.")

            return response.text

    raise BackendError(502, "Too many redirects.")


def _extract_text(html: str) -> str:
    """Pull the readable text out of the HTML, one blank line between blocks.

    The double newline matters: chunker.split_into_fragments splits on it, so this
    is what turns the page into the paragraph-level fragments the model expects.
    """
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(list(NOISE_TAGS)):
        tag.decompose()

    # main/article first when present: policy pages often wrap the legal text in one,
    # and it excludes sidebars without guessing.
    root = soup.find("main") or soup.find("article") or soup.body or soup

    blocks = []
    for element in root.find_all(["p", "li", "h1", "h2", "h3", "h4", "div"]):
        # Only leaf-ish elements, or every parent div would repeat its children's text.
        if element.find(["p", "li", "div"]):
            continue
        text = element.get_text(" ", strip=True)
        if text and len(text) > 1:
            blocks.append(text)

    if not blocks:
        blocks = [root.get_text("\n", strip=True)]

    # De-duplicate consecutive repeats (common in templated legal pages).
    unique = []
    for block in blocks:
        if not unique or unique[-1] != block:
            unique.append(block)

    return "\n\n".join(unique).strip()


def fetch_policy_text(url: str) -> str:
    """URL -> plain text ready for analyze_text. Raises BackendError with a readable
    message when the page cannot be read, instead of returning something unusable."""
    text = _extract_text(_download(url))

    if len(text) < MIN_USEFUL_CHARS:
        raise BackendError(
            422,
            "We could not read enough text from that page. It may load its content "
            "with JavaScript, or the URL may not point directly to the privacy "
            "policy. Try the direct link to the policy, or the browser extension.",
        )

    return text[:MAX_TEXT_LENGTH]