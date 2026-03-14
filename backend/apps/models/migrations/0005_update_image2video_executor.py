from django.db import migrations


OLD_EXECUTOR = "core.ai_client.image2video_client.Image2VideoClient"
NEW_EXECUTOR = "core.ai_client.image2video_client.VideoGeneratorClient"


def forwards(apps, schema_editor):
    ModelProvider = apps.get_model("models", "ModelProvider")
    ModelProvider.objects.filter(
        provider_type="image2video",
        executor_class=OLD_EXECUTOR,
    ).update(executor_class=NEW_EXECUTOR)


def backwards(apps, schema_editor):
    ModelProvider = apps.get_model("models", "ModelProvider")
    ModelProvider.objects.filter(
        provider_type="image2video",
        executor_class=NEW_EXECUTOR,
    ).update(executor_class=OLD_EXECUTOR)


class Migration(migrations.Migration):

    dependencies = [
        ("models", "0004_create_mock_providers"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
