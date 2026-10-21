"""Publication guards for reviewer prose and manually released follow-up briefs."""
import re

MARKER = 'REVIEWER_ONLY_DO_NOT_PUBLISH'


def normalize(text):
    return ' '.join(re.findall(r'\w+', re.sub(r'<[^>]+>', ' ', text).lower()))


def load_reviewer_material(root):
    fingerprints = set()
    hidden_labels = set()
    errors = []
    reviewers = root / 'reviewers'
    for path in reviewers.rglob('*.md'):
        text = path.read_text()
        if MARKER not in text:
            errors.append(f'Missing reviewer marker: {path}')
        for line in text.splitlines():
            words = normalize(line).split()
            if len(words) >= 16:
                fingerprints.add(' '.join(words[:16]))
        if path.is_relative_to(reviewers / 'followups'):
            hidden_labels.add(normalize(path.stem))
            for line in text.splitlines():
                if line.startswith('# '):
                    # Guard the title even when a copied heading drops the ID.
                    title = line[2:].partition(' — ')[2]
                    if title:
                        hidden_labels.add(normalize(title))
    return fingerprints, hidden_labels, errors


def publication_leaks(text, fingerprints, hidden_labels):
    errors = []
    if MARKER in text:
        errors.append('Leaked reviewer marker')
    normalized = normalize(text)
    if any(fingerprint in normalized for fingerprint in fingerprints):
        errors.append('Reviewer prose leaked')
    if any(label in normalized for label in hidden_labels):
        errors.append('Reviewer-controlled follow-up label leaked')
    return errors
