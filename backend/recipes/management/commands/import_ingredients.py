import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из CSV.'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Путь к CSV файлу с ингредиентами'
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
                        measurement_unit = row.get(
                            'measurement_unit', '').strip()
                    else:
                        # Если нет заголовков
                        name, measurement_unit = row[0].strip(), row[1].strip()

                    if name and measurement_unit:
                        Ingredient.objects.get_or_create(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                        count += 1

            self.stdout.write(self.style.SUCCESS(
                f'Успешно загружено {count} ингредиентов!'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл не найден: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {str(e)}'))
