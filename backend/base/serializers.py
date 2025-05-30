from rest_framework import serializers
class SerializerMixin(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = self.context.get('fields')
        if fields is not None:
            allowed_fields = set(fields)
            existing_fields = set(self.fields.keys())
            for field_name in existing_fields - allowed_fields:
                self.fields.pop(field_name)