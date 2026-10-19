"""Validate published navigation, metadata, HTML links and reviewer isolation offline."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
SITE = ROOT / 'site'
errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

config = tomllib.loads((ROOT / 'zensical.toml').read_text())['project']
require(config.get('docs_dir') == 'docs', 'Published source must be docs/')
require(config.get('site_dir') == 'site', 'Generated destination must be site/')
nav = set()
def walk(value):
    if isinstance(value, str):
        nav.add(value)
    elif isinstance(value, list):
        for item in value:
            walk(item)
    elif isinstance(value, dict):
        for item in value.values():
            walk(item)
walk(config['nav'])
for item in nav:
    require((DOCS / item).is_file(), f'Missing navigation target: {item}')
for page in DOCS.rglob('*.md'):
    require(str(page.relative_to(DOCS)) in nav, f'Page missing from navigation: {page}')
for path in DOCS.rglob('*'):
    require(not path.is_symlink(), f'Symlinks prohibited in published source: {path}')
    require('reviewer' not in path.name.lower(), f'Reviewer path under docs: {path}')

from project_metadata import load_projects, validate_views

try:
    projects = load_projects(ROOT)
    errors.extend(validate_views(projects, ROOT))
except ValueError as exc:
    errors.append(str(exc))
    projects = []

# Fingerprints catch copied reviewer prose even if its sentinel is stripped.
reviewer_fingerprints = set()
for path in (ROOT / 'reviewers').glob('*.md'):
    text = path.read_text()
    require('REVIEWER_ONLY_DO_NOT_PUBLISH' in text, f'Missing reviewer marker: {path}')
    for line in text.splitlines():
        words = re.findall(r'\w+', line.lower())
        if len(words) >= 16:
            reviewer_fingerprints.add(' '.join(words[:16]))

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for attr in ('href', 'src'):
            if attrs.get(attr):
                self.links.append(attrs[attr])

require(SITE.is_dir(), 'Build site before validation')
pages = {p.resolve(): Page(p.read_text()) for p in SITE.rglob('*.html')}
require(bool(pages), 'No generated HTML')
base_path = urlsplit(config['site_url']).path
checked = 0
for path, page in pages.items():
    for link in page.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            continue
        raw = unquote(url.path)
        if raw.startswith('/'):
            raw = raw.removeprefix(base_path) if raw.startswith(base_path) else raw.lstrip('/')
            target = SITE / raw
        else:
            target = path.parent / raw if raw else path
        if target.is_dir():
            target /= 'index.html'
        target = target.resolve()
        require(target.is_relative_to(SITE.resolve()), f'Link escapes site: {path}: {link}')
        require(target.exists(), f'Broken local link: {path.relative_to(SITE)}: {link}')
        if url.fragment and target in pages:
            require(unquote(url.fragment) in pages[target].ids, f'Broken anchor: {path.relative_to(SITE)}: {link}')
        checked += 1

# Scan source plus every generated text asset, including search data and JSON.
for tree in (DOCS, SITE):
    for path in tree.rglob('*'):
        if not path.is_file():
            continue
        require('reviewer' not in str(path.relative_to(tree)).lower(), f'Reviewer artifact: {path}')
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
        require('REVIEWER_ONLY_DO_NOT_PUBLISH' not in text, f'Leaked reviewer marker: {path}')
        normalized = ' '.join(re.findall(r'\w+', re.sub(r'<[^>]+>', ' ', text).lower()))
        for fingerprint in reviewer_fingerprints:
            if fingerprint in normalized:
                errors.append(f'Reviewer prose leaked: {path}')
                break

if errors:
    print('\n'.join(errors), file=sys.stderr)
    sys.exit(1)
print(f'Validated {len(projects)} projects, {len(pages)} HTML pages, {checked} local links/assets/anchors; reviewer isolation passed.')
