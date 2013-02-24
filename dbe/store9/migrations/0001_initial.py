# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'AddressBook'
        db.create_table(u'store9_addressbook', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(related_name='addressbook', to=orm['store9.Contact'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('addressee', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('street1', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('street2', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=30)),
            ('is_default_shipping', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_default_billing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('country_name', self.gf('django.db.models.fields.CharField')(max_length=80, blank=True)),
        ))
        db.send_create_signal(u'store9', ['AddressBook'])

        # Adding model 'Contact'
        db.create_table(u'store9_contact', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], unique=True, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(max_length=500, blank=True)),
            ('create_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=15, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=30, null=True)),
            ('organization_name', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal(u'store9', ['Contact'])

        # Adding model 'Product'
        db.create_table(u'store9_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_description', self.gf('django.db.models.fields.TextField')(default='', max_length=200, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('length', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=6, decimal_places=0, blank=True)),
            ('sequence', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('contact', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='contacts', null=True, to=orm['store9.Contact'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owns', null=True, to=orm['store9.Contact'])),
            ('royalty_rate', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=2, decimal_places=2, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(max_length=500, blank=True)),
        ))
        db.send_create_signal(u'store9', ['Product'])

        # Adding model 'Item'
        db.create_table(u'store9_item', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('date_added', self.gf('django.db.models.fields.DateField')(auto_now_add=True, null=True, blank=True)),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('sort_order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sequence', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(max_length=500, blank=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store9.Product'], null=True, blank=True)),
            ('item_id', self.gf('django.db.models.fields.TextField')(max_length=12, primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
        ))
        db.send_create_signal(u'store9', ['Item'])

        # Adding M2M table for field variation_of on 'Item'
        db.create_table(u'store9_item_variation_of', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_item', models.ForeignKey(orm[u'store9.item'], null=False)),
            ('to_item', models.ForeignKey(orm[u'store9.item'], null=False))
        ))
        db.create_unique(u'store9_item_variation_of', ['from_item_id', 'to_item_id'])

        # Adding model 'CartItem'
        db.create_table(u'store9_cartitem', (
            ('date_added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['store9.Item'])),
            ('cart_item_id', self.gf('django.db.models.fields.TextField')(max_length=12, primary_key=True)),
        ))
        db.send_create_signal(u'store9', ['CartItem'])

        # Adding model 'Order'
        db.create_table(u'store9_order', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('items', self.gf('django.db.models.fields.TextField')(max_length=20000, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(max_length=500, blank=True)),
            ('shipped', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('po_num', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('order_num', self.gf('django.db.models.fields.CharField')(max_length=8, primary_key=True)),
        ))
        db.send_create_signal(u'store9', ['Order'])


    def backwards(self, orm):
        
        # Deleting model 'AddressBook'
        db.delete_table(u'store9_addressbook')

        # Deleting model 'Contact'
        db.delete_table(u'store9_contact')

        # Deleting model 'Product'
        db.delete_table(u'store9_product')

        # Deleting model 'Item'
        db.delete_table(u'store9_item')

        # Removing M2M table for field variation_of on 'Item'
        db.delete_table('store9_item_variation_of')

        # Deleting model 'CartItem'
        db.delete_table(u'store9_cartitem')

        # Deleting model 'Order'
        db.delete_table(u'store9_order')


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
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 24, 14, 10, 24, 775249)'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 2, 24, 14, 10, 24, 774754)'}),
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
        u'store9.addressbook': {
            'Meta': {'object_name': 'AddressBook'},
            'addressee': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'addressbook'", 'to': u"orm['store9.Contact']"}),
            'country_name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_default_billing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_default_shipping': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'street1': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'street2': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
        },
        u'store9.cartitem': {
            'Meta': {'ordering': "['date_added']", 'object_name': 'CartItem'},
            'cart_item_id': ('django.db.models.fields.TextField', [], {'max_length': '12', 'primary_key': 'True'}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store9.Item']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'store9.contact': {
            'Meta': {'object_name': 'Contact'},
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'organization_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'store9.item': {
            'Meta': {'ordering': "('sort_order', 'name', '-date_added')", 'object_name': 'Item'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'item_id': ('django.db.models.fields.TextField', [], {'max_length': '12', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['store9.Product']", 'null': 'True', 'blank': 'True'}),
            'sequence': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'variation_of': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'variation_of_rel_+'", 'null': 'True', 'to': u"orm['store9.Item']"})
        },
        u'store9.order': {
            'Meta': {'object_name': 'Order'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'items': ('django.db.models.fields.TextField', [], {'max_length': '20000', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'order_num': ('django.db.models.fields.CharField', [], {'max_length': '8', 'primary_key': 'True'}),
            'po_num': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'shipped': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'store9.product': {
            'Meta': {'ordering': "['-date_added']", 'object_name': 'Product'},
            'contact': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'contacts'", 'null': 'True', 'to': u"orm['store9.Contact']"}),
            'date_added': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'length': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '6', 'decimal_places': '0', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owns'", 'null': 'True', 'to': u"orm['store9.Contact']"}),
            'royalty_rate': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '2', 'decimal_places': '2', 'blank': 'True'}),
            'sequence': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['store9']
