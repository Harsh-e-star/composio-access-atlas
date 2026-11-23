"""Bundles frontend/dist into a self-contained single-page HTML case study.
Inlines CSS and JS so the entire dashboard can be opened via double-click without a server.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "frontend" / "dist"
STANDALONE_DIR = ROOT / "standalone"
STANDALONE_FILE = STANDALONE_DIR / "case_study.html"
ROOT_CASE_STUDY = ROOT / "case_study.html"

def inline_bundle():
    html_file = DIST / "index.html"
    if not html_file.exists():
        raise FileNotFoundError(f"{html_file} does not exist. Run 'npm run build' first.")

    html_content = html_file.read_text(encoding="utf-8")

    # Inline CSS
    css_match = re.search(r'<link rel="stylesheet"[^>]*href="(/assets/[^"]+)"[^>]*>', html_content)
    if css_match:
        css_path = DIST / css_match.group(1).lstrip("/")
        if css_path.exists():
            css_content = css_path.read_text(encoding="utf-8")
            html_content = html_content.replace(css_match.group(0), f"<style>\n{css_content}\n</style>")

    # Inline JS and place at the end of body
    js_match = re.search(r'<script type="module"[^>]*src="(/assets/[^"]+)"[^>]*></script>', html_content)
    if js_match:
        js_path = DIST / js_match.group(1).lstrip("/")
        if js_path.exists():
            js_content = js_path.read_text(encoding="utf-8")
            # Escape </script> if present inside js strings
            safe_js = js_content.replace("</script>", "<\\/script>")
            # Remove original script from head
            html_content = html_content.replace(js_match.group(0), "")
            # Append before </body>
            html_content = html_content.replace("</body>", f"<script>\n{safe_js}\n</script>\n</body>")

    STANDALONE_DIR.mkdir(parents=True, exist_ok=True)
    STANDALONE_FILE.write_text(html_content, encoding="utf-8")
    ROOT_CASE_STUDY.write_text(html_content, encoding="utf-8")
    print(f"Successfully generated single-page HTML bundle at:\n  - {STANDALONE_FILE}\n  - {ROOT_CASE_STUDY} ({len(html_content) // 1024} KB)")

if __name__ == "__main__":
    inline_bundle()
