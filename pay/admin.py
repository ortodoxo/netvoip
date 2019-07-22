from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db import connection

# Register your models here.
from pay.models import TpDestinations,TpRates,Carrier,RateDeck,TpDestinationRates,TpRatingPlans,TpRatingProfiles, \
    TpAccountActions, TpActionTriggers, TpTimings, TpActionPlans, TpActions, TpChargers, TpSharedGroups, \
    TpResources, Filters, TpSuppliers, TpAttributes, TpThresholds, Cdrs, TpStats, User
from pay.forms import CreateTpRatingProfiles, CreateTpAccountActions, CreateTpTimings, CreateTpActionTriggers,\
    CreateTpActionPlans, CreateChargers, CreateTpSharedGroups, \
    CreateTpSupplier, CreateTpFilter, CreateTpAttributes, CreateResource, CreateThreshold, CreateStats

class DestinationsAdmin(admin.ModelAdmin):
    list_display = ('tpid','tag','prefix')
    search_fields = ['tag','prefix']
    fields = ('prefix',)

class RatesAdmin(admin.ModelAdmin):
    list_display = ('tag','connect_fee','rate','rate_unit','rate_increment','group_interval_start')
    search_fields = ['tag','rate']
    fields = ('connect_fee','rate','rate_unit','rate_increment','group_interval_start')

class CarrierAdmin(admin.ModelAdmin):
    list_display = ('nameid','description','rate')

class RateDeckAdmin(admin.ModelAdmin):
    list_display = ('carrier','uploadday','efectiveday')

class DestinationRatesAdmin(admin.ModelAdmin):
    list_display = ('tag','destinations_tag','rates_tag','rounding_method','rounding_decimals','max_cost','max_cost_strategy')
    search_fields = ['tag','destinations_tag','rates_tag']

class RatingPlansAdmin(admin.ModelAdmin):
    list_display = ('tag','destrates_tag','timing_tag','weight')
    search_fields = ('tag','destrates_tag','timing_tag','weight')

class RatingProfile(admin.ModelAdmin):
    list_display = ('tenant','category','subject','activation_time','rating_plan_tag')
    fields = ('tenant','category','subject','activation_time','rating_plan_tag','fallback_subjects')
    search_fields = ('tenant','category','subject','activation_time','rating_plan_tag','fallback_subjects')
    form = CreateTpRatingProfiles

class AccountActions(admin.ModelAdmin):
    list_display = ('tenant','account','action_plan_tag','action_triggers_tag','allow_negative','disabled')
    fields = ('tenant','account','action_plan_tag','action_triggers_tag','allow_negative','disabled')
    search_fields = ('tenant','account','action_plan_tag','action_triggers_tag','allow_negative','disabled')
    form = CreateTpAccountActions

class ActionTriggers(admin.ModelAdmin):
    list_display = ('tag', 'unique_id', 'threshold_type', 'threshold_value', 'recurrent', 'min_sleep', 'expiry_time', 'activation_time', 'balance_tag', 'balance_type', 'balance_categories', 'balance_destination_tags', 'balance_rating_subject', 'balance_shared_groups', 'balance_expiry_time', 'balance_timing_tags', 'balance_weight', 'balance_blocker','balance_disabled', 'actions_tag', 'weight')
    fields = ('tag', 'unique_id', 'threshold_type', 'threshold_value', 'recurrent', 'min_sleep', 'expiry_time', 'activation_time', 'balance_tag', 'balance_type', 'balance_categories', 'balance_destination_tags', 'balance_rating_subject', 'balance_shared_groups', 'balance_expiry_time', 'balance_timing_tags', 'balance_weight', 'balance_blocker','balance_disabled', 'actions_tag', 'weight')
    search_fields = ('tag', 'unique_id', 'threshold_type', 'threshold_value', 'recurrent', 'min_sleep', 'expiry_time', 'activation_time', 'balance_tag', 'balance_type', 'balance_categories', 'balance_destination_tags', 'balance_rating_subject', 'balance_shared_groups', 'balance_expiry_time', 'balance_timing_tags', 'balance_weight', 'balance_blocker','balance_disabled', 'actions_tag', 'weight')
    form =  CreateTpActionTriggers

class Timings(admin.ModelAdmin):
    list_display = ('tag','years','months','month_days','week_days','time')
    fields = ('tag','years','months','month_days','week_days','time')
    search_fields = ('tag','years','months','month_days','week_days','time')
    form = CreateTpTimings

class ActionPlans(admin.ModelAdmin):
    list_display = ('tag','actions_tag','timing_tag','weight')
    fields = ('tag','actions_tag','timing_tag','weight')
    search_fields = ('tag','actions_tag','timing_tag','weight')
    form = CreateTpActionPlans

class Actions(admin.ModelAdmin):
    list_display = ('tag','action','balance_tag','balance_type','units','expiry_time','timing_tags','destination_tags','rating_subject','categories','shared_groups','balance_weight','balance_blocker','balance_disabled','extra_parameters','filter','weight')
    fields = ('tag','action','balance_tag','balance_type','units','expiry_time','timing_tags','destination_tags','rating_subject','categories','shared_groups','balance_weight','balance_blocker','balance_disabled','extra_parameters','filter','weight')
    search_fields = ('tag','action','balance_tag','balance_type','units','expiry_time','timing_tags','destination_tags','rating_subject','categories','shared_groups','balance_weight','balance_blocker','balance_disabled','extra_parameters','filter','weight')

class Chargers(admin.ModelAdmin):
    list_display =  ('tenant','id','filter_ids','activation_interval','run_id','attribute_ids','weight')
    fields = ('tenant','id','filter_ids','activation_interval','run_id','attribute_ids','weight')
    search_fields = ('tenant','id','filter_ids','activation_interval','run_id','attribute_ids','weight')
    form = CreateChargers

