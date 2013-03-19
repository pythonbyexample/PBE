# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Milestone'
        db.create_table(u'medtrics_milestone', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
        ))
        db.send_create_signal(u'medtrics', ['Milestone'])

        # Adding model 'MedForm'
        db.create_table(u'medtrics_medform', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=60)),
        ))
        db.send_create_signal(u'medtrics', ['MedForm'])

        # Adding model 'FormSubmission'
        db.create_table(u'medtrics_formsubmission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='submissions', null=True, to=orm['auth.User'])),
            ('form', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='submissions', null=True, to=orm['medtrics.MedForm'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'medtrics', ['FormSubmission'])

        # Adding model 'Section'
        db.create_table(u'medtrics_section', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=300, null=True, blank=True)),
            ('medform', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sections', null=True, to=orm['medtrics.MedForm'])),
        ))
        db.send_create_signal(u'medtrics', ['Section'])

        # Adding model 'Question'
        db.create_table(u'medtrics_question', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('choices', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('answer_type', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('max_length', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='questions', null=True, to=orm['medtrics.Section'])),
        ))
        db.send_create_signal(u'medtrics', ['Question'])

        # Adding unique constraint on 'Question', fields ['section', 'order']
        db.create_unique(u'medtrics_question', ['section_id', 'order'])

        # Adding M2M table for field milestone on 'Question'
        db.create_table(u'medtrics_question_milestone', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('question', models.ForeignKey(orm[u'medtrics.question'], null=False)),
            ('milestone', models.ForeignKey(orm[u'medtrics.milestone'], null=False))
        ))
        db.create_unique(u'medtrics_question_milestone', ['question_id', 'milestone_id'])

        # Adding model 'Answer'
        db.create_table(u'medtrics_answer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('answer', self.gf('django.db.models.fields.CharField')(max_length=300, null=True, blank=True)),
            ('text_answer', self.gf('django.db.models.fields.TextField')(max_length=3000, null=True, blank=True)),
            ('num_answer', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('question', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='answers', null=True, to=orm['medtrics.Question'])),
            ('submission', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='answers', null=True, to=orm['medtrics.FormSubmission'])),
        ))
        db.send_create_signal(u'medtrics', ['Answer'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Question', fields ['section', 'order']
        db.delete_unique(u'medtrics_question', ['section_id', 'order'])

        # Deleting model 'Milestone'
        db.delete_table(u'medtrics_milestone')

        # Deleting model 'MedForm'
        db.delete_table(u'medtrics_medform')

        # Deleting model 'FormSubmission'
        db.delete_table(u'medtrics_formsubmission')

        # Deleting model 'Section'
        db.delete_table(u'medtrics_section')

        # Deleting model 'Question'
        db.delete_table(u'medtrics_question')

        # Removing M2M table for field milestone on 'Question'
        db.delete_table('medtrics_question_milestone')

        # Deleting model 'Answer'
        db.delete_table(u'medtrics_answer')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 3, 15, 11, 25, 41, 175631)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 3, 15, 11, 25, 41, 174877)'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'medtrics.answer': {
            'Meta': {'ordering': "['question__section__order', 'question__order']", 'object_name': 'Answer'},
            'answer': ('django.db.models.fields.CharField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_answer': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'question': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'answers'", 'null': 'True', 'to': u"orm['medtrics.Question']"}),
            'submission': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'answers'", 'null': 'True', 'to': u"orm['medtrics.FormSubmission']"}),
            'text_answer': ('django.db.models.fields.TextField', [], {'max_length': '3000', 'null': 'True', 'blank': 'True'})
        },
        u'medtrics.formsubmission': {
            'Meta': {'ordering': "['user', 'created']", 'object_name': 'FormSubmission'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submissions'", 'null': 'True', 'to': u"orm['medtrics.MedForm']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'submissions'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'medtrics.medform': {
            'Meta': {'object_name': 'MedForm'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '60'})
        },
        u'medtrics.milestone': {
            'Meta': {'object_name': 'Milestone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'})
        },
        u'medtrics.question': {
            'Meta': {'unique_together': "[['section', 'order']]", 'object_name': 'Question'},
            'answer_type': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'choices': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_length': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'milestone': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['medtrics.Milestone']", 'null': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'questions'", 'null': 'True', 'to': u"orm['medtrics.Section']"})
        },
        u'medtrics.section': {
            'Meta': {'ordering': "('order',)", 'object_name': 'Section'},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '300', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'medform': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sections'", 'null': 'True', 'to': u"orm['medtrics.MedForm']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'order': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['medtrics']
