from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db import connection

# Register your models here.
from pay.models import TpDestinations,TpRates,Carrier,RateDeck,TpDestinationRates,TpRatingPlans,TpRatingProfiles, \
    TpAccountActions, TpActionTriggers, TpTimings, TpActionPlans, TpActions, TpDerivedChargers, TpCdrStats, TpSharedGroups, \
    TpLcrRules, TpUsers, TpAliases, TpResources, Filters, TpSuppliers, TpAttributes, TpThresholds, Cdrs, TpStats, User
from pay.forms import CreateTpRatingProfiles, CreateTpAccountActions, CreateTpTimings, CreateTpActionTriggers,\
    CreateTpActionPlans, CreateTpDerivedChargers, CreateTpCdrStats, CreateTpLcrRules, CreateTpAliases, CreateTpSharedGroups, \
    CreateTpSupplier, CreateTpFilter, CreateTpAttributes, CreateResource, CreateThreshold, CreateUsers

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
    list_display = ('direction','tenant','category','subject','activation_time','rating_plan_tag')
    fields = ('direction','tenant','category','subject','activation_time','rating_plan_tag','fallback_subjects','cdr_stat_queue_ids')
    search_fields = ('direction','tenant','category','subject','activation_time','rating_plan_tag','fallback_subjects','cdr_stat_queue_ids')
    form = CreateTpRatingProfiles

class AccountActions(admin.ModelAdmin):
    list_display = ('tenant','account','action_plan_tag','action_triggers_tag','allow_negative','disabled')
    fields = ('tenant','account','action_plan_tag','action_triggers_tag','allow_negative','disabled')
    search_fields = ('tenant','account','action_plan_tag','action_triggers_tag','allow_negative','disabled')
    form = CreateTpAccountActions

class ActionTriggers(admin.ModelAdmin):
    list_display = ('tag', 'unique_id', 'threshold_type', 'threshold_value', 'recurrent', 'min_sleep', 'expiry_time', 'activation_time', 'balance_tag', 'balance_type', 'balance_directions', 'balance_categories', 'balance_destination_tags', 'balance_rating_subject', 'balance_shared_groups', 'balance_expiry_time', 'balance_timing_tags', 'balance_weight', 'balance_blocker','balance_disabled', 'min_queued_items', 'actions_tag', 'weight')
    fields = ('tag', 'unique_id', 'threshold_type', 'threshold_value', 'recurrent', 'min_sleep', 'expiry_time', 'activation_time', 'balance_tag', 'balance_type', 'balance_directions', 'balance_categories', 'balance_destination_tags', 'balance_rating_subject', 'balance_shared_groups', 'balance_expiry_time', 'balance_timing_tags', 'balance_weight', 'balance_blocker','balance_disabled', 'min_queued_items', 'actions_tag', 'weight')
    search_fields = ('tag', 'unique_id', 'threshold_type', 'threshold_value', 'recurrent', 'min_sleep', 'expiry_time', 'activation_time', 'balance_tag', 'balance_type', 'balance_directions', 'balance_categories', 'balance_destination_tags', 'balance_rating_subject', 'balance_shared_groups', 'balance_expiry_time', 'balance_timing_tags', 'balance_weight', 'balance_blocker','balance_disabled', 'min_queued_items', 'actions_tag', 'weight')
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
    list_display = ('tag','action','balance_tag','balance_type','directions','units','expiry_time','timing_tags','destination_tags','rating_subject','categories','shared_groups','balance_weight','balance_blocker','balance_disabled','extra_parameters','filter','weight')
    fields = ('tag','action','balance_tag','balance_type','directions','units','expiry_time','timing_tags','destination_tags','rating_subject','categories','shared_groups','balance_weight','balance_blocker','balance_disabled','extra_parameters','filter','weight')
    search_fields = ('tag','action','balance_tag','balance_type','directions','units','expiry_time','timing_tags','destination_tags','rating_subject','categories','shared_groups','balance_weight','balance_blocker','balance_disabled','extra_parameters','filter','weight')

class DerivedChargers(admin.ModelAdmin):
    list_display = ('direction','tenant','category','account','subject','destination_ids','runid','run_filters','req_type_field','direction_field','tenant_field','category_field','account_field','subject_field','destination_field','setup_time_field','pdd_field','answer_time_field','usage_field','supplier_field','disconnect_cause_field','rated_field','cost_field')
    fields = ('direction','tenant','category','account','subject','destination_ids','runid','run_filters','req_type_field','direction_field','tenant_field','category_field','account_field','subject_field','destination_field','setup_time_field','pdd_field','answer_time_field','usage_field','supplier_field','disconnect_cause_field','rated_field','cost_field')
    search_fields = ('direction','tenant','category','account','subject','destination_ids','runid','run_filters','req_type_field','direction_field','tenant_field','category_field','account_field','subject_field','destination_field','setup_time_field','pdd_field','answer_time_field','usage_field','supplier_field','disconnect_cause_field','rated_field','cost_field')
    form = CreateTpDerivedChargers