class SharedGroups(admin.ModelAdmin):
    list_display = ('tag','account','strategy','rating_subject')
    fields = ('tag','account','strategy','rating_subject')
    search_fields = ('tag','account','strategy','rating_subject')
    form = CreateTpSharedGroups


class Resources(admin.ModelAdmin):
    list_display = ('tenant','id','filter_ids','activation_interval','usage_ttl','limit','allocation_message','blocker','stored','weight','threshold_ids')
    fields = ('tenant','id','filter_ids','activation_interval','usage_ttl','limit','allocation_message','blocker','stored','weight','threshold_ids')
    search_fields = ('tenant','id','filter_ids','activation_interval','usage_ttl','limit','allocation_message','blocker','stored','weight','threshold_ids')
    form = CreateResource

class FilterAdmin(admin.ModelAdmin):
    list_display = ('tenant','id','filter_type','filter_field_name','filter_field_values','activation_interval')
    fields =  ('tenant','id','filter_type','filter_field_name','filter_field_values','activation_interval')
    search_fields =  ('tenant','id','filter_type','filter_field_name','filter_field_values','activation_interval')
    form = CreateTpFilter

class SuppliersAdmin(admin.ModelAdmin):
    list_display = ('tenant','id','filter_ids','activation_interval','sorting','sorting_parameters','supplier_id','supplier_filter_ids','supplier_account_ids','supplier_ratingplan_ids','supplier_resource_ids','supplier_stat_ids','supplier_weight','supplier_blocker','supplier_parameters','weight')
    fields = ('tenant','id','filter_ids','activation_interval','sorting','sorting_parameters','supplier_id','supplier_filter_ids','supplier_account_ids','supplier_ratingplan_ids','supplier_resource_ids','supplier_stat_ids','supplier_weight','supplier_blocker','supplier_parameters','weight')
    search_fields = ('tenant','id','filter_ids','activation_interval','sorting','sorting_parameters','supplier_id','supplier_filter_ids','supplier_account_ids','supplier_ratingplan_ids','supplier_resource_ids','supplier_stat_ids','supplier_weight','supplier_blocker','supplier_parameters','weight')
    form = CreateTpSupplier

class AttributesAdmin(admin.ModelAdmin):
    list_display = ('tenant','id','contexts','filter_ids','activation_interval','attribute_filter_ids','field_name','type','value','blocker','weight')
    fields = ('tenant','id','contexts','filter_ids','activation_interval','attribute_filter_ids','field_name','type','value','blocker','weight')
    search_fields = ('tenant','id','contexts','filter_ids','activation_interval','attribute_filter_ids','field_name','type','value','blocker','weight')
    form = CreateTpAttributes

class ThresholdsAdmin(admin.ModelAdmin):
    list_display = ('id','tenant','filter_ids','activation_interval','min_hits','min_sleep','blocker','weight','action_ids','async','created_at')
    fields = ('id','tenant','filter_ids','activation_interval','min_hits','min_sleep','blocker','weight','action_ids','async')
    search_fields = ('id','tenant','filter_ids','activation_interval','min_hits','min_sleep','blocker','weight','action_ids','async')
    form = CreateThreshold

class TpStatsAdmin(admin.ModelAdmin):
    list_display = ('tenant','id','filter_ids','activation_interval','queue_length','ttl','min_items','metric_ids','metric_filter_ids','stored','blocker','weight','threshold_ids')
    fields = ('tenant','id','filter_ids','activation_interval','queue_length','ttl','min_items','metric_ids','metric_filter_ids','stored','blocker','weight','threshold_ids')
    search_fields = ('tenant','id','filter_ids','activation_interval','queue_length','ttl','min_items','metric_ids','metric_filter_ids','stored','blocker','weight','threshold_ids')
    form = CreateStats


class CdrsAdmin(admin.ModelAdmin):
    list_display = ('cgrid','run_id','origin_host','source','origin_id','tor','request_type','tenant','category','account','subject','destination','setup_time','answer_time','usage','cost_source','cost','created_at','updated_at')
    search_fields = ('cgrid','run_id','origin_host','source','origin_id','tor','request_type','tenant','category','account','subject','destination','setup_time','answer_time','usage','cost_source','cost','created_at','updated_at')


class UserAdmin(admin.ModelAdmin):
    list_display = ('username','tenant','first_name','last_name')

admin.site.register(User,UserAdmin)
admin.site.register(TpDestinations,DestinationsAdmin)
admin.site.register(TpRates,RatesAdmin)
admin.site.register(Carrier,CarrierAdmin)
admin.site.register(RateDeck,RateDeckAdmin)
admin.site.register(TpDestinationRates,DestinationRatesAdmin)
admin.site.register(TpRatingPlans,RatingPlansAdmin)
admin.site.register(TpRatingProfiles,RatingProfile)
admin.site.register(TpAccountActions,AccountActions)
admin.site.register(TpActionTriggers,ActionTriggers)
admin.site.register(TpTimings,Timings)
admin.site.register(TpActionPlans,ActionPlans)
admin.site.register(TpActions,Actions)
admin.site.register(TpChargers,Chargers)
admin.site.register(TpSharedGroups,SharedGroups)
admin.site.register(TpResources,Resources)
admin.site.register(Filters,FilterAdmin)
admin.site.register(TpSuppliers,SuppliersAdmin)
admin.site.register(TpAttributes,AttributesAdmin)
admin.site.register(TpThresholds,ThresholdsAdmin)
admin.site.register(TpStats,TpStatsAdmin)
admin.site.register(Cdrs,CdrsAdmin)
