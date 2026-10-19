import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from categories.models import Category


class Command(BaseCommand):
    help = 'Import motorcycle category tree from motorcycle_categories.json.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Validate import and roll back changes.')

    def handle(self, *args, **options):
        path = Path(__file__).with_name('motorcycle_categories.json')
        try:
            records = json.loads(path.read_text(encoding='utf-8'))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise CommandError(f'Could not read {path}: {exc}') from exc

        if not isinstance(records, list):
            raise CommandError('JSON must contain an array.')

        roots = set()
        seen = set()
        for index, record in enumerate(records, 1):
            if not isinstance(record, dict):
                raise CommandError(f'Item {index} is not an object.')
            name = record.get('name')
            parent = record.get('parent')
            if not isinstance(name, str) or not name.strip():
                raise CommandError(f'Invalid name at item {index}.')
            if parent is not None and (not isinstance(parent, str) or not parent.strip()):
                raise CommandError(f'Invalid parent at item {index}.')
            if not isinstance(record.get('description', ''), str):
                raise CommandError(f'Invalid description at item {index}.')
            if not isinstance(record.get('is_active', True), bool):
                raise CommandError(f'Invalid is_active at item {index}.')
            name = name.strip()
            parent = parent.strip() if parent is not None else None
            record['name'] = name
            record['parent'] = parent
            if parent is None:
                roots.add(name)
            key = (parent, name)
            if key in seen:
                raise CommandError(
                    f'Duplicate entry at item {index}: name={name!r}, parent={parent!r}. '
                    'Check that every child has the correct "parent" value.'
                )
            seen.add(key)

        for record in records:
            if record['parent'] is not None and record['parent'] not in roots:
                raise CommandError(f'Unknown parent {record["parent"]!r} for {record["name"]!r}.')

        counts = {'created': 0, 'updated': 0, 'unchanged': 0}
        try:
            with transaction.atomic():
                parents = {}
                ordered = [r for r in records if r['parent'] is None]
                ordered += [r for r in records if r['parent'] is not None]
                for record in ordered:
                    parent = parents.get(record['parent']) if record['parent'] else None
                    category = Category.objects.filter(name=record['name'], parent=parent).first()
                    description = record.get('description', '')
                    is_active = record.get('is_active', True)
                    if category is None:
                        category = Category(name=record['name'], parent=parent,
                                            description=description, is_active=is_active)
                        category.full_clean()
                        category.save()
                        counts['created'] += 1
                    elif category.description != description or category.is_active != is_active:
                        category.description = description
                        category.is_active = is_active
                        category.full_clean()
                        category.save()
                        counts['updated'] += 1
                    else:
                        counts['unchanged'] += 1
                    if parent is None:
                        parents[record['name']] = category
                if options['dry_run']:
                    transaction.set_rollback(True)
        except Exception as exc:
            raise CommandError(f'Import rolled back: {exc}') from exc

        state = 'DRY RUN' if options['dry_run'] else 'Imported'
        self.stdout.write(self.style.SUCCESS(
            f'{state}: created={counts["created"]}, '
            f'updated={counts["updated"]}, unchanged={counts["unchanged"]}'
        ))
