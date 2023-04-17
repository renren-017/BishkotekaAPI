from django.db import connection
from events.models import OneTimeEvent, Category
from django.db.models import Model
from datetime import datetime

from events.models import Event
from users.models import Organization, Customer


def get_events(category, keyword, start_time: int = None, type: Event = OneTimeEvent):
    cursor = connection.cursor()

    cursor.execute(f"SELECT event_ptr_id FROM {type.objects.model._meta.db_table}")
    objects_ids = {objects[0] for objects in cursor.fetchall()}

    search_query = f"AND title ILIKE '%{keyword}%'" if keyword else ""

    if category:
        cursor.execute(
            f"SELECT event_id FROM events_eventcategory WHERE category_id = {category}"
        )
        objects_ids.intersection_update({objects[0] for objects in cursor.fetchall()})

    if start_time:
        cursor.execute(
            f"SELECT event_ptr_id FROM events_onetimeevent WHERE DATE(start_time) = '{datetime.fromtimestamp(int(start_time)).date()}'::date"
        )
        objects_ids.intersection_update({objects[0] for objects in cursor.fetchall()})

    if not objects_ids:
        return type.objects.none()

    filter_ids_query = f"WHERE id = ANY(ARRAY{list(objects_ids)})"

    cursor.execute(f"SELECT id FROM events_event {filter_ids_query} {search_query}")
    events_ids = [objects[0] for objects in cursor.fetchall()]
    return type.objects.filter(id__in=events_ids).order_by("-start_time")


def get_categories(is_not_empty: bool = False):
    cursor = connection.cursor()
    search_query = (
        f"WHERE EXISTS (SELECT 1 FROM events_eventcategory WHERE events_eventcategory.category_id = events_category.id)"
        if is_not_empty
        else ""
    )

    cursor.execute(f"SELECT id FROM events_category {search_query}")
    categories_ids = [objects[0] for objects in cursor.fetchall()]
    return Category.objects.filter(id__in=categories_ids)


def get_organizations(keyword):
    cursor = connection.cursor()

    search_query = f"WHERE name ILIKE '%{keyword}%'" if keyword else ""

    cursor.execute(f"SELECT id FROM {Organization.objects.model._meta.db_table} {search_query}")
    objects_ids = {objects[0] for objects in cursor.fetchall()}

    return Organization.objects.filter(id__in=objects_ids)


def get_customers(keyword):
    cursor = connection.cursor()

    search_query = f"WHERE username ILIKE '%{keyword}%'" if keyword else ""

    cursor.execute(f"SELECT user_id FROM {Customer.objects.model._meta.db_table} {search_query}")
    objects_ids = {objects[0] for objects in cursor.fetchall()}

    return Customer.objects.filter(user_id__in=objects_ids)
