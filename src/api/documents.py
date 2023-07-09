# documents.py

from django_elasticsearch_dsl import Index, Document, fields

from src.api.models import Medicine

# TODO: Run this for creating indexes
# python manage.py search_index --rebuild


PUBLISHER_INDEX = Index('medicine')
PUBLISHER_INDEX.settings(
    number_of_shards=1,
    number_of_replicas=1
)


@PUBLISHER_INDEX.doc_type
class MedicineDocument(Document):
    id = fields.IntegerField(attr='id')
    name = fields.TextField(fields={
        'raw': {
            'type': 'keyword'
        }
    })
    salt_name = fields.TextField(fields={
        'raw': {
            'type': 'keyword'
        }
    })

    class Django(object):
        model = Medicine
