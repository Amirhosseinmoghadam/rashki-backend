import io
import json
from unittest.mock import patch
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from categories.models import Category

MODULE = 'categories.management.commands.import_motorcycle_categories.Path'


class ImportCategoryCommandTests(TestCase):
    def execute_records(self, records, *args):
        # Patch only the JSON read, avoiding any changes to the production JSON.
        with patch(MODULE) as fake_path:
            fake_path.return_value.with_name.return_value.read_text.return_value = json.dumps(records, ensure_ascii=False)
            output = io.StringIO()
            call_command('import_motorcycle_categories', *args, stdout=output)
            return output.getvalue()

    def test_import_root_and_child(self):
        self.execute_records([
            {'name': 'موتور', 'parent': None},
            {'name': 'پیستون', 'parent': 'موتور'},
        ])
        parent = Category.objects.get(name='موتور')
        self.assertEqual(Category.objects.get(name='پیستون').parent, parent)

    def test_import_is_idempotent(self):
        records = [{'name': 'موتور', 'parent': None}, {'name': 'پیستون', 'parent': 'موتور'}]
        self.execute_records(records)
        self.execute_records(records)
        self.assertEqual(Category.objects.count(), 2)

    def test_existing_category_is_updated(self):
        self.execute_records([{'name': 'موتور', 'description': 'قدیمی'}])
        self.execute_records([{'name': 'موتور', 'description': 'جدید', 'is_active': False}])
        category = Category.objects.get(name='موتور')
        self.assertEqual(category.description, 'جدید')
        self.assertFalse(category.is_active)

    def test_dry_run_does_not_persist(self):
        self.execute_records([{'name': 'آزمایشی'}], '--dry-run')
        self.assertFalse(Category.objects.filter(name='آزمایشی').exists())

    def test_duplicate_entry_rejected(self):
        with self.assertRaisesRegex(CommandError, 'Duplicate entry'):
            self.execute_records([{'name': 'موتور'}, {'name': 'موتور'}])

    def test_unknown_parent_rejected(self):
        with self.assertRaisesRegex(CommandError, 'Unknown parent'):
            self.execute_records([{'name': 'پیستون', 'parent': 'ناموجود'}])

    def test_non_array_rejected(self):
        with self.assertRaisesRegex(CommandError, 'array'):
            self.execute_records({'name': 'موتور'})

    def test_empty_name_rejected(self):
        with self.assertRaisesRegex(CommandError, 'Invalid name'):
            self.execute_records([{'name': '  '}])

    def test_invalid_active_flag_rejected(self):
        with self.assertRaisesRegex(CommandError, 'Invalid is_active'):
            self.execute_records([{'name': 'موتور', 'is_active': 'yes'}])

    def test_description_must_be_string(self):
        with self.assertRaisesRegex(CommandError, 'Invalid description'):
            self.execute_records([{'name': 'موتور', 'description': 123}])
