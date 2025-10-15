import csv

from django.core.management.base import BaseCommand
from recipes.models import Tag


class Command(BaseCommand):
    help = 'Импорт тегов из CSV.'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Путь к CSV файлу с тегами'
        )
        parser.add_argument(
            '--delimiter',
            type=str,
            default=',',
            help='Разделитель полей в CSV (по умолчанию: ",")'
        )

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        delimiter = kwargs['delimiter']

        try:
            with open(csv_file, encoding='utf-8') as f:
                # Определяем, есть ли заголовки
                has_header = csv.Sniffer().has_header(f.read(1024))
                f.seek(0)

                reader = csv.DictReader(
                    f, delimiter=delimiter) if has_header else csv.reader(
                    f, delimiter=delimiter)

                count = 0
                for row in reader:
                    if isinstance(row, dict):
                        name = row.get('name', '').strip()
                        slug = row.get('slug', '').strip().lower
                    else:
                        # Если нет заголовков
                        name, slug = row[0].strip(), row[1].strip()

                    if name and slug:
                        Tag.objects.get_or_create(
                            name=name,
                            slug=slug
                        )
                        count += 1

            self.stdout.write(self.style.SUCCESS(
                f'Успешно загружено {count} тегов!'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл не найден: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))
