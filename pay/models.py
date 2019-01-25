# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from pay.validators import csv_file_validator, activation_time_validate
import hashlib, binascii, requests, json

import datetime

class Carrier(models.Model):
    nameid = models.CharField(max_length=40)
    description = models.CharField(max_length=40,default="")
    rate = models.CharField(max_length=3)

    def __str__(self):
        return self.nameid

    class Meta:
        managed = True
        db_table = 'Carrier'


class RateDeck(models.Model):
    carrier = models.ForeignKey(Carrier,on_delete=models.CASCADE)
    uploadday = models.DateTimeField()
    efectiveday= models.DateTimeField()
    filename = models.FileField(default="",validators=[csv_file_validator])

    class Meta:
        managed = True
        db_table = 'RateDeck'
        verbose_name = 'Rate Deck'




class Cdrs(models.Model):
    cgrid = models.CharField(max_length=40)
    run_id = models.CharField(max_length=64)
    origin_host = models.CharField(max_length=64)
    source = models.CharField(max_length=64)
    origin_id = models.CharField(max_length=64)
    tor = models.CharField(max_length=16)
    request_type = models.CharField(max_length=24)
    tenant = models.CharField(max_length=64)
    category = models.CharField(max_length=32)
    account = models.CharField(max_length=128)
    subject = models.CharField(max_length=128)
    destination = models.CharField(max_length=128)
    setup_time = models.DateTimeField()
    answer_time = models.DateTimeField()
    usage = models.IntegerField()
    extra_fields = models.TextField()
    cost_source = models.CharField(max_length=64)
    cost = models.DecimalField(max_digits=20, decimal_places=4)
    cost_details = models.TextField(blank=True, null=True)
    extra_info = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cdrs'
        unique_together = (('cgrid', 'run_id', 'origin_id'),)
        verbose_name = 'cdr'


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class SmCosts(models.Model):
    cgrid = models.CharField(max_length=40)
    run_id = models.CharField(max_length=64)
    origin_host = models.CharField(max_length=64)
    origin_id = models.CharField(max_length=64)
    cost_source = models.CharField(max_length=64)
    usage = models.DecimalField(max_digits=30, decimal_places=9)
    cost_details = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sm_costs'
        unique_together = (('cgrid', 'run_id'),)


class TpAccountActions(models.Model):
    tpid = models.CharField(max_length=64, default='CgratesPay')
    loadid = models.CharField(max_length=64, default='CSVLOAD')
    tenant = models.CharField(max_length=64)
    account = models.CharField(max_length=64)
    action_plan_tag = models.CharField(max_length=64, blank=True, null=True)
    action_triggers_tag = models.CharField(max_length=64, blank=True, null=True)
    allow_negative = models.IntegerField(choices=((1,'true'),(0,'false'),))
    disabled = models.IntegerField(choices=((1,'true'),(0,'false'),))
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_account_actions'
        unique_together = (('tpid', 'loadid', 'tenant', 'account'),)
        verbose_name = 'Account Action'


class TpActionPlans(models.Model):
    tpid = models.CharField(max_length=64,default='CgratesPay')
    tag = models.CharField(max_length=64)
    actions_tag = models.CharField(max_length=64)
    timing_tag = models.CharField(max_length=64,default='*asap')
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_action_plans'
        unique_together = (('tpid', 'tag', 'actions_tag'),)
        verbose_name = 'Action Plan'


