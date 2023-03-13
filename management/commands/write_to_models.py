import openpyxl
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from forarmenians_app.models import News, NewsCategory

User = get_user_model()


class Command(BaseCommand):
    help = 'Writes everything to models'

    def add_arguments(self, parser):
        parser.add_argument('category_name', type=str)

    def handle(self, *args, **options):

        category, _ = NewsCategory.objects.get_or_create(category=options['category_name'])

        workbook = openpyxl.load_workbook('forarmenians_app/management/commands/news.xlsx')
        worksheet = workbook.active

        titles, dates, bodies, images, links = [], [], [], [], []

        for row in worksheet.iter_rows(values_only=True, min_row=2):
            titles.append(row[0])
            dates.append(row[1])
            bodies.append(row[2])
            images.append(row[3])
            links.append(row[4])

        for i in range(len(titles)):
            try:
                news_item = News.objects.get(link=links[i])
            except News.DoesNotExist:
                news = News.objects.create(
                    category=category,
                    created_by=User.objects.first(),
                    title=titles[i],
                    description=bodies[i],
                    photo=images[i],
                    news_source='armenianbd.com',
                    link=links[i]
                )
