# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Promotion'
        db.create_table(u'photo_contest_promotion', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=70)),
        ))
        db.send_create_signal(u'photo_contest', ['Promotion'])

        # Adding model 'ImageProfile'
        db.create_table(u'photo_contest_imageprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('promotion', self.gf('django.db.models.fields.related.ForeignKey')(related_name='images', to=orm['photo_contest.Promotion'])),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=75)),
            ('confirm_email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('personal_info', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('birthday', self.gf('django.db.models.fields.DateField')(max_length=10, null=True, blank=True)),
            ('sex', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=14, null=True, blank=True)),
            ('address1', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('address2', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('thumbnail', self.gf('django.db.models.fields.files.ImageField')(max_length=100, null=True, blank=True)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('caption', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('accept_terms', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('waive_rights', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'photo_contest', ['ImageProfile'])


    def backwards(self, orm):
        
        # Deleting model 'Promotion'
        db.delete_table(u'photo_contest_promotion')

        # Deleting model 'ImageProfile'
        db.delete_table(u'photo_contest_imageprofile')


    models = {
        u'photo_contest.imageprofile': {
            'Meta': {'ordering': "['created']", 'object_name': 'ImageProfile'},
            'accept_terms': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'birthday': ('django.db.models.fields.DateField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'confirm_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'personal_info': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '14', 'null': 'True', 'blank': 'True'}),
            'promotion': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': u"orm['photo_contest.Promotion']"}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'waive_rights': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'photo_contest.promotion': {
            'Meta': {'object_name': 'Promotion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'})
        }
    }

    complete_apps = ['photo_contest']
