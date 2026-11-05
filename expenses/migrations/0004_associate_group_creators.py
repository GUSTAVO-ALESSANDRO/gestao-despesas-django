from django.db import migrations


def associate_group_creators(apps, schema_editor):
    Group = apps.get_model('expenses', 'Group')
    GroupMembership = apps.get_model('expenses', 'GroupMembership')
    database = schema_editor.connection.alias

    for group in Group.objects.using(database).all().iterator():
        membership, created = GroupMembership.objects.using(database).get_or_create(
            group_id=group.pk,
            user_id=group.created_by_id,
            defaults={'is_accepted': True, 'is_group_admin': True},
        )
        if not created and (not membership.is_accepted or not membership.is_group_admin):
            membership.is_accepted = True
            membership.is_group_admin = True
            membership.save(using=database, update_fields=('is_accepted', 'is_group_admin'))


class Migration(migrations.Migration):
    dependencies = [
        ('expenses', '0003_restricoes_e_metadados'),
    ]

    operations = [
        migrations.RunPython(associate_group_creators, migrations.RunPython.noop),
    ]
