from itertools import accumulate
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from pay.models import RateDeck, TpDestinations, TpRatingProfiles, TpAccountActions, TpActionTriggers, \
    TpActions, TpActionPlans, TpSharedGroups, Filters, TpResources, TpThresholds, \
    TpSuppliers, TpAttributes, Balance, TpChargers, TpStats
from pay.tasks import uploadrate, delete_rating_plan
from django.db import transaction
from requests.exceptions import ConnectionError
import requests
import json

SERVER = 'http://192.168.100.142:2080/jsonrpc'
HEAD = {'content-type':'application/json'}

@receiver(post_save, sender=RateDeck)
def post_save_RateDeck(sender, instance, **kwargs):
    idpk = instance.pk
    transaction.on_commit(lambda :uploadrate.apply_async(args=[idpk]))

@receiver(pre_delete, sender=RateDeck)
def pre_delete_RateDeck(sender, instance, **kwargs):
    ob = RateDeck.objects.get(pk=instance.pk)
    name = ob.carrier.nameid
    delete_rating_plan.apply_async(args=[name])

@receiver(post_save, sender=TpDestinations)
def post_save_Destinations(sender, instance, **kwargs):
    prefix = TpDestinations.objects.get(pk=instance.pk)
    ID = prefix.tag
    TPid = prefix.tpid
    transaction.on_commit(lambda :LoadDestination(ID,TPid))

@receiver(pre_delete, sender=TpDestinations)
def pre_delete_Destinations(sender, instance, **kwargs):
    prefix = TpDestinations.objects.get(pk=instance.pk)
    ID = prefix.tag
    RemoveDestination(ID)

@receiver(pre_delete, sender=TpRatingProfiles)
def pre_delete_RatingProfiles(sender, instance, **kwargs):
    profile = TpRatingProfiles.objects.get(pk=instance.pk)
    Tenant = profile.tenant
    Category = profile.category
    Subject = profile.subject
    RemoveRatingProfile(Tenant,Category,Subject)

@receiver(post_save, sender=TpRatingProfiles)
def post_save_RatingProfiles(sender, instance, **kwargs):
    profile = TpRatingProfiles.objects.get(pk=instance.pk)
    Tenant = profile.tenant
    Category = profile.category
    Subject = profile.subject
    RatingPlanId = profile.rating_plan_tag
    transaction.on_commit(lambda :LoadRatingProfile(Tenant,Category,Subject,RatingPlanId))

@receiver(pre_delete, sender=TpAccountActions)
def pre_delete_AccountActions(sender, instance, **kwargs):
    account = TpAccountActions.objects.get(pk=instance.pk)
    Tenant = account.tenant
    Account = account.account
    RemoveAccount(Tenant,Account)

@receiver(post_save, sender=TpAccountActions)
def post_save_AccountActions(sender, instance, **kwargs):
    account = TpAccountActions.objects.get(pk=instance.pk)
    Tenant=account.tenant
    Account=account.account
    ActionPlanId=account.action_plan_tag
    ActionTriggersId=account.action_triggers_tag
    AllowNegative= account.allow_negative
    Disabled =account.disabled
    transaction.on_commit(lambda :SetAccount(Tenant,Account,ActionPlanId,ActionTriggersId,AllowNegative,Disabled))

@receiver(pre_delete, sender=TpActionTriggers)
def pre_delete_ActionTriggers(sender, instance, **kwargs):
    trigger = TpActionTriggers.objects.get(pk=instance.pk)
    GroupID = trigger.tag
    UniqueID = trigger.unique_id
    RemoveActionTrigger(GroupID,UniqueID)


@receiver(pre_delete, sender=TpStats)
def pre_delete_RemoveStatQueueProfile(sender, instance, **kwargs):
    stats =  TpStats.objects.get(p_k=instance.pk)
    tenant = stats.tenant
    id = stats.id
    RemoveStatQueueProfile(tenant,id)

