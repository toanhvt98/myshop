from rest_framework import serializers
class SerializerMixin(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        requested_fields = self.context.get('fields')

        if requested_fields:
            existing_fields = list(self.fields.keys())
            for field_name in existing_fields:
                if field_name not in requested_fields:
                    self.fields.pop(field_name)