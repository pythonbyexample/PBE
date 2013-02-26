# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Language'
        db.create_table('langapp_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name_eng', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name_native', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('iso639_1', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('iso639_2T', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('iso639_2B', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('iso639_X', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('direction', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('text_align', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('langapp', ['Language'])

        # Adding model 'Flag'
        db.create_table('langapp_flag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('icon', self.gf('django.db.models.fields.files.ImageField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('information', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('langapp', ['Flag'])

        # Adding model 'RIDocumentation'
        db.create_table('langapp_ridocumentation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=255)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2000)),
        ))
        db.send_create_signal('langapp', ['RIDocumentation'])

        # Adding model 'RIEmploymentHistory'
        db.create_table('langapp_riemploymenthistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('employer', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('position_title', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('position_level', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('work_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.TypeWork'])),
            ('commencement_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('completion_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('duties', self.gf('django.db.models.fields.TextField')(max_length=2000, null=True, blank=True)),
        ))
        db.send_create_signal('langapp', ['RIEmploymentHistory'])

        # Adding model 'UserSettings'
        db.create_table('langapp_usersettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('primary_language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='setting_languages', to=orm['langapp.Language'])),
            ('resume_style', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.TypeResumeStyle'])),
            ('display_primary_language', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_mutiple_languages', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('display_single_language', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('primary_virtual_keyboard_language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('display_primary_virtual_keyboard', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('langapp', ['UserSettings'])

        # Adding model 'LanguageProfile'
        db.create_table('langapp_languageprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('profile_language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('languages', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_intl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_eng', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_native', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('flag', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Flag'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('years_experience', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('language_competency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.TypeLanguageCompetency'])),
            ('competency_user_desc', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('certification_level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.TypeLanguageCertification'])),
            ('certification_user_desc', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('certification_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('spoken_level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.TypeLanguageSpoken'])),
            ('spoken_level_user_desc', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('written_level', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.TypeLanguageWritten'])),
            ('written_level_user_desc', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('langapp', ['LanguageProfile'])

        # Adding model 'TypeIndustrySector'
        db.create_table('langapp_typeindustrysector', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('description_intl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_eng', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('langapp', ['TypeIndustrySector'])

        # Adding model 'TypeLanguageCertification'
        db.create_table('langapp_typelanguagecertification', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('description_intl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_eng', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('langapp', ['TypeLanguageCertification'])

        # Adding model 'TypeLanguageCompetency'
        db.create_table('langapp_typelanguagecompetency', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('description_intl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_eng', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('langapp', ['TypeLanguageCompetency'])

        # Adding model 'TypeLanguageSpoken'
        db.create_table('langapp_typelanguagespoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('description_intl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_eng', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('langapp', ['TypeLanguageSpoken'])

        # Adding model 'TypeLanguageWritten'
        db.create_table('langapp_typelanguagewritten', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('description_intl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_eng', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('langapp', ['TypeLanguageWritten'])

        # Adding model 'TypeWork'
        db.create_table('langapp_typework', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('description_intl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_eng', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('langapp', ['TypeWork'])

        # Adding model 'TypeResumeStyle'
        db.create_table('langapp_typeresumestyle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
            ('style', self.gf('django.db.models.fields.IntegerField')()),
            ('name_intl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('name_eng', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_intl', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description_eng', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('langapp', ['TypeResumeStyle'])

        # Adding model 'UserLanguage'
        db.create_table('langapp_userlanguage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
        ))
        db.send_create_signal('langapp', ['UserLanguage'])

        # Adding model 'LanguageNativeList'
        db.create_table('langapp_languagenativelist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['langapp.Language'])),
        ))
        db.send_create_signal('langapp', ['LanguageNativeList'])


    def backwards(self, orm):
        
        # Deleting model 'Language'
        db.delete_table('langapp_language')

        # Deleting model 'Flag'
        db.delete_table('langapp_flag')

        # Deleting model 'RIDocumentation'
        db.delete_table('langapp_ridocumentation')

        # Deleting model 'RIEmploymentHistory'
        db.delete_table('langapp_riemploymenthistory')

        # Deleting model 'UserSettings'
        db.delete_table('langapp_usersettings')

        # Deleting model 'LanguageProfile'
        db.delete_table('langapp_languageprofile')

        # Deleting model 'TypeIndustrySector'
        db.delete_table('langapp_typeindustrysector')

        # Deleting model 'TypeLanguageCertification'
        db.delete_table('langapp_typelanguagecertification')

        # Deleting model 'TypeLanguageCompetency'
        db.delete_table('langapp_typelanguagecompetency')

        # Deleting model 'TypeLanguageSpoken'
        db.delete_table('langapp_typelanguagespoken')

        # Deleting model 'TypeLanguageWritten'
        db.delete_table('langapp_typelanguagewritten')

        # Deleting model 'TypeWork'
        db.delete_table('langapp_typework')

        # Deleting model 'TypeResumeStyle'
        db.delete_table('langapp_typeresumestyle')

        # Deleting model 'UserLanguage'
        db.delete_table('langapp_userlanguage')

        # Deleting model 'LanguageNativeList'
        db.delete_table('langapp_languagenativelist')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 13, 10, 23, 52, 802238)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 13, 10, 23, 52, 802159)'}),
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
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'information': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"})
        },
        'langapp.language': {
            'Meta': {'object_name': 'Language'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
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
            'certification_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.TypeLanguageCertification']"}),
            'certification_user_desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'competency_user_desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_intl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_native': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'flag': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Flag']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language_competency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.TypeLanguageCompetency']"}),
            'languages': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'profile_language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.Language']"}),
            'spoken_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.TypeLanguageSpoken']"}),
            'spoken_level_user_desc': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'written_level': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['langapp.TypeLanguageWritten']"}),
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
            'description_eng': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'description_intl': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
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