@receiver(post_save, sender=TpActionTriggers)
def post_save_ActionTriggers(sender, instance, **kwargs):
    trigger = TpActionTriggers.objects.get(pk=instance.pk)
    print(instance.pk)
    GroupID = trigger.tag
    UniqueID = trigger.unique_id
    ThresholdType = trigger.threshold_type
    ThresholdValue = float(trigger.threshold_value)
    Recurrent = trigger.recurrent
    MinSleep = trigger.min_sleep
    ExpirationDate = trigger.expiry_time
    ActivationDate = trigger.activation_time
    BalanceID = trigger.balance_tag
    BalanceType = trigger.balance_type
    BalanceDestinationIds = trigger.balance_categories
    BalanceWeight = trigger.balance_weight
    BalanceExpirationDate = trigger.balance_expiry_time
    BalanceTimingTags = trigger.balance_timing_tags
    BalanceRatingSubject = trigger.balance_rating_subject
    BalanceCategories = trigger.balance_categories
    BalanceSharedGroups = trigger.balance_shared_groups
    BalanceBlocker = trigger.balance_blocker
    BalanceDisabled = trigger.balance_disabled
    ActionsID = trigger.actions_tag
    SetActionTrigger(GroupID,UniqueID,ThresholdType,ThresholdValue,Recurrent,MinSleep,ExpirationDate,
                     ActivationDate,BalanceID,BalanceType,BalanceDestinationIds,
                     BalanceWeight,BalanceExpirationDate,BalanceTimingTags,BalanceRatingSubject,BalanceCategories,
                     BalanceSharedGroups,BalanceBlocker,BalanceDisabled,ActionsID)

@receiver(post_save, sender=TpActions)
def post_save_Actions(sender, instance, **kwargs):
    action = TpActions.objects.get(pk=instance.pk)
    ActionsId = action.tag
    Overwrite = True
    Identifier = action.action
    BalanceId = action.balance_tag
    BalanceUuid = ""
    BalanceType = action.balance_type
    Units = action.units
    ExpiryTime = action.expiry_time
    Filter = action.filter
    TimingTags = action.timing_tags
    DestinationIds = action.destination_tags
    RatingSubject = action.rating_subject
    Categories = action.categories
    SharedGroups = action.shared_groups
    BalanceWeight = action.balance_weight
    ExtraParameters = action.extra_parameters
    BalanceBlocker = action.balance_blocker
    BalanceDisabled = action.balance_disabled
    Weight = action.weight
    SetActions(ActionsId, Overwrite, Identifier, BalanceId, BalanceUuid, BalanceType, Units, ExpiryTime,
               Filter, TimingTags, DestinationIds, RatingSubject, Categories, SharedGroups, BalanceWeight,
               ExtraParameters, BalanceBlocker, BalanceDisabled, Weight)

@receiver(pre_delete, sender=TpActions)
def pre_delete_Actions(sender, instance, **kwargs):
    action = TpActions.objects.get(pk=instance.pk)
    ActionIDs = action.tag
    RemoveActions(ActionIDs)

@receiver(post_save, sender=TpActionPlans)
def post_save_ActionPlans(sender, instance, **kwargs):
    action = TpActionPlans.objects.get(pk=instance.pk)
    Id = action.tag
    ActionsId = action.actions_tag
    Years = "*any"
    Months = "*any"
    MonthDays = "*any"
    WeekDays = "*any"
    Time = action.timing_tag
    Weight =  float(action.weight)
    transaction.on_commit(lambda :SetActionPlan(Id, ActionsId, Years, Months, MonthDays, WeekDays, Time, Weight))

@receiver(pre_delete, sender=TpActionPlans)
def pre_delete_ActionPlans(sender, instance, **kwargs):
    action = TpActionPlans.objects.get(pk=instance.pk)
    ActionPlanId = action.tag
    RemActionPlan(ActionPlanId)

'''
Signaling for save a Shared Group into cgrates
collect the variables for Shared Group pass to function to handle the api to cgrates
just Load before save in db
'''
@receiver(post_save, sender = TpSharedGroups)
def post_save_SharedGroups(sender, instance, **kwargs):
    sharedGroup = TpSharedGroups.objects.get(pk=instance.pk)
    TPid = sharedGroup.tpid
    SharedGroupId = sharedGroup.tag

    Account = sharedGroup.account #Temporary variable for SetTPSharedGroups
    Strategy = sharedGroup.strategy #Temporary variable for SetTPSharedGroups
    RatingSubject = sharedGroup.rating_subject #Temporary variable for SetTPSharedGroups

    transaction.on_commit(lambda :LoadSharedGroup(TPid,SharedGroupId))

@receiver(pre_delete, sender = TpSharedGroups)
def pre_delete_SharedGroups(sender, instance, **kwargs):
    sharedGroup = TpSharedGroups.objects.get(pk=instance.pk)
    TPid = sharedGroup.tpid
    SharedGroupId = sharedGroup.tag
    RemTPSharedGroups(TPid,SharedGroupId)
    LoadSharedGroup(TPid,SharedGroupId)

