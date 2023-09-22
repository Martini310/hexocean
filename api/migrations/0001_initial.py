# Generated by Django 4.2.5 on 2023-09-22 08:56

import api.models
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('image', models.ImageField(upload_to=api.models.upload_to, validators=[api.models.validate_image_extension], verbose_name='Image')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('thumbnail_size', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Tier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('has_original_link', models.BooleanField(default=False)),
                ('can_generate_expiring_links', models.BooleanField(default=False)),
                ('thumbnail_sizes', models.ManyToManyField(related_name='tiers', to='api.size')),
            ],
        ),
        migrations.CreateModel(
            name='TemporaryLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exp_time', models.IntegerField(default=300, validators=[django.core.validators.MaxValueValidator(30000), django.core.validators.MinValueValidator(300)])),
                ('exp_date', models.DateTimeField(blank=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='api.image')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tier', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='profiles', to='api.tier')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='image',
            name='size',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='images', to='api.size'),
        ),
        migrations.AddField(
            model_name='image',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to=settings.AUTH_USER_MODEL),
        ),
    ]
