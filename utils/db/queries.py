from django.db import connection
from events.models import OneTimeEvent
from django.db.models import Model

from events.models import Event


def get_events(category, keyword, type: Event = OneTimeEvent):
    cursor = connection.cursor()

    cursor.execute(f"SELECT event_ptr_id FROM {type.objects.model._meta.db_table}")
    objects_ids = {objects[0] for objects in cursor.fetchall()}

    search_query = f"AND title ILIKE '%{keyword}%'" if keyword else ""

    if category:
        cursor.execute(
            f"SELECT event_id FROM events_eventcategory WHERE category_id = {category}"
        )
        objects_ids.intersection_update({objects[0] for objects in cursor.fetchall()})

    if not objects_ids:
        return type.objects.none()

    filter_ids_query = f"WHERE id = ANY(ARRAY{list(objects_ids)})"

    cursor.execute(f"SELECT id FROM events_event {filter_ids_query} {search_query}")
    events_ids = [objects[0] for objects in cursor.fetchall()]
    return type.objects.filter(id__in=events_ids)