@receiver(post_save, sender = Filters)
def post_save_Filter(sender, instance, **kwargs):
    filters = Filters.objects.get(pk=instance.pk)
    FiltersArray = Filters.objects.filter(tenant=filters.tenant, id=filters.id)
    FilterJson = Filter_Parse(FiltersArray)

    filter = Filters.objects.get(pk=instance.pk)
    Tenant = filter.tenant
    ID = filter.id
    Type = filter.filter_type
    FieldName = filter.filter_field_name
    Values = filter.filter_field_values
    ActivationInterval = filter.activation_interval
    transaction.on_commit(lambda :SetFilter(Tenant,ID,Type,FieldName,Values,ActivationInterval, FilterJson))

@receiver(pre_delete, sender = Filters)
def pre_delete_Filter(sender, instance, **kwargs):
    filter = Filters.objects.get(pk=instance.pk)
    Tenant = filter.tenant
    ID = filter.id
    RemoveFilter(Tenant,ID)

@receiver(post_save, sender = TpResources)
def post_save_Resources(sender, instance, **kwargs):
    Resource = TpResources.objects.get(pk=instance.pk)
    Tenant = Resource.tenant
    ID = Resource.id
    FilterIDs = Resource.filter_ids
    ActivationInterval = Resource.activation_interval
    UsageTTL = Resource.usage_ttl
    Limit  = Resource.limit
    AllocationMessage = Resource.allocation_message
    Blocker = Resource.blocker
    Stored = Resource.stored
    Weight = Resource.weight
    ThresholdIDs = Resource.threshold_ids
    transaction.on_commit(lambda :SetResourceProfile(Tenant,ID,FilterIDs,ActivationInterval,UsageTTL,Limit,AllocationMessage,Blocker,Stored,Weight,ThresholdIDs))

@receiver(pre_delete, sender = TpResources)
def pre_delete_Resources(sender, instance, **kwargs):
    Resource = TpResources.objects.get(pk=instance.pk)
    Tenant = Resource.tenant
    ID = Resource.id
    RemoveResourceProfile(Tenant,ID)

@receiver(post_save, sender = TpThresholds)
def post_save_Thresholds(sender, instance, **kwargs):
    Thresholds = TpThresholds.objects.get(pk=instance.pk)
    Tenant = Thresholds.tenant
    ID  = Thresholds.id
    FilterIDs = Thresholds.filter_ids
    ActivationInterval = Thresholds.activation_interval
    Recurrent = Thresholds.recurrent
    MinHits = Thresholds.min_hits
    MinSleep = Thresholds.min_sleep
    Blocker = Thresholds.blocker
    Weight = Thresholds.weight
    ActionIDs = Thresholds.action_ids
    Async = Thresholds.async
    transaction.on_commit(lambda :SetThresholdProfile(Tenant,ID,FilterIDs,ActivationInterval,Recurrent,MinHits,MinSleep,Blocker,Weight,ActionIDs,Async))

@receiver(pre_delete, sender = TpThresholds)
def pre_delete_Thresholds(sender, instance, **kwargs):
    Thresholds = TpThresholds.objects.get(pk=instance.pk)
    Tenant = Thresholds.tenant
    ID  = Thresholds.id
    RemoveThresholdProfile(Tenant, ID)

'''
Supplier parte take a list of query by tenant and id
'''

def Supplier_Parse(supplier):
    sup_array =[]
    for sup in supplier:
        Supplier_Json = {
            "ID": sup.supplier_id if sup.supplier_id is not "" else "",                                             # SupplierID
            "FilterIDs": [sup.supplier_filter_ids] if sup.supplier_filter_ids is not "" else None,
            "AccountIDs": [sup.supplier_account_ids] if sup.supplier_account_ids is not "" else None,               # []string
            "RatingPlanIDs":[sup.supplier_ratingplan_ids] if sup.supplier_ratingplan_ids is not "" else None,       # []string // used when computing price
            "ResourceIDs": [sup.supplier_resource_ids] if sup.supplier_resource_ids is not "" else None,            # []string // queried in some strategies
            "StatIDs": [sup.supplier_stat_ids] if sup.supplier_stat_ids is not "" else None,                        # []string // queried in some strategies
            "Weight": float(sup.supplier_weight) if sup.supplier_weight is not "" else float(0.0),                  # float64
            "Blocker": False if sup.supplier_blocker == 1 else True,                                                # bool // do not process further supplier after this one
            "SupplierParameters": sup.supplier_parameters if sup.supplier_parameters is not "" else ""              # string
        }
        sup_array.append(Supplier_Json)
    return sup_array

''' Filter parte take a list of query by Tnenat and id'''

