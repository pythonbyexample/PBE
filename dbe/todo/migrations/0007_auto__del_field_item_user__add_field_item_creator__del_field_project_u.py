# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Item.user'
        db.delete_column('todo_item', 'user_id')

        # Adding field 'Item.creator'
        db.add_column('todo_item', 'creator', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='items', null=True, to=orm['auth.User']), keep_default=False)

        # Deleting field 'Project.user'
        db.delete_column('todo_project', 'user_id')

        # Adding field 'Project.creator'
        db.add_column('todo_project', 'creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)

        # Deleting field 'Tag.user'
        db.delete_column('todo_tag', 'user_id')

        # Adding field 'Tag.creator'
        db.add_column('todo_tag', 'creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)

        # Deleting field 'Type.user'
        db.delete_column('todo_type', 'user_id')

        # Adding field 'Type.creator'
        db.add_column('todo_type', 'creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'Item.user'
        db.add_column('todo_item', 'user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='items', null=True, to=orm['auth.User'], blank=True), keep_default=False)

        # Deleting field 'Item.creator'
        db.delete_column('todo_item', 'creator_id')

        # Adding field 'Project.user'
        db.add_column('todo_project', 'user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)

        # Deleting field 'Project.creator'
        db.delete_column('todo_project', 'creator_id')

        # Adding field 'Tag.user'
        db.add_column('todo_tag', 'user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)

        # Deleting field 'Tag.creator'
        db.delete_column('todo_tag', 'creator_id')

        # Adding field 'Type.user'
        db.add_column('todo_type', 'user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True), keep_default=False)

        # Deleting field 'Type.creator'
        db.delete_column('todo_type', 'creator_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'todo.item': {
            'Meta': {'object_name': 'Item'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'items'", 'null': 'True', 'to': "orm['auth.User']"}),
            'difficulty': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '3000', 'blank': 'True'}),
            'onhold': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'progress': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'items'", 'null': 'True', 'to': "orm['todo.Project']"}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'items'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['todo.Tag']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'items'", 'null': 'True', 'to': "orm['todo.Type']"})
        },
        'todo.project': {
            'Meta': {'object_name': 'Project'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.CharField', [], {'max_length': '60'})
        },
        'todo.tag': {
            'Meta': {'object_name': 'Tag'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'todo.type': {
            'Meta': {'object_name': 'Type'},
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        }
    }

    complete_apps = ['todo']
