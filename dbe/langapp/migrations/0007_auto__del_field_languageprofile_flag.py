# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'LanguageProfile.flag'
        db.delete_column('langapp_languageprofile', 'flag_id')


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'LanguageProfile.flag'
        raise RuntimeError("Cannot reverse this migration. 'LanguageProfile.flag' and its values cannot be restored.")


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 13, 14, 25, 33, 518856)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 13, 14, 25, 33, 518727)'}),
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
        'langapp.flag': {
            'Meta': {'object_name': 'Flag'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'information': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"})
        },
        'langapp.language': {
            'Meta': {'object_name': 'Language'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'direction': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'iso639_1': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'iso639_2B': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'iso639_2T': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'iso639_X': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'name_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_native': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'text_align': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'langapp.languagenativelist': {
            'Meta': {'object_name': 'LanguageNativeList'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"})
        },
        'langapp.languageprofile': {
            'Meta': {'object_name': 'LanguageProfile'},
            'certification_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'certification_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.TypeLanguageCertification']", 'null': 'True', 'blank': 'True'}),
            'certification_user_desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'competency_user_desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_intl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_competency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.TypeLanguageCompetency']", 'null': 'True', 'blank': 'True'}),
            'languages': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'profile_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'spoken_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.TypeLanguageSpoken']", 'null': 'True', 'blank': 'True'}),
            'spoken_level_user_desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'written_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.TypeLanguageWritten']", 'null': 'True', 'blank': 'True'}),
            'written_level_user_desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'years_experience': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'})
        },
        'langapp.ridocumentation': {
            'Meta': {'object_name': 'RIDocumentation'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'langapp.riemploymenthistory': {
            'Meta': {'object_name': 'RIEmploymentHistory'},
            'commencement_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'completion_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'duties': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'null': 'True', 'blank': 'True'}),
            'employer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'position_level': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'position_title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'work_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.TypeWork']"})
        },
        'langapp.typeindustrysector': {
            'Meta': {'object_name': 'TypeIndustrySector'},
            'description_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_intl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'ordering': ('django.db.models.fields.IntegerField', [], {})
        },
        'langapp.typelanguagecertification': {
            'Meta': {'object_name': 'TypeLanguageCertification'},
            'description_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_intl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'ordering': ('django.db.models.fields.IntegerField', [], {})
        },
        'langapp.typelanguagecompetency': {
            'Meta': {'object_name': 'TypeLanguageCompetency'},
            'description_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_intl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'ordering': ('django.db.models.fields.IntegerField', [], {})
        },
        'langapp.typelanguagespoken': {
            'Meta': {'object_name': 'TypeLanguageSpoken'},
            'description_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_intl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'ordering': ('django.db.models.fields.IntegerField', [], {})
        },
        'langapp.typelanguagewritten': {
            'Meta': {'object_name': 'TypeLanguageWritten'},
            'description_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_intl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'ordering': ('django.db.models.fields.IntegerField', [], {})
        },
        'langapp.typeresumestyle': {
            'Meta': {'object_name': 'TypeResumeStyle'},
            'description_eng': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description_intl': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'name_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name_intl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'style': ('django.db.models.fields.IntegerField', [], {})
        },
        'langapp.typework': {
            'Meta': {'object_name': 'TypeWork'},
            'description_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_intl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'ordering': ('django.db.models.fields.IntegerField', [], {})
        },
        'langapp.userlanguage': {
            'Meta': {'object_name': 'UserLanguage'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'langapp.usersettings': {
            'Meta': {'object_name': 'UserSettings'},
            'display_mutiple_languages': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_primary_language': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_primary_virtual_keyboard': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'display_single_language': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'primary_language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'setting_languages'", 'to': "orm['langapp.Language']"}),
            'primary_virtual_keyboard_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'resume_style': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.TypeResumeStyle']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['langapp']
