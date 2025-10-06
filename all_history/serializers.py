from auditlog.models import LogEntry
from rest_framework import serializers



class HistoryTrackSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source="actor.email", read_only=True)
    actor_username = serializers.CharField(source="actor.username", read_only=True)
    object_data = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = [
            "id", "object_pk", "object_id", "object_repr", "serialized_data",
            "action", "changes", "object_data", "timestamp",
            "actor", "actor_email", "actor_username"
        ]

    def get_object_data(self, obj):
        try:
            if obj.content_type.model_class():
                model_class = obj.content_type.model_class()
                instance = model_class.objects.filter(pk=obj.object_pk).first()
                if instance:
                    
                    return {
                        "title": getattr(instance, "title", None),
                        "content": getattr(instance, "content", None)
                    }
        except:
            pass
        return None