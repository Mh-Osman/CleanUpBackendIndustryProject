from rest_framework import serializers
from auditlog.models import LogEntry


class HistoryTrackSerializer(serializers.ModelSerializer):
    actor_email = serializers.CharField(source="actor.email", read_only=True)
    actor_username = serializers.CharField(source="actor.name", read_only=True)
    object_data = serializers.SerializerMethodField()
    message = serializers.SerializerMethodField()

    class Meta:
        model = LogEntry
        fields = [
            "id", "object_pk", "object_id", "object_repr", "serialized_data",
            "action", "changes", "object_data", "timestamp",
            "actor", "actor_email", "actor_username", "message"
        ]

    def get_object_data(self, obj):
        try:
            model_class = obj.content_type.model_class()
            instance = model_class.objects.filter(pk=obj.object_pk).first()
            if instance:
                return {
                    "title": getattr(instance, "title", None),
                    "content": getattr(instance, "content", None),
                }
        except:
            pass
        return None

    def get_message(self, obj):
        MODEL_LABELS = {
            "user": "User",
            "employee": "Employee",
            "building": "Building",
            "subscription": "Subscription",
            "client": "Client",
        }

        model_name = obj.content_type.model.lower()
        display_name = MODEL_LABELS.get(model_name, model_name.title())
        actor = getattr(obj.actor, "name", None) or "System"

        if obj.action == 0:
            action_label = f"New {display_name} added"
        elif obj.action == 1:
            action_label = f"{display_name} updated"
        elif obj.action == 2:
            action_label = f"{display_name} deleted"
        else:
            action_label = f"{display_name} changed"

        return f"{action_label} by {actor}"
