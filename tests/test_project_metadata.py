"""Contract tests for author errors, stable identity and multi-domain growth."""
import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from project_metadata import ROOT, catalog, load_projects, project_navigation, validate_views


class ProjectMetadataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'platform/schemas', self.root / 'platform/schemas')
        self.project = json.loads((ROOT / 'projects/DEVOPS-001/project.json').read_text())
        self.write(self.project)

    def write(self, data, folder=None):
        definition = self.root / 'projects' / (folder or data['id']) / 'project.json'
        definition.parent.mkdir(parents=True, exist_ok=True)
        definition.write_text(json.dumps(data))
        for page in data['pages']:
            path = self.root / 'docs' / data['content_path'] / page['file']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('# Fixture\n')
        reviewer = self.root / 'reviewers' / f"{data['id']}.md"
        reviewer.parent.mkdir(parents=True, exist_ok=True)
        reviewer.write_text('REVIEWER_ONLY_DO_NOT_PUBLISH\n')

    def rejected(self, **fields):
        self.project.update(fields)
        self.write(self.project)
        with self.assertRaises(ValueError):
            load_projects(self.root)

    def test_initial_definition_and_template_match_schema(self):
        self.assertEqual(load_projects(self.root)[0]['id'], 'DEVOPS-001')
        schema = json.loads((ROOT / 'platform/schemas/project.schema.json').read_text())
        Draft202012Validator(schema).validate(json.loads((ROOT / 'templates/project.json').read_text()))

    def test_unknown_field_is_rejected(self):
        self.rejected(dificulty='intermediate')

    def test_invalid_difficulty_is_rejected(self):
        self.rejected(difficulty='expert')

    def test_structured_prerequisites_are_required(self):
        self.rejected(prerequisites=['Linux'])

    def test_reversed_effort_is_rejected(self):
        self.rejected(estimated_effort={'min':20,'max':10,'unit':'hours'})

    def test_primary_domain_must_match_directory(self):
        self.rejected(primary_domain='databases', domains=['databases','kubernetes'])

    def test_secondary_domains_do_not_duplicate_navigation(self):
        data = load_projects(self.root)
        nav = project_navigation(data)
        self.assertEqual(len(nav), 2)  # Catalog plus one primary-domain group.
        self.assertIn('Kubernetes', nav[1])

    def test_content_move_preserves_identity(self):
        self.project.update(primary_domain='databases', content_path='projects/databases/git-platform')
        self.write(self.project)
        self.assertEqual(load_projects(self.root)[0]['id'], 'DEVOPS-001')

    def test_unresolved_prerequisite_and_self_reference_fail(self):
        for reference in ['DEVOPS-999', 'DEVOPS-001']:
            with self.subTest(reference=reference):
                self.rejected(prerequisites={'skills':[], 'tools':[], 'projects':[reference]})

    def test_duplicate_canonical_path_fails(self):
        second = copy.deepcopy(self.project)
        second['id'] = 'DEVOPS-002'
        self.write(second)
        with self.assertRaisesRegex(ValueError, 'Duplicate canonical'):
            load_projects(self.root)

    def test_duplicate_ids_fail(self):
        self.write(self.project, folder='DEVOPS-002')
        with self.assertRaisesRegex(ValueError, 'Duplicate project ID'):
            load_projects(self.root)

    def test_deprecation_requires_reason_and_valid_replacement(self):
        self.rejected(status='deprecated')
        self.project['deprecation'] = {'reason':'Retired after review'}
        self.write(self.project)
        self.assertIn('Retired after review', catalog(load_projects(self.root)))
        self.project['deprecation']['replacement_id'] = 'DEVOPS-999'
        self.write(self.project)
        with self.assertRaisesRegex(ValueError, 'invalid project reference'):
            load_projects(self.root)

    def test_navigation_and_catalog_drift_fail(self):
        shutil.copy(ROOT / 'zensical.toml', self.root / 'zensical.toml')
        projects = load_projects(self.root)
        path = self.root / 'docs/projects/index.md'
        path.write_text(catalog(projects))
        self.assertEqual(validate_views(projects, self.root), [])
        path.write_text('stale')
        self.assertTrue(any('Catalog is stale' in e for e in validate_views(projects, self.root)))
        path.write_text(catalog(projects))
        config = self.root / 'zensical.toml'
        config.write_text(config.read_text().replace('DEVOPS-001 · Self-Hosted Gitea Platform','Wrong title'))
        self.assertTrue(any('navigation differs' in e for e in validate_views(projects, self.root)))

    def test_twenty_one_projects_across_domains_and_levels(self):
        for number in range(2, 22):
            project = copy.deepcopy(self.project)
            project['id'] = f'DEVOPS-{number:03}'
            project['title'] = f'Test assignment {number}'
            project['primary_domain'] = 'databases' if number % 2 else 'kubernetes'
            project['domains'] = [project['primary_domain']]
            project['difficulty'] = ['beginner','intermediate','advanced'][number % 3]
            project['content_path'] = f"projects/{project['primary_domain']}/assignment-{number}"
            self.write(project)
        projects = load_projects(self.root)
        self.assertEqual(len(projects),21)
        self.assertEqual(len(project_navigation(projects)),3)  # Catalog plus two domains.
        self.assertEqual(catalog(projects).count('learning objectives'),21)


if __name__ == '__main__':
    unittest.main()
