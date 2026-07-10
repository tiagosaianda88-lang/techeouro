from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = ROOT / "dist"
PUBLIC_PATTERNS = ("*.html", "*.css", "*.js", "*.png", "*.jpg", "*.jpeg", "*.webp")
PUBLIC_FILES = ("ads.txt", "robots.txt", "sitemap.xml", "_headers", "_redirects")
REQUIRED_FILES = {
    "index.html",
    "style.css",
    "script.js",
    "ads.txt",
    "robots.txt",
    "sitemap.xml",
    "_headers",
    "_redirects",
}


def build(destination=DEFAULT_DESTINATION):
    destination = Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    selected = set()
    for pattern in PUBLIC_PATTERNS:
        selected.update(path for path in ROOT.glob(pattern) if path.is_file())
    selected.update(ROOT / name for name in PUBLIC_FILES if (ROOT / name).is_file())

    missing = sorted(REQUIRED_FILES - {path.name for path in selected})
    if missing:
        raise RuntimeError(f"Missing required public files: {', '.join(missing)}")

    for source in sorted(selected):
        shutil.copy2(source, destination / source.name)

    forbidden = [destination / name for name in ("conteudos", "scripts", ".git") if (destination / name).exists()]
    if forbidden:
        raise RuntimeError(f"Private paths copied to public build: {forbidden}")

    print(f"Public build ready: {len(selected)} files in {destination}")
    return destination


if __name__ == "__main__":
    build()
