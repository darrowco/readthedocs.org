# -*- coding: utf-8 -*-
import os

from django.test import TestCase

from readthedocs.projects.models import ImportedFile, Project
from readthedocs.projects.tasks import _create_imported_files, _sync_imported_files


base_dir = os.path.dirname(os.path.dirname(__file__))


class ImportedFileTests(TestCase):
    fixtures = ['eric', 'test_data']

    def setUp(self):
        self.project = Project.objects.get(slug='pip')
        self.version = self.project.versions.first()
    
    def _manage_imported_files(self, version, path, commit, build):
        """Helper function for the tests to create and sync ImportedFiles."""
        _create_imported_files(version, path, commit, build)
        _sync_imported_files(version, build, set())

    def test_properly_created(self):
        test_dir = os.path.join(base_dir, 'files')
        self.assertEqual(ImportedFile.objects.count(), 0)
        self._manage_imported_files(self.version, test_dir, 'commit01', 1)
        self.assertEqual(ImportedFile.objects.count(), 3)
        self._manage_imported_files(self.version, test_dir, 'commit01', 2)
        self.assertEqual(ImportedFile.objects.count(), 3)

    def test_update_commit(self):
        test_dir = os.path.join(base_dir, 'files')
        self.assertEqual(ImportedFile.objects.count(), 0)
        self._manage_imported_files(self.version, test_dir, 'commit01', 1)
        self.assertEqual(ImportedFile.objects.first().commit, 'commit01')
        self._manage_imported_files(self.version, test_dir, 'commit02', 2)
        self.assertEqual(ImportedFile.objects.first().commit, 'commit02')

    def test_update_content(self):
        test_dir = os.path.join(base_dir, 'files')
        self.assertEqual(ImportedFile.objects.count(), 0)

        with open(os.path.join(test_dir, 'test.html'), 'w+') as f:
            f.write('Woo')

        self._manage_imported_files(self.version, test_dir, 'commit01', 1)
        self.assertEqual(ImportedFile.objects.get(name='test.html').md5, 'c7532f22a052d716f7b2310fb52ad981')

        with open(os.path.join(test_dir, 'test.html'), 'w+') as f:
            f.write('Something Else')

        self._manage_imported_files(self.version, test_dir, 'commit02', 2)
        self.assertNotEqual(ImportedFile.objects.get(name='test.html').md5, 'c7532f22a052d716f7b2310fb52ad981')

        self.assertEqual(ImportedFile.objects.count(), 3)