class TpActionTriggers(models.Model):
    THRESHOLDTYPE = (
        ('*min_counter','*min_counter'),
        ('*max_counter','*max_counter'),
        ('*min_balance','*min_balance'),
        ('*max_balance','*max_balance'),
        ('*min_asr','*min_asr'),
        ('*max_asr','*max_asr'),
        ('*min_acd','*min_acd'),
        ('*max_acd','*max_acd'),
        ('*min_acc','*min_acc'),
        ('*max_acc','*max_acc'),
        ('*min_tcc','*min_tcc'),
        ('*max_tcc','*max_tcc'),
        ('*min_tcd','*min_tcd'),
        ('*max_tcd','*max_tcd'),
        ('*min_pdd','*min_pdd'),
        ('*max_pdd','*max_pdd'),
    )
    BalanceTag = (
        ('MONETARY','MONETARY'),
        ('SMS','SMS'),
        ('INTERNET','INTERNET'),
        ('INTERNET_TIME','INTERNET_TIME'),
        ('MINUTES','MINUTES'),
    )

    BalanceType = (
        ('*voice','*voice'),
        ('*sms','*sms'),
        ('*data','*data'),
        ('*monetary','*monetary'),
    )

    INBOUND = '*in'
    OUTBOUND = '*out'
    DIRECTION = (
        (INBOUND,'*in'),
        (OUTBOUND,'*out'),
    )

    tpid = models.CharField(max_length=64, default='CgratesPay')
    tag = models.CharField(max_length=64)
    unique_id = models.CharField(max_length=64, blank=True)
    threshold_type = models.CharField(max_length=64,choices=THRESHOLDTYPE)
    threshold_value = models.DecimalField(default=0,max_digits=20, decimal_places=4,null=True, blank=True)
    recurrent = models.IntegerField(default=0,choices=((1,'True'),(0,'False')))
    min_sleep = models.CharField(default="0",max_length=16, null=True, blank=True)
    expiry_time = models.CharField(default="0001-01-01T00:00:00Z",max_length=24, blank=True)
    activation_time = models.CharField(default="0001-01-01T00:00:00Z",max_length=24, blank=True)
    balance_tag = models.CharField(max_length=64,choices=BalanceTag)
    balance_type = models.CharField(max_length=24,choices=BalanceType)
    balance_directions = models.CharField(max_length=8,choices=DIRECTION)
    balance_categories = models.CharField(max_length=32, blank=True)
    balance_destination_tags = models.CharField(max_length=64, blank=True)
    balance_rating_subject = models.CharField(max_length=64, blank=True)
    balance_shared_groups = models.CharField(max_length=64, blank=True)
    balance_expiry_time = models.CharField(default="0001-01-01T00:00:00Z",max_length=24, blank=True)
    balance_timing_tags = models.CharField(max_length=128, blank=True)
    balance_weight = models.CharField(default=0,max_length=10, blank=True)
    balance_blocker = models.CharField(default=0,choices=(('1','True'),('0','False')),max_length=5, blank=True)
    balance_disabled = models.CharField(default=0,choices=(('1','True'),('0','False')),max_length=5, blank=True)
    min_queued_items = models.IntegerField( default=0, blank=True)
    actions_tag = models.CharField(max_length=64)
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=0, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_action_triggers'
        unique_together = (('tpid', 'tag', 'balance_tag', 'balance_type', 'balance_directions', 'threshold_type', 'threshold_value', 'balance_destination_tags', 'actions_tag'),)
        verbose_name = 'Action Trigger'


class TpActions(models.Model):
    Action = (
        ('*allow_negative','*allow_negative'),
        ('*call_url','*call_url'),
        ('*call_url_async','*call_url_async'),
        ('*cdrlog','*cdrlog'),
        ('*debit','*debit'),
        ('*deny_negative','*deny_negative'),
        ('*disable_account','*disable_account'),
        ('*enable_account','*enable_account'),
        ('*log','*log'),
        ('*mail_async','*mail_async'),
        ('*reset_account','*reset_account'),
        ('*reset_counter','*reset_counter'),
        ('*reset_counters','*reset_counters'),
        ('*reset_triggers','*reset_triggers'),
        ('*set_recurrent','*set_recurrent'),
        ('*topup','*topup'),
        ('*topup_reset','*topup_reset'),
        ('*unset_recurrent','*unset_recurrent'),
        ('*unlimited','*unlimited')
    )

    BalanceType = (
        ('*voice','*voice'),
        ('*sms','*sms'),
        ('*data','*data'),
        ('*monetary','*monetary'),
    )

    INBOUND = '*in'
    OUTBOUND = '*out'
    DIRECTION = (
        (INBOUND,'*in'),
        (OUTBOUND,'*out'),
    )

    tpid = models.CharField(max_length=64, default='CgratesPay')
    tag = models.CharField(max_length=64,null=True, blank=True)
    action = models.CharField(max_length=24,choices=Action, blank=True)
    balance_tag = models.CharField(max_length=64, blank=True, default='')
    balance_type = models.CharField(max_length=24,choices=BalanceType, blank=True, default='')
    directions = models.CharField(max_length=8,choices=DIRECTION, blank=True, default='')
    units = models.CharField(default=0, max_length=256, blank=True)
    expiry_time = models.CharField(max_length=24, blank=True, default='')
    timing_tags = models.CharField(max_length=128, blank=True, default='')
    destination_tags = models.CharField(max_length=64, blank=True, default='')
    rating_subject = models.CharField(max_length=64, blank=True, default='')
    categories = models.CharField(max_length=32, blank=True, default='')
    shared_groups = models.CharField(max_length=64, blank=True, default='')
    balance_weight = models.CharField(default=0 ,max_length=10, blank=True)
    balance_blocker = models.CharField(max_length=5, blank=True,choices=(('true','true'),('false','false'),),default='false')
    balance_disabled = models.CharField(max_length=24, blank=True,choices=(('true','true'),('false','false'),),default='false')
    extra_parameters = models.CharField(max_length=256, blank=True)
    filter = models.CharField(max_length=256, blank=True, default='')
    weight = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_actions'
        unique_together = (('tpid', 'tag', 'action', 'balance_tag', 'balance_type', 'directions', 'expiry_time', 'timing_tags', 'destination_tags', 'shared_groups', 'balance_weight', 'weight'),)
        verbose_name = 'Action'