def Filter_Parse(filter):
    filter_array = []
    for fltr in filter:
        Filters_Json = {
            "Type": fltr.filter_type if fltr.filter_type is not "" else "",
            "FieldName": fltr.filter_field_name if fltr.filter_field_name is not "" else "",
            "Values": fltr.filter_field_values.split(';') if fltr.filter_field_values.split(';') is not "" else ""
        }
        filter_array.append(Filters_Json)
    return filter_array

'''Stats parse take a list of query by Tenant and Id'''

def Stats_Parse(stats):
    stats_array = []
    for st in stats:
        Stats_Json = {
            "FilterIDs":None if st.metric_filter_ids is "" else st.metric_filter_ids.split(";"),
            "MetricID": st.metric_ids
        }
        stats_array.append(Stats_Json)
    return stats_array

@receiver(post_save, sender = TpSuppliers)
def post_save_Suppliers(sender, instance, **kwargs):
    Suppliers = TpSuppliers.objects.get(pk=instance.pk)
    SuppliersArray =  TpSuppliers.objects.filter(tenant=Suppliers.tenant,id=Suppliers.id)
    SupplierJson = Supplier_Parse(SuppliersArray)

    Tenant = Suppliers.tenant
    ID = Suppliers.id
    FilterIDs = Suppliers.filter_ids
    ActivationInterval = Suppliers.activation_interval
    Sorting = Suppliers.sorting
    SortingParameters = [Suppliers.sorting_parameters] if Suppliers.supplier_parameters is not "" else None
    IDd = Suppliers.supplier_id
    FilterIDsd = Suppliers.supplier_filter_ids
    AccountIDs = Suppliers.supplier_account_ids
    RatingPlanIDs = Suppliers.supplier_ratingplan_ids
    ResourceIDs = Suppliers.supplier_resource_ids
    StatIDs = Suppliers.supplier_stat_ids
    Weightd = Suppliers.supplier_weight
    Blocker = Suppliers.supplier_blocker
    SupplierParameters = Suppliers.sorting_parameters
    Weight = Suppliers.supplier_weight
    transaction.on_commit(lambda :SetSupplierProfile(Tenant,ID,FilterIDs,ActivationInterval,Sorting,SortingParameters,IDd,FilterIDsd,AccountIDs,RatingPlanIDs,ResourceIDs,StatIDs,Weightd,Blocker,SupplierParameters,Weight,SupplierJson))

@receiver(pre_delete, sender= TpSuppliers)
def pre_delete_Suppliers(sender, instance, **kwargs):
    Suppliers = TpSuppliers.objects.get(pk=instance.pk)
    Tenant = Suppliers.tenant
    ID = Suppliers.id
    RemoveSupplierProfile(Tenant,ID)

@receiver(post_save, sender = TpAttributes)
def post_save_Attributes(sender, instance, **kwargs):
    attributes = TpAttributes.objects.get(pk=instance.pk)
    Tenant = attributes.tenant
    ID = attributes.id
    Contexts = attributes.contexts
    FilterIDs = attributes.filter_ids
    ActivationInterval = attributes.activation_interval
    FieldName = attributes.field_name
    Initial = attributes.initial
    Substitute = attributes.substitute
    Append = attributes.append
    Weight = attributes.weight
    transaction.on_commit(lambda :SetAttributeProfile(Tenant, ID, Contexts, FilterIDs, ActivationInterval, FieldName, Initial, Substitute, Append, Weight))

@receiver(pre_delete, sender = TpAttributes)
def pre_delete_Attributes(sender, instance, **kwargs):
    attributes = TpAttributes.objects.get(pk=instance.pk)
    Tenant = attributes.tenant
    ID = attributes.id
    Contexts = attributes.contexts
    RemoveAttributeProfile(Tenant, ID, Contexts)

@receiver(post_save,sender = TpChargers)
def post_save_Chargers(sender, instance, **kwargs):
    chargers = TpChargers.objects.get(pk=instance.pk)
    Tenant = chargers.tenant
    ID = chargers.id
    FilterIDs = chargers.filter_ids
    ActivationInterval = chargers.activation_interval
    RunID = chargers.run_id
    AttributeIDs = chargers.attribute_ids
    Weight = chargers.weight
    AddChargerProfile(Tenant,ID,FilterIDs,ActivationInterval,RunID,AttributeIDs,Weight)