class CdrStats(admin.ModelAdmin):
    list_display = ('tag','queue_length','time_window','save_interval','metrics','setup_interval','tors','cdr_hosts','cdr_sources','req_types','directions','tenants','categories','accounts','subjects','destination_ids','pdd_interval','usage_interval','suppliers','disconnect_causes','mediation_runids','rated_accounts','rated_subjects','cost_interval','action_triggers')
    fields = ('tag','queue_length','time_window','save_interval','metrics','setup_interval','tors','cdr_hosts','cdr_sources','req_types','directions','tenants','categories','accounts','subjects','destination_ids','pdd_interval','usage_interval','suppliers','disconnect_causes','mediation_runids','rated_accounts','rated_subjects','cost_interval','action_triggers')
    search_fields = ('tag','queue_length','time_window','save_interval','metrics','setup_interval','tors','cdr_hosts','cdr_sources','req_types','directions','tenants','categories','accounts','subjects','destination_ids','pdd_interval','usage_interval','suppliers','disconnect_causes','mediation_runids','rated_accounts','rated_subjects','cost_interval','action_triggers')
    form = CreateTpCdrStats

class SharedGroups(admin.ModelAdmin):
    list_display = ('tag','account','strategy','rating_subject')
    fields = ('tag','account','strategy','rating_subject')
    search_fields = ('tag','account','strategy','rating_subject')
    form = CreateTpSharedGroups

class LcrRules(admin.ModelAdmin):
    list_display = ('direction','tenant','category','account','subject','destination_tag','rp_category','strategy','strategy_params','activation_time','weight')
    fields =  ('direction','tenant','category','account','subject','destination_tag','rp_category','strategy','strategy_params','activation_time','weight')
    search_fields = ('direction','tenant','category','account','subject','destination_tag','rp_category','strategy','strategy_params','activation_time','weight')
    form = CreateTpLcrRules

class Aliases(admin.ModelAdmin):
    list_display = ('direction','tenant','category','account','subject','destination_id','context','target','original','alias','weight')
    fields = ('direction','tenant','category','account','subject','destination_id','context','target','original','alias','weight')
    search_fields = ('direction','tenant','category','account','subject','destination_id','context','target','original','alias','weight')
    form = CreateTpAliases


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
    list_display = ('tenant','id','contexts','filter_ids','activation_interval','field_name','initial','substitute','append','blocker','weight')
    fields = ('tenant','id','contexts','filter_ids','activation_interval','field_name','initial','substitute','append','blocker','weight')
    search_fields = ('tenant','id','contexts','filter_ids','activation_interval','field_name','initial','substitute','append','blocker','weight')
    form = CreateTpAttributes

class ThresholdsAdmin(admin.ModelAdmin):
    list_display = ('id','tenant','filter_ids','activation_interval','min_hits','min_sleep','blocker','weight','action_ids','async','created_at')
    fields = ('id','tenant','filter_ids','activation_interval','min_hits','min_sleep','blocker','weight','action_ids','async')
    search_fields = ('id','tenant','filter_ids','activation_interval','min_hits','min_sleep','blocker','weight','action_ids','async')
    form = CreateThreshold

class TpStatsAdmin(admin.ModelAdmin):
    list_display = ('tenant','id','filter_ids','activation_interval','queue_length','ttl','metrics','parameters','blocker','stored','weight','min_items','threshold_ids')
    fields = ('tenant','id','filter_ids','activation_interval','queue_length','ttl','metrics','parameters','blocker','stored','weight','min_items','threshold_ids')
    search_fields = ('tenant','id','filter_ids','activation_interval','queue_length','ttl','metrics','parameters','blocker','stored','weight','min_items','threshold_ids')


class CdrsAdmin(admin.ModelAdmin):
    list_display = ('cgrid','run_id','origin_host','source','origin_id','tor','request_type','tenant','category','account','subject','destination','setup_time','answer_time','usage','cost_source','cost','created_at','updated_at')



class Users(admin.ModelAdmin):
    list_display = ('tenant','user_name','masked','attribute_name','attribute_value','weight')
    fields = ('tenant','user_name','masked','attribute_name','attribute_value','weight')
    search_fields = ('tenant','user_name','masked','attribute_name','attribute_value','weight')
    form = CreateUsers

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
admin.site.register(TpDerivedChargers,DerivedChargers)
admin.site.register(TpCdrStats,CdrStats)
admin.site.register(TpSharedGroups,SharedGroups)
admin.site.register(TpLcrRules,LcrRules)
admin.site.register(TpUsers,Users)
admin.site.register(TpAliases,Aliases)
admin.site.register(TpResources,Resources)
admin.site.register(Filters,FilterAdmin)
admin.site.register(TpSuppliers,SuppliersAdmin)
admin.site.register(TpAttributes,AttributesAdmin)
admin.site.register(TpThresholds,ThresholdsAdmin)
admin.site.register(TpStats,TpStatsAdmin)
admin.site.register(Cdrs,CdrsAdmin)
