"""Prevent reviewer-released briefs from leaking into public text assets."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from reviewer_isolation import MARKER, load_reviewer_material, publication_leaks


class ReviewerIsolationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.handout = self.root / 'reviewers/followups/DEVOPS-999-HA.md'
        self.handout.parent.mkdir(parents=True)
        self.prose = ' '.join(f'privateword{n}' for n in range(20))
        self.handout.write_text(
            f'<!-- {MARKER} -->\n# DEVOPS-999-HA — A withheld challenge title\n\n{self.prose}\n'
        )

    def leaks(self, text):
        fingerprints, labels, errors = load_reviewer_material(self.root)
        self.assertEqual(errors, [])
        return publication_leaks(text, fingerprints, labels)

    def test_nested_handouts_require_exclusion_marker(self):
        self.handout.write_text('# Unmarked handout\n')
        self.assertTrue(load_reviewer_material(self.root)[2])

    def test_marker_is_detected_in_search_json(self):
        self.assertIn('Leaked reviewer marker', self.leaks(f'{{"text":"{MARKER}"}}'))

    def test_copied_nested_prose_is_detected_without_marker(self):
        self.assertIn('Reviewer prose leaked', self.leaks(f'<p>{self.prose}</p>'))

    def test_followup_identifier_is_detected_in_a_url(self):
        self.assertIn('Reviewer-controlled follow-up label leaked',
                      self.leaks('{"location":"/DEVOPS-999-HA/"}'))

    def test_title_is_detected_without_identifier(self):
        self.assertIn('Reviewer-controlled follow-up label leaked',
                      self.leaks('<h1>A withheld <em>challenge</em> title</h1>'))

    def test_normal_base_assignment_text_is_allowed(self):
        self.assertEqual(self.leaks('DEVOPS-999: verify Git push and browser access.'), [])


if __name__ == '__main__':
    unittest.main()
