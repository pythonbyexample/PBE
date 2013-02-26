# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'x'
        db.create_table('businesstest_x', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('menu', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', max_length=2000, blank=True)),
            ('tm_target', self.gf('django.db.models.fields.FloatField')(default=-1, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('businesstest', ['x'])


    def backwards(self, orm):
        
        # Deleting model 'x'
        db.delete_table('businesstest_x')


    models = {
        'businesstest.x': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'x'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'menu': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'tm_target': ('django.db.models.fields.FloatField', [], {'default': '-1', 'blank': 'True'})
        }
    }

    complete_apps = ['businesstest']
