# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'ImageProfile', fields ['email_profile']
        db.delete_unique(u'photo_contest_imageprofile', ['email_profile_id'])

        # Deleting field 'ImageProfile.promotion'
        db.delete_column(u'photo_contest_imageprofile', 'promotion_id')

        # Changing field 'ImageProfile.caption'
        db.alter_column(u'photo_contest_imageprofile', 'caption', self.gf('django.db.models.fields.CharField')(max_length=140, null=True))

        # Changing field 'ImageProfile.email_profile'
        db.alter_column(u'photo_contest_imageprofile', 'email_profile_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['photo_contest.EmailProfile']))


    def backwards(self, orm):
        
        # Adding field 'ImageProfile.promotion'
        db.add_column(u'photo_contest_imageprofile', 'promotion', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='images', to=orm['photo_contest.Promotion']), keep_default=False)

        # Changing field 'ImageProfile.caption'
        db.alter_column(u'photo_contest_imageprofile', 'caption', self.gf('django.db.models.fields.CharField')(max_length=150, null=True))

        # Changing field 'ImageProfile.email_profile'
        db.alter_column(u'photo_contest_imageprofile', 'email_profile_id', self.gf('django.db.models.fields.related.OneToOneField')(unique=True, to=orm['photo_contest.EmailProfile']))

        # Adding unique constraint on 'ImageProfile', fields ['email_profile']
        db.create_unique(u'photo_contest_imageprofile', ['email_profile_id'])


    models = {
        u'photo_contest.emailprofile': {
            'Meta': {'object_name': 'EmailProfile'},
            'activation_key': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'confirm_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'photo_contest.imageprofile': {
            'Meta': {'ordering': "['created']", 'object_name': 'ImageProfile'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'banned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'birthday': ('django.db.models.fields.DateField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'caption': ('django.db.models.fields.CharField', [], {'max_length': '140', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'images'", 'to': u"orm['photo_contest.EmailProfile']"}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'personal_info': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '14', 'null': 'True', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'thumbnail': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        u'photo_contest.promotion': {
            'Meta': {'object_name': 'Promotion'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '70'})
        }
    }

    complete_apps = ['photo_contest']
