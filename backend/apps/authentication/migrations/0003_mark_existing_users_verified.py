from django.db import migrations


def mark_existing_users_verified(apps, schema_editor):
    User = apps.get_model('authentication', 'User')
    User.objects.update(is_email_verified=True)


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0002_user_is_email_verified_emailverificationtoken'),
    ]

    operations = [
        migrations.RunPython(mark_existing_users_verified, migrations.RunPython.noop),
    ]