@receiver(post_save, sender = TpStats)
def post_save_Stats(sender, instance, **kwargs):
    stats = TpStats.objects.get(p_k=instance.pk)
    stats_array = TpStats.objects.filter(tenant=stats.tenant,id=stats.id)
    stats_json = Stats_Parse(stats_array)

    tenant =  stats.tenant
    id = stats.id
    filter_ids = stats.filter_ids
    activation_interval = stats.activation_interval
    queue_length = stats.queue_length
    ttl = stats.ttl
    min_items = stats.min_items
    metric_ids = stats.metric_ids
    metric_filter_ids = stats.metric_filter_ids
    stored = stats.stored
    blocker = stats.blocker
    weight = stats.weight
    threshold_ids = stats.threshold_ids
    transaction.on_commit(lambda :SetStatQueueProfile(tenant,id,filter_ids,activation_interval,queue_length,ttl,min_items,metric_ids,metric_filter_ids,stored,blocker,weight,threshold_ids, stats_json))

def LoadDestination(ID, TPid):
    payload = {"id": 1,"method":"ApierV1.LoadDestination","params":[{"TPid":TPid,"ID": ID}]}
    r = requests.post(SERVER,headers=HEAD,data=json.dumps(payload))

def RemoveDestination(ID):
    payload = {"id": 1,"method":"ApierV1.RemoveDestination","params":[{"DestinationIDs":[ID]}]}
    r = requests.post(SERVER,headers=HEAD,data=json.dumps(payload))

def RemoveRatingProfile(Tenant,Category,Subject):
    payload = {
        "id":1,
        "method":"ApierV1.RemoveRatingProfile",
        "params":[{
            "Tenant":Tenant,
            "Category":Category,
            "Subject":Subject
        }]
    }
    r= requests.post(SERVER,headers = HEAD,data=json.dumps(payload))
    print(r)
    print(r.content)

def LoadRatingProfile(Tenant,Category,Subject,RatingPlanId):
    payload = {"id":1,
               "method":"ApierV1.LoadRatingProfile",
               "params":[{
                          "TPid":"CgratesPay",
                          "LoadId":"CSVLOAD",
                          "Tenant":Tenant,
                          "Category":Category,
                          "Subject":Subject,
                          "RatingPlanActivations":[{"ActivationTime":"2018-01-01T00:00:00Z",
                                                    "RatingPlanId":RatingPlanId,
                                                    "FallbackSubjects":"",
                                                    "CdrStatQueueIds":""}]}]}
    r= requests.post(SERVER,headers = HEAD,data=json.dumps(payload))
    print(r.content)

def SetRatingProfile(Tenant,Category,Subject,Overwrite,ActivationTime,RatingPlanId,FallbackSubjects,CdrStatQueueIds):
    payload = {
        "id":1,
        "method":"ApierV1.SetRatingProfile",
        "params":[{
            "Tenant":Tenant,
            "Category":Category,
            "Subject":Subject,
            "Overwrite":Overwrite,
            "RatingPlanActivations":[{
                "ActivationTime":ActivationTime,
                "RatingPlanId":RatingPlanId,
                "FallbackSubjects":FallbackSubjects,
                "CdrStatQueueIds":CdrStatQueueIds
            }]
        }]
    }

    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)



def RemoveAccount(Tenant,Account):
    payload = {"id": 1,
               "method": "ApierV1.RemoveAccount",
               "params": [{
                   "Tenant":Tenant,
                   "Account": Account
               }]}
    r = requests.post(SERVER, headers= HEAD, data=json.dumps(payload))
    print(r.content)

def SetAccount(Tenant,Account,ActionPlanId,ActionTriggersId,AllowNegative,Disabled):
    balance = Balance(Tenant,Account)
    if AllowNegative == 0:
        AllowNegative = False
    else:
        AllowNegative = True

    if Disabled == 0:
        Disabled = False
    else:
        Disabled = True

    payload = {"id":1,
              "method": "ApierV1.SetAccount",
              "params":[{
                  "Tenant": Tenant,
                  "Account": Account,
                  "ActionPlanId": ActionPlanId,
                  "ActionTriggersId": ActionTriggersId,
                  "AllowNegative":AllowNegative,
                  "Disabled":Disabled
              }]
    }

    r = requests.post(SERVER,headers=HEAD,data=json.dumps(payload))
    print(r.content)
    print(balance.AddBalance(Tenant,Account,BalanceId="MONETARY",BalanceType="*monetary", Value=0))


def RemoveActionTrigger(GroupID,UniqueID):
    payload = {"id":1,
               "method":"ApierV1.RemoveActionTrigger",
               "params":[{
                   "GroupID": GroupID,
                   "UniqueID": UniqueID
               }]
    }
    r= requests.post(SERVER,headers=HEAD,data=json.dumps(payload))

