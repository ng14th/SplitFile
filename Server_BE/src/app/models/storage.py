from tortoise import Model, fields
import unidecode


class Storage(Model):
    name = fields.CharField(max_length=200)
    name_unaccent = fields.TextField(null=True, blank=True)
    location_path = fields.CharField(max_length=200)

    class Meta:
        table = 'Storage'

    def save(self, using_db=None, update_fields=None, force_create=False, force_update=False):
        if not self.id:
            self.name_unaccent = unidecode.unidecode(self.name)
        return super().save(using_db, update_fields, force_create, force_update)

    def __str__(self):
        return self.name


class ChunkStorage(Model):
    name = fields.CharField(max_length=200)
    storage = fields.ForeignKeyField(
        'app.Storage',
        related_name='chunks'
    )
    duration = fields.FloatField(null=True, blank=True)

    class Meta:
        table = 'chunk_storage'