class TpAliases(models.Model):
    INBOUND = '*in'
    OUTBOUND = '*out'
    DIRECTION = (
        (INBOUND,'*in'),
        (OUTBOUND,'*out'),
    )
    tpid = models.CharField(max_length=64)
    direction = models.CharField(max_length=8,choices=DIRECTION)
    tenant = models.CharField(max_length=64)
    category = models.CharField(max_length=64)
    account = models.CharField(max_length=64)
    subject = models.CharField(max_length=64)
    destination_id = models.CharField(max_length=64)
    context = models.CharField(max_length=64)
    target = models.CharField(max_length=64)
    original = models.CharField(max_length=64)
    alias = models.CharField(max_length=64)
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_aliases'
        unique_together = (('tpid', 'direction', 'tenant', 'category', 'account', 'subject', 'context', 'target'),)
        verbose_name = 'Aliase'


class TpCdrStats(models.Model):
    METRICS = (
        ('ACC','ACC'),
        ('ACD','ACD'),
        ('ASR','ASR'),
        ('PDD','PDD'),
        ('TCC','TCC'),
        ('TCD','TCD')
    )
    tpid = models.CharField(max_length=64)
    tag = models.CharField(max_length=64)
    queue_length = models.IntegerField()
    time_window = models.CharField(max_length=8)
    save_interval = models.CharField(max_length=8)
    metrics = models.CharField(max_length=64,choices=METRICS)
    setup_interval = models.CharField(max_length=64,blank=True,null=True)
    tors = models.CharField(max_length=64, blank=True,null=True)
    cdr_hosts = models.CharField(max_length=64,blank=True,null=True)
    cdr_sources = models.CharField(max_length=64,blank=True,null=True)
    req_types = models.CharField(max_length=64,blank=True,null=True)
    directions = models.CharField(max_length=8,blank=True,null=True)
    tenants = models.CharField(max_length=64,blank=True,null=True)
    categories = models.CharField(max_length=32,blank=True,null=True)
    accounts = models.CharField(max_length=255,blank=True,null=True)
    subjects = models.CharField(max_length=64,blank=True,null=True)
    destination_ids = models.CharField(max_length=64,blank=True,null=True)
    pdd_interval = models.CharField(max_length=64,blank=True,null=True)
    usage_interval = models.CharField(max_length=64,blank=True,null=True)
    suppliers = models.CharField(max_length=64,blank=True,null=True)
    disconnect_causes = models.CharField(max_length=64,blank=True,null=True)
    mediation_runids = models.CharField(default="*default",max_length=64)
    rated_accounts = models.CharField(max_length=255,blank=True,null=True)
    rated_subjects = models.CharField(max_length=64,blank=True,null=True)
    cost_interval = models.CharField(default=0.0,max_length=24,blank=True,null=True)
    action_triggers = models.CharField(max_length=64,blank=True,null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_cdr_stats'
        verbose_name = 'Cdr Stat'


class TpDerivedChargers(models.Model):
    INBOUND = '*in'
    OUTBOUND = '*out'
    DIRECTION = (
        (INBOUND,'*in'),
        (OUTBOUND,'*out'),
    )

    REQUESTYPE = (
        ('^*prepaid','*prepaid'),
        ('^*postpaid','*postpaid'),
        ('^*pseudoprepaid','*pseudoprepaid'),
        ('^*rated','*rated')
    )
    tpid = models.CharField(max_length=64)
    loadid = models.CharField(max_length=64)
    direction = models.CharField(max_length=8,choices=DIRECTION)
    tenant = models.CharField(max_length=64)
    category = models.CharField(max_length=32)
    account = models.CharField(max_length=64)
    subject = models.CharField(max_length=64)
    destination_ids = models.CharField(max_length=64,blank=True,null=True)
    runid = models.CharField(max_length=24)
    run_filters = models.CharField(max_length=256, blank=True,null=True)
    req_type_field = models.CharField(default="^*rated",choices=REQUESTYPE,max_length=64)
    direction_field = models.CharField(default="*default",max_length=64)
    tenant_field = models.CharField(default="*default",max_length=64)
    category_field = models.CharField(default="*default",max_length=64)
    account_field = models.CharField(default="*default",max_length=64)
    subject_field = models.CharField(default="*default",max_length=64)
    destination_field = models.CharField(default="*default",max_length=64)
    setup_time_field = models.CharField(default="*default",max_length=64)
    pdd_field = models.CharField(default="*default",max_length=64)
    answer_time_field = models.CharField(default="*default",max_length=64)
    usage_field = models.CharField(default="*default",max_length=64)
    supplier_field = models.CharField(default="*default",max_length=64)
    disconnect_cause_field = models.CharField(default="*default",max_length=64)
    rated_field = models.CharField(default="*default",max_length=64)
    cost_field = models.CharField(default="*default",max_length=64)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_derived_chargers'
        verbose_name = 'Derived Charger'


class TpDestinationRates(models.Model):
    tpid = models.CharField(max_length=64)
    tag = models.CharField(max_length=64)
    destinations_tag = models.CharField(max_length=64)
    rates_tag = models.CharField(max_length=64)
    rounding_method = models.CharField(max_length=255)
    rounding_decimals = models.IntegerField()
    max_cost = models.DecimalField(max_digits=7, decimal_places=4)
    max_cost_strategy = models.CharField(max_length=16)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_destination_rates'
        unique_together = (('tpid', 'tag', 'destinations_tag'),)
        verbose_name = 'Destinations Rate'


class TpDestinations(models.Model):
    tpid = models.CharField(max_length=64,default='CgratesPay')
    tag = models.CharField(max_length=64)
    prefix = models.CharField(max_length=24,validators=[RegexValidator(regex='^(1[2-9]|[2-9])([0-9]{2})([2-9][0-9]{2})',message='The prefix will be valid'),])
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_destinations'
        unique_together = (('tpid', 'tag', 'prefix'),)
        verbose_name = 'Prefix'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.tag = 'USA_' + self.prefix
        super(TpDestinations, self).save()


class TpLcrRules(models.Model):
    STRATEGY = (
        ('*static','*static'),
        ('*lowest_cost','*lowest_cost'),
        ('*highest_cost','*highest_cost'),
        ('*qos_with_threshold','*qos_with_threshold'),
        ('*qos','*qos'),
        ('*load_distribution','*load_distribution')
    )

    INBOUND = '*in'
    OUTBOUND = '*out'
    DIRECTION = (
        (INBOUND,'*in'),
        (OUTBOUND,'*out'),
    )
    tpid = models.CharField(max_length=64)
    direction = models.CharField(max_length=8,choices=DIRECTION)
    tenant = models.CharField(max_length=64)
    category = models.CharField(max_length=32)
    account = models.CharField(max_length=64)
    subject = models.CharField(max_length=64)
    destination_tag = models.CharField(max_length=64)
    rp_category = models.CharField(max_length=32)
    strategy = models.CharField(max_length=18,choices=STRATEGY)
    strategy_params = models.CharField(max_length=256)
    activation_time = models.CharField(max_length=24)
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_lcr_rules'
        verbose_name = 'Lcr Rule'


class TpRates(models.Model):
    tpid = models.CharField(max_length=64)
    tag = models.CharField(max_length=64)
    connect_fee = models.DecimalField(max_digits=7, decimal_places=4)
    rate = models.DecimalField(max_digits=7, decimal_places=4)
    rate_unit = models.CharField(max_length=16,validators=[RegexValidator(regex='^[1-9][0-9]+$',message='The billing unit expressed in seconds'),])
    rate_increment = models.CharField(max_length=16,validators=[RegexValidator(regex='^[1-9][0-9]+$',message='This rate will apply in increments of duration'),])
    group_interval_start = models.CharField(max_length=16,validators=[RegexValidator(regex='^[0-9]+$',message='When the rate starts'),])
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_rates'
        unique_together = (('tpid', 'tag', 'group_interval_start'),)
        verbose_name = 'Rate'
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.tag = "RT_%sCNT" %(str(self.rate)[2:])
        self.rate_unit = self.rate_unit + 's'
        self.rate_increment = self.rate_increment + 's'
        self.group_interval_start = self.group_interval_start + 's'
        super(TpRates, self).save()

class TpRatingPlans(models.Model):
    tpid = models.CharField(max_length=64)
    tag = models.CharField(max_length=64)
    destrates_tag = models.CharField(max_length=64)
    timing_tag = models.CharField(max_length=64)
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_rating_plans'
        unique_together = (('tpid', 'tag', 'destrates_tag', 'timing_tag'),)
        verbose_name = 'Rating Plan'


class TpRatingProfiles(models.Model):
    INBOUND = '*in'
    OUTBOUND = '*out'
    DIRECTION = (
        (INBOUND,'*in'),
        (OUTBOUND,'*out'),
    )
    tpid = models.CharField(max_length=64, default='CgratesPay')
    loadid = models.CharField(max_length=64, default='CSVLOAD')
    direction = models.CharField(max_length=8,choices=DIRECTION,default=OUTBOUND)
    tenant = models.CharField(max_length=64)
    category = models.CharField(max_length=32)
    subject = models.CharField(max_length=64)
    activation_time = models.CharField(max_length=24, validators=[activation_time_validate])
    rating_plan_tag = models.CharField(max_length=64)
    fallback_subjects = models.CharField(max_length=64, blank=True, null=True)
    cdr_stat_queue_ids = models.CharField(max_length=64, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_rating_profiles'
        unique_together = (('tpid', 'loadid', 'tenant', 'category', 'direction', 'subject', 'activation_time'),)
        verbose_name = 'Rating Profile'


class TpResources(models.Model):
    p_k = models.AutoField(primary_key=True)
    tpid = models.CharField(max_length=64)
    tenant = models.CharField(max_length=64)
    id = models.CharField(max_length=64)
    filter_ids = models.CharField(max_length=16)
    activation_interval = models.CharField(max_length=64)
    usage_ttl = models.CharField(max_length=32)
    limit = models.CharField(max_length=64)
    allocation_message = models.CharField(max_length=64)
    blocker = models.IntegerField(choices=((1,'true'),(0,'false'),))
    stored = models.IntegerField(choices=((1,'true'),(0,'false'),))
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    threshold_ids = models.CharField(max_length=64)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_resources'
        unique_together = (('tpid', 'tenant', 'id', 'filter_ids'),)
        verbose_name = 'Resource'


class TpSharedGroups(models.Model):
    tpid = models.CharField(default='CgratesPay',max_length=64)
    tag = models.CharField(max_length=64)
    account = models.CharField(max_length=64, default='*any')
    strategy = models.CharField(max_length=24)
    rating_subject = models.CharField(max_length=24,null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_shared_groups'
        unique_together = (('tpid', 'tag', 'account', 'strategy', 'rating_subject'),)
        verbose_name = 'Shared Group'

class TpThresholds(models.Model):
    p_k = models.AutoField(primary_key=True)
    tpid = models.CharField(max_length=64)
    tenant = models.CharField(max_length=64)
    id = models.CharField(max_length=64)
    filter_ids = models.CharField(max_length=64)
    activation_interval = models.CharField(max_length=64)
    min_hits = models.IntegerField()
    min_sleep = models.CharField(max_length=16)
    blocker = models.IntegerField(choices=((1,'true'),(0,'false'),))
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    action_ids = models.CharField(max_length=64)
    async = models.IntegerField(choices=((1,'true'),(0,'false'),))
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_thresholds'
        unique_together = (('tpid', 'id', 'filter_ids'),)
        verbose_name = 'Threshold'


class TpTimings(models.Model):
    tpid = models.CharField(max_length=64, default='CgratesPay')
    tag = models.CharField(max_length=64)
    years = models.CharField(max_length=255)
    months = models.CharField(max_length=255)
    month_days = models.CharField(max_length=255)
    week_days = models.CharField(max_length=255)
    time = models.CharField(max_length=32)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_timings'
        unique_together = (('tpid', 'tag'),)
        verbose_name = 'Timing'


class TpUsers(models.Model):
    ATTRIBUTES = (
        ('SysUserName','SysUserName'),
        ('SysPassword','SysPassword'),
        ('Cli','Cli'),
        ('Account','Account'),
        ('Subject','Subject'),
        ('Uuid','Uuid'),
        ('SubscriberId','SubscriberId'),
        ('RequestType','RequestType'),
        ('SysUserName','SysUserName'),
        ('RifAttr','RifAttr')
    )
    tpid = models.CharField(max_length=64, default='CgratesPay')
    tenant = models.CharField(max_length=64)
    user_name = models.CharField(max_length=64)
    masked = models.IntegerField()
    attribute_name = models.CharField(max_length=64,choices=ATTRIBUTES)
    attribute_value = models.CharField(max_length=64)
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.attribute_name == 'SysPassword':
            password = hashlib.pbkdf2_hmac('sha1',str(self.attribute_value).encode('utf-8'), b'salt', 64)
            self.attribute_value = binascii.hexlify(password)
            super(TpUsers, self).save()
        else:
            super(TpUsers, self).save()

    def __str__(self):
        return self.tenant

    class Meta:
        managed = False
        db_table = 'tp_users'
        verbose_name = 'Cgrates User'

class User(AbstractUser):
    tenant = models.CharField(max_length=64, default='NetProviderSolutions')

    class Meta:
        verbose_name = 'User'

class Versions(models.Model):
    item = models.CharField(unique=True, max_length=64)
    version = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'versions'

class Filters(models.Model):
    FILTERS = (
        ('*string','*string'),
        ('*prefix','*prefix'),
        ('*timings','*timings'),
        ('*destinations','*destinations'),
        ('*rsr','*rsr'),
        ('*lt','*lt')
    )
    p_k = models.AutoField(primary_key=True)
    tpid = models.CharField(max_length=64,default='CgratesPay')
    tenant = models.CharField(max_length=64)
    id = models.CharField(max_length=64)
    filter_type = models.CharField(max_length=16,choices=FILTERS)
    filter_field_name = models.CharField(max_length=64)
    filter_field_values = models.CharField(max_length=256)
    activation_interval = models.CharField(max_length=64,blank=True,default="0000-01-01T00:00:00Z")
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_filters'
        verbose_name = 'Filter'

class TpSuppliers(models.Model):
    STRATEGY = (
        ('*static', '*static'),
        ('*lowest_cost', '*lowest_cost'),
        ('*highest_cost', '*highest_cost'),
        ('*qos_with_threshold', '*qos_with_threshold'),
        ('*qos', '*qos'),
        ('*load_distribution', '*load_distribution')
    )
    p_k = models.AutoField(primary_key=True)
    tpid= models.CharField(max_length=64, default='CgratesPay')
    tenant = models.CharField(max_length=64)
    id = models.CharField(max_length=64)
    filter_ids = models.CharField(max_length=64, blank=True)
    activation_interval = models.CharField(max_length=64,blank=True)
    sorting = models.CharField(max_length=32,choices=STRATEGY,blank=True)
    sorting_parameters = models.CharField(max_length=64,blank=True)
    supplier_id = models.CharField(max_length=32,blank=True)
    supplier_filter_ids = models.CharField(max_length=64,blank=True)
    supplier_account_ids = models.CharField(max_length=64,blank=True)
    supplier_ratingplan_ids = models.CharField(max_length=64,blank=True)
    supplier_resource_ids = models.CharField(max_length=64,blank=True)
    supplier_stat_ids = models.CharField(max_length=64,blank=True)
    supplier_weight= models.DecimalField(max_digits=8,decimal_places=2,blank=True)
    supplier_blocker = models.IntegerField(choices=((1,'true'),(0,'false'),),blank=True)
    supplier_parameters = models.CharField(max_length=64,blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2,blank=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_suppliers'
        verbose_name = 'Supplier'

class TpAttributes(models.Model):
    APPEND = (
        (1,'True'),
        (0,'False')
    )
    p_k = models.AutoField(primary_key=True)
    tpid= models.CharField(max_length=64, default='CgratesPay')
    tenant = models.CharField(max_length=64)
    id = models.CharField(max_length=64)
    contexts = models.CharField(max_length=64)
    filter_ids = models.CharField(max_length=64)
    activation_interval = models.CharField(max_length=64,blank=True,default='0000-01-01T00:00:00Z')
    field_name = models.CharField(max_length=64)
    initial = models.CharField(max_length=64, blank=True)
    substitute = models.CharField(max_length=64)
    append = models.IntegerField(choices=APPEND)
    blocker = models.IntegerField(choices=APPEND)
    weight = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'tp_attributes'
        verbose_name = 'Attribute'

class TpStats(models.Model):
    p_k  = models.AutoField(primary_key=True)
    tpid = models.CharField(max_length=64,default='CgratesPay')
    tenant = models.CharField(max_length=64)
    id = models.CharField(max_length=64)
    filter_ids  = models.CharField(max_length=64)
    activation_interval = models.CharField(max_length=64)
    queue_length = models.IntegerField()
    ttl = models.CharField(max_length=32)
    metrics = models.CharField(max_length=64)
    parameters = models.CharField(max_length=64)
    blocker = models.IntegerField()
    stored = models.IntegerField()
    weight = models.DecimalField(max_digits=8,decimal_places=2)
    min_items = models.IntegerField()
    threshold_ids = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = 'tp_stats'
        verbose_name = 'Stat'


class CgratesAPI:
    def __init__(self, server = settings.CGRATES_JSONRPC, head = settings.CGRATES_HEAD):
        self.server = server
        self.head = head

    def Query(self,payload):
        response = requests.post(self.server,headers = self.head,data=json.dumps(payload))
        return json.loads(response.content.decode('utf-8'))


    def GetAccount(self,Tenant,Account):
        payload = {"id":1,
               "method":"ApierV1.GetAccount",
               "params":[{
                   "Tenant": Tenant,
                   "Account": Account
               }]
        }
        return self.Query(payload)

    def SetBalance(self, Tenant='',Account='',BalanceType="*monetary", BalanceUUID='', BalanceID='', Directions='',
                   Value = 0, ExpiryTime= '', RatingSubject='', Categories='', DestinationIds='', TimingIds='', Weight=0,
                   SharedGroups='',Blocker=False, Disabled=False):
        payload = {"id":1,
                   "method":"ApierV1.SetBalance",
                   "params":[{
                       "Tenant":Tenant,
                       "Account":Account,
                       "BalanceUuid":BalanceUUID,
                       "BalanceId": BalanceID,
                       "BalanceType":BalanceType,
                       "Directions":Directions,
                       "Value":float(Value),
                       "ExpiryTime":ExpiryTime,
                       "RatingSubject":RatingSubject,
                       "Categories":Categories,
                       "DestinationIds":DestinationIds,
                       "TimingIds":TimingIds,
                       "Weight":Weight,
                       "SharedGroups":SharedGroups,
                       "Blocker":Blocker,
                       "Disabled":Disabled
                   }]
        }
        return self.Query(payload)

class Balance(CgratesAPI):
    Tenant          = ''         #string
    Account         = ''         #string
    BalanceUuid     = ''         #*string
    BalanceId       = ''         #*string
    BalanceType     = ''         #string
    Directions      = ''         #*string
    Value           = 0.0        #float64
    ExpiryTime      = ''         #*string
    RatingSubject   = ''         #*string
    Categories      = ''         #*string
    DestinationIds  = ''         #*string
    TimingIds       = ''         #*string
    Weight          = 0.0        #*float64
    SharedGroups    = ''         #*string
    Overwrite       = False      #bool // When true it will reset if the balance is already there
    Blocker         = False      #*bool
    Disabled        = False      #*bool
    UnitCounters    = ''         #Unit counter
    json            = {}

    def __init__(self,Tenant='', Account=''):
        self.server=settings.CGRATES_JSONRPC
        self.head=settings.CGRATES_HEAD
        json = self.GetAccount(Tenant,Account)
        self.Tenant = Tenant
        self.Account = Account
        self.BalanceUuid = json['result']['BalanceMap']['*monetary*out'][0]['Uuid']
        self.BalanceId = json['result']['BalanceMap']['*monetary*out'][0]['Id']
        self.BalanceType = json['result']['UnitCounters'][0]['BalanceType']
        self.Directions = json['result']['UnitCounters'][0]['Direction']
        self.Value = json['result']['BalanceMap']['*monetary*out'][0]['Value']
        self.ExpiryTime = json['result']['BalanceMap']['*monetary*out'][0]['ExpirationDate']
        self.RatingSubject = json['result']['BalanceMap']['*monetary*out'][0]['RatingSubject']
        self.Categories = json['result']['BalanceMap']['*monetary*out'][0]['Category']
        self.DestinationIds=json['result']['BalanceMap']['*monetary*out'][0]['DestinationIds']
        self.TimingIds=json['result']['BalanceMap']['*monetary*out'][0]['TimingIDs']
        self.Weight=json['result']['BalanceMap']['*monetary*out'][0]['Weight']
        self.SharedGroups=json['result']['BalanceMap']['*monetary*out'][0]['SharedGroup']
        self.Disabled = json['result']['BalanceMap']['*monetary*out'][0]['Disabled']
        self.UnitCounters = json['result']['UnitCounters'][0]['Balances'][0]['Value']

    def GetAccount(self, Tenant, Account):
        payload = {
            "id": 1,
            "method": "ApierV1.GetAccount",
            "params": [{
                "Tenant": Tenant,
                "Account": Account
            }]
        }
        return self.Query(payload)

    def SetBalance(self, Tenant='',Account='',BalanceType="*monetary", BalanceUUID='', BalanceID='', Directions='',
                   Value = 0, ExpiryTime= '', RatingSubject='', Categories='', DestinationIds='', TimingIds='', Weight=0,
                   SharedGroups='',Blocker=False, Disabled=False):
        self.Tenant = Tenant
        self.Account = Account
        self.BalanceType = BalanceType
        self.BalanceUuid = BalanceUUID
        self.BalanceId = BalanceID
        self.Directions = Directions
        self.Value = Value
        self.ExpiryTime = ExpiryTime
        self.RatingSubject = RatingSubject
        self.Categories=Categories
        self.DestinationIds = DestinationIds
        self.TimingIds = TimingIds
        self.Weight = Weight
        self.SharedGroups  =SharedGroups
        self.Blocker = Blocker
        self.Disabled = Disabled

        payload = {"id":1,
                   "method":"ApierV1.SetBalance",
                   "params":[{
                       "Tenant":self.Tenant,
                       "Account":self.Account,
                       "BalanceUuid":self.BalanceUuid,
                       "BalanceId": self.BalanceId,
                       "BalanceType":self.BalanceType,
                       "Directions":self.Directions,
                       "Value":float(self.Value),
                       "ExpiryTime":self.ExpiryTime,
                       "RatingSubject":self.RatingSubject,
                       "Categories":self.Categories,
                       "DestinationIds":self.DestinationIds,
                       "TimingIds":self.TimingIds,
                       "Weight":self.Weight,
                       "SharedGroups":self.SharedGroups,
                       "Blocker":self.Blocker,
                       "Disabled":self.Disabled
                   }]
        }
        return self.Query(payload)

    def AddBalance(self, Tenant='',Account='',BalanceUuid='',BalanceId='',BalanceType="*monetary",Directions='',Value=0,ExpiryTime='',RatingSubject='',
                   Categories='',DestinationIds='',TimingIds='',Weight='',SharedGroups='',Overwrite=False,Blocker=False,Disabled=False):
        self.Tenant=Tenant
        self.Account=Account
        self.BalanceUuid=BalanceUuid
        self.BalanceId=BalanceId
        self.BalanceType=BalanceType
        self.Directions=Directions
        self.Value=Value
        self.ExpiryTime=ExpiryTime
        self.RatingSubject=RatingSubject
        self.Categories=Categories
        self.DestinationIds=DestinationIds
        self.TimingIds=TimingIds
        self.Weight=Weight
        self.SharedGroups=SharedGroups
        self.Overwrite=Overwrite
        self.Blocker=Blocker
        self.Disabled=Disabled

        payload = {"id":1,
                   "method":"ApierV1.AddBalance",
                   "params":[{
                       "Tenant":self.Tenant,
                       "Account":self.Account,
                       "BalanceUuid":self.BalanceUuid,
                       "BalanceId":self.BalanceId,
                       "BalanceType":self.BalanceType,
                       "Directions":self.Directions,
                       "Value":self.Value,
                       "ExpiryTime":self.ExpiryTime,
                       "RatingSubject":self.RatingSubject,
                       "Categories":self.Categories,
                       "DestinationIds":self.DestinationIds,
                       "TimingIds":self.TimingIds,
                       "Weight":self.Weight,
                       "SharedGroups":self.SharedGroups,
                       "Overwrite":self.Overwrite,
                       "Blocker":self.Blocker,
                       "Disabled":self.Disabled
                   }]
        }
        return self.Query(payload)




