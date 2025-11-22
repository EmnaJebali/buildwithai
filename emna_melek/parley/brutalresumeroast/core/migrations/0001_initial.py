# Generated manually
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RoastResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.CharField(db_index=True, max_length=255, unique=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('roast_text', models.TextField(blank=True)),
                ('image_url', models.URLField(blank=True, null=True)),
                ('pdf_path', models.CharField(blank=True, max_length=500)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='roastresult',
            index=models.Index(fields=['task_id'], name='core_roastr_task_id_idx'),
        ),
        migrations.AddIndex(
            model_name='roastresult',
            index=models.Index(fields=['status', 'created_at'], name='core_roastr_status_created_idx'),
        ),
    ]

