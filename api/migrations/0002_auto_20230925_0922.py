# Generated by Django 4.2.5 on 2023-09-25 07:22

from django.db import migrations

def create_sizes(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Size = apps.get_model("api", "Size")

    Size.objects.create(width=200, height=200, thumbnail_size=True)
    Size.objects.create(width=400, height=400, thumbnail_size=True)

def create_tiers(apps, schema_editor):
    Tier = apps.get_model("api", "Tier")
    Size = apps.get_model("api", "Size")

    basic = Tier.objects.create(
        name='Basic',
        )
    basic.thumbnail_sizes.set(Size.objects.filter(height=200))

    premium = Tier.objects.create(
        name='Premium',
        has_original_link=True
        )
    premium.thumbnail_sizes.set(Size.objects.all())

    enterprise = Tier.objects.create(
        name='Enterprise',
        has_original_link=True,
        can_generate_expiring_links=True
        )
    enterprise.thumbnail_sizes.set(Size.objects.all())
    

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_sizes),
        migrations.RunPython(create_tiers),
    ]