def SetActionTrigger(GroupID,UniqueID,ThresholdType,ThresholdValue,Recurrent,MinSleep,ExpirationDate,ActivationDate,BalanceID,
                     BalanceType,BalanceDestinationIds,BalanceWeight,BalanceExpirationDate,BalanceTimingTags,
                     BalanceRatingSubject,BalanceCategories,BalanceSharedGroups,BalanceBlocker,BalanceDisabled,
                     ActionsID):
    if Recurrent == 0:
        Recurrent = False
    else:
        Recurrent = True

    if BalanceBlocker == 0:
        BalanceBlocker = False
    else:
        BalanceBlocker = True

    if BalanceDisabled == 0:
        BalanceDisabled = False
    else:
        BalanceDisabled = True

    payload = {"id":1,
               "method":"ApierV1.SetActionTrigger",
               "params":[{
                   "GroupID":GroupID,
                   "UniqueID":UniqueID,
                   "ThresholdType":ThresholdType,
                   "ThresholdValue":float(ThresholdValue),
                   "Recurrent": Recurrent,
                   "MinSleep":MinSleep,
                   "ExpirationDate":ExpirationDate,
                   "ActivationDate":ActivationDate,
                   "BalanceID": BalanceID,
                   "BalanceType":BalanceType,
                   "BalanceDirections":[],
                   "BalanceDestinationIds":[BalanceDestinationIds],
                   "BalanceWeight": float(BalanceWeight),
                   "BalanceExpirationDate":BalanceExpirationDate,
                   "BalanceTimingTags":[BalanceTimingTags],
                   "BalanceRatingSubject":BalanceRatingSubject,
                   "BalanceCategories":[BalanceCategories],
                   "BalanceSharedGroups":[BalanceSharedGroups],
                   "BalanceBlocker":BalanceBlocker,
                   "BalanceDisabled":BalanceDisabled,
                   "MinQueuedItems": int(),
                   "ActionsID": ActionsID
               }]
    }
    r = requests.post(SERVER,headers=HEAD,data=json.dumps(payload))

def SetActions(ActionsId,Overwrite,Identifier,BalanceId,BalanceUuid,BalanceType,Units,
               ExpiryTime,Filter,TimingTags,DestinationIds,RatingSubject,Categories,SharedGroups,
               BalanceWeight,ExtraParameters,BalanceBlocker,BalanceDisabled,Weight):

    if Units is not None:
        print('fuck te coji')

    payload = {
        "id":1,
        "method":"ApierV1.SetActions",
        "params":[{
            "ActionsId":ActionsId,
            "Overwrite":Overwrite,
            "Actions":[{
                "Identifier":Identifier,
                "BalanceId":BalanceId,
                "BalanceUuid":BalanceUuid,
                "BalanceType":BalanceType,
                "Units":float(Units),
                "ExpiryTime":ExpiryTime,
                "Filter":Filter,
                "TimingTags":TimingTags,
                "DestinationIds":DestinationIds,
                "RatingSubject":RatingSubject,
                "Categories":Categories,
                "SharedGroups":SharedGroups,
                "BalanceWeight":float(BalanceWeight),
                "ExtraParameters":ExtraParameters,
                "BalanceBlocker": BalanceBlocker,
                "BalanceDisabled": BalanceDisabled,
                "Weight":float(Weight)
            }]
        }]
    }
    r = requests.post(SERVER,headers=HEAD,data=json.dumps(payload))
    print(r.content)

def RemoveActions(ActionIDs):
    payload = {
        "id":1,
        "method":"ApierV1.RemoveActions",
        "params":[{
            "ActionIDs":[ActionIDs]
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))

def SetActionPlan(Id,ActionsId,Years,Months,MonthDays,WeekDays,Time,Weight):
    payload = {
        "id":1,
        "method":"ApierV1.SetActionPlan",
        "params":[{
            "Id":Id,
            "ActionPlan":[{
                "ActionsId":ActionsId,
                "Years":Years,
                "Months":Months,
                "MonthDays":MonthDays,
                "WeekDays":WeekDays,
                "Time":Time,
                "Weight":float(Weight)
            }]
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def RemActionPlan(ActionPlanId):
    payload = {
        "id":1,
        "method":"ApierV1.RemActionTiming",
        "params":[{
            "ActionPlanId":ActionPlanId,
            "ActionTimingId":"",
            "Tenant":"",
            "Account":"",
            "ReloadScheduler":True
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def LoadSharedGroup(TPid,SharedGroupId):
    payload = {
        "id":1,
        "method":"ApierV1.LoadSharedGroup",
        "params":[{
            "TPid":TPid,
            "SharedGroupId":SharedGroupId
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def SetTPSharedGroups(TPid,ID,Account,Strategy,RatingSubject):
    payload = {
        "id":1,
        "method":"ApierV1.SetTPSharedGroups",
        "params":[{
            "TPid":TPid,
            "ID":ID,
            "SharedGroups":[{
                "Account":Account,
                "Strategy":Strategy,
                "RatingSubject":RatingSubject
            }]
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def RemTPSharedGroups(TPid,ID):
    payload = {
        "id":1,
        "method":"ApierV1.RemTPSharedGroups",
        "params":[{
            "TPid":TPid,
            "ID":ID
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def SetFilter(Tenant,ID,Type,FieldName,Values,ActivationInterval, FilterJson):
    '''
    :param Tenant:
    :param ID:
    :param Type:
    :param FieldName:
    :param Values: The Value come with a string but we need split that in a array of the string
    the format of the string come with ; example Value="1001;1002"
    :param ActivationInterval:
    :return:
    '''
    payload = {
        "id":1,
        "method":"ApierV1.SetFilter",
        "params":[{
            "Tenant":Tenant,
            "ID":ID,
            "Rules":FilterJson,
            "ActivationInterval":{
                "ActivationInterval":ActivationInterval,
                "ExpiryTime":ActivationInterval
            }
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def RemoveFilter(Tenant,ID):
    payload = {
        "id":1,
        "method":"ApierV1.RemoveFilter",
        "params":[{
            "Tenant":Tenant,
            "ID":ID
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def SetResourceProfile(Tenant,ID,FilterIDs,ActivationInterval,UsageTTL,Limit,AllocationMessage,Blocker,Stored,Weight,ThresholdIDs):
    if Blocker == 1:
        Blocker = True
    else:
        Blocker = False

    if Stored == 1:
        Stored = True
    else:
        Stored = False


    payload = {
        "id":1,
        "method":"ApierV1.SetResourceProfile",
        "params":[{
            "Tenant":Tenant,
            "ID":ID,
            "FilterIDs":[FilterIDs],
            "ActivationInterval":{
                "ActivationTime":ActivationInterval,
                "ExpiryTime":ActivationInterval
            },
            "UsageTTL":int(UsageTTL),
            "Limit":float(Limit),
            "AllocationMessage":AllocationMessage,
            "Blocker":Blocker,
            "Stored":Stored,
            "Weight":float(Weight),
            "ThresholdIDs":[ThresholdIDs]
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def RemoveResourceProfile(Tenant,ID):
    payload = {
        "id":1,
        "method":"ApierV1.RemoveResourceProfile",
        "params":[{
            "Tenant":Tenant,
            "ID":ID
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def SetThresholdProfile(Tenant,ID,FilterIDs,ActivationInterval,Recurrent,MinHits,MinSleep,Blocker,Weight,ActionIDs,Async):
    if Recurrent == 1:
        Recurrent = True
    else:
        Recurrent = False

    if Blocker == 1:
        Blocker = True
    else:
        Blocker = False

    if Async == 1:
        Async = True
    else:
        Async = False

    payload = {
        "id":1,
        "method":"ApierV1.SetThresholdProfile",
        "params":[{
            "Tenant":Tenant,
            "ID":ID,
            "FilterIDs":[FilterIDs],
            "ActivationInterval":{
                "ActivationTime":ActivationInterval,
                "ExpiryTime":ActivationInterval
            },
            "Recurrent":Recurrent,
            "MinHits":int(MinHits),
            "MinSleep":int(MinSleep),
            "Blocker":Blocker,
            "Weight":float(Weight),
            "ActionIDs":[ActionIDs],
            "Async":Async
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def RemoveThresholdProfile(Tenant,ID):
    payload = {
        "id": 1,
        "method": "ApierV1.RemoveThresholdProfile",
        "params": [{
            "Tenant": Tenant,
            "ID": ID
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def SetSupplierProfile(Tenant,ID,FilterIDs,ActivationInterval,Sorting,SortingParameters,IDd,FilterIDsd,AccountIDs,RatingPlanIDs,ResourceIDs,StatIDs,Weightd,Blocker,SupplierParameters,Weight,SupplierJson):
    payload = {
        "id":1,
        "method":"ApierV1.SetSupplierProfile",
        "params":[{
            "Tenant":Tenant,
            "ID":ID,
            "FilterIDs":[FilterIDs],
            "ActivationInterval":{
                "ActivationTime": ActivationInterval,
                "ExpiryTime": '0001-01-01T00:00:00Z'
            },
            "Sorting":Sorting,
            "SortingParameters":SortingParameters,
            "Suppliers":SupplierJson,
            "Weight":float(Weight)
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def RemoveSupplierProfile(Tenant,ID):
    payload = {
        "id": 1,
        "method": "ApierV1.RemoveSupplierProfile",
        "params": [{
            "Tenant": Tenant,
            "ID": ID
        }]
    }
    try:
        r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    except ConnectionError:
        pass
def SetAttributeProfile(Tenant,ID,Contexts,FilterIDs,ActivationInterval,FieldName,Initial,Substitute,Append,Weight):
    '''

    :param Tenant:
    :param ID:
    :param Contexts:
    :param FilterIDs:
    :param ActivationInterval:
    :param FieldName:
    :param Initial:
    :param Substitute:
    :param Append:
    :param Weight:
    :return:
    '''

    if Append == 1:
        Append = True
    else:
        Append = False

    payload= {
        "id":1,
        "method":"ApierV1.SetAttributeProfile",
        "params":[{
            "Tenant":Tenant,
            "ID":ID,
            "Contexts":[Contexts],
            "FilterIDs":[FilterIDs],
            "ActivationInterval":{
                "ActivationTime":ActivationInterval,
                "ExpiryTime":ActivationInterval
            },
            "Attributes":[{
                "FieldName":FieldName,
                "Initial":Initial,
                "Substitute":[
                    {
                        "Rules":Substitute,
                        "AllFiltersMatch":True
                    }
                ],
                "Append":Append
            }],
            "Weight":float(Weight)
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def RemoveAttributeProfile(Tenant,ID,Contexts):
    payload = {
        "id":1,
        "method":"ApierV1.RemoveAttributeProfile",
        "params":[{
            "Tenant":Tenant,
            "ID":ID,
            "Contexts":[Contexts]
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

'''
    Tenant             string
    ID                 string
    FilterIDs          []string
    ActivationInterval *utils.ActivationInterval // Activation interval
    RunID              string
    AttributeIDs       []string // perform data aliasing based on these Attributes
    Weight             float64
'''
def AddChargerProfile(Tenant,ID,FilterIDs,ActivationInterval,RunID,AttributeIDs,Weight):
    payload = {
        "id":1,
        "method":"ApierV1.SetChargerProfile",
        "params":[{
            "Tenant":Tenant,
            "ID":ID,
            "FilterIDs":[],
            "ActivationInterval":None,
            "RunID":RunID,
            "AttributeIDs":[AttributeIDs],
            "Weight":float(Weight)
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)


'''
SetResourceProfile
    Tenant             string
    ID                 string // identifier of this resource
    FilterIDs          []string
    ActivationInterval *utils.ActivationInterval // time when this resource becomes active and expires
    UsageTTL           time.Duration             // auto-expire the usage after this duration
    Limit              float64                   // limit value
    AllocationMessage  string                    // message returned by the winning resource on allocation
    Blocker            bool                      // blocker flag to stop processing on filters matched
    Stored             bool
    Weight             float64  // Weight to sort the resources
    ThresholdIDs       []string // Thresholds to check after changing Limit
'''

def SetStatQueueProfile(Tenant,ID,FilterIDs,ActivationInterval,QueueLength,TTL,MinItems,Metrics,MetricFilterIDs,Stored,Blocker,Weight,ThresholdIDs,StatsJson):

    paylaod = {
        "id": 117,
        "method":"ApierV1.SetStatQueueProfile",
        "params":[{
            "Tenant":Tenant,
            "ID":ID,
            "FilterIDs":[FilterIDs],
            "ActivationInterval":{
                "ActivationTime": ActivationInterval,
                "ExpiryTime": '0001-01-01T00:00:00Z'
            },
            "QueueLength":QueueLength,
            "TTL":int(TTL),
            "MinItems":MinItems,
            "Metrics":StatsJson,
            "Stored":True if Stored == 1 else False,
            "Blocker":True if Blocker == 1 else False,
            "Weight":float(Weight),
            "ThresholdIDs":[ThresholdIDs]
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(paylaod))
    print(r.content)


def RemoveStatQueueProfile(Tenant,ID):
    paylaod = {
        "id":145,
        "method":"ApierV1.RemoveStatQueueProfile",
        "params":[{
            "Tenant":Tenant,
            "ID":ID
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(paylaod))
    print(r.content)
