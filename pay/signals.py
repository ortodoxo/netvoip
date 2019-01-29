from itertools import accumulate
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from pay.models import RateDeck, TpDestinations, TpRatingProfiles, TpAccountActions, TpActionTriggers, \
    TpActions, TpActionPlans, TpDerivedChargers,TpCdrStats, TpSharedGroups, Filters, TpResources, TpThresholds, \
    TpSuppliers, TpAttributes, Balance
from pay.tasks import uploadrate, delete_rating_plan
from django.db import transaction
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
    Direction = profile.direction
    Tenant = profile.tenant
    Category = profile.category
    Subject = profile.subject
    RemoveRatingProfile(Direction,Tenant,Category,Subject)

@receiver(post_save, sender=TpRatingProfiles)
def post_save_RatingProfiles(sender, instance, **kwargs):
    profile = TpRatingProfiles.objects.get(pk=instance.pk)
    Direction = profile.direction
    Tenant = profile.tenant
    Category = profile.category
    Subject = profile.subject
    RatingPlanId = profile.rating_plan_tag
    transaction.on_commit(lambda :LoadRatingProfile(Direction,Tenant,Category,Subject,RatingPlanId))

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
    BalanceDirections = trigger.balance_directions
    BalanceDestinationIds = trigger.balance_categories
    BalanceWeight = trigger.balance_weight
    BalanceExpirationDate = trigger.balance_expiry_time
    BalanceTimingTags = trigger.balance_timing_tags
    BalanceRatingSubject = trigger.balance_rating_subject
    BalanceCategories = trigger.balance_categories
    BalanceSharedGroups = trigger.balance_shared_groups
    BalanceBlocker = trigger.balance_blocker
    BalanceDisabled = trigger.balance_disabled
    MinQueuedItems = trigger.min_queued_items
    ActionsID = trigger.actions_tag
    SetActionTrigger(GroupID,UniqueID,ThresholdType,ThresholdValue,Recurrent,MinSleep,ExpirationDate,
                     ActivationDate,BalanceID,BalanceType,BalanceDirections,BalanceDestinationIds,
                     BalanceWeight,BalanceExpirationDate,BalanceTimingTags,BalanceRatingSubject,BalanceCategories,
                     BalanceSharedGroups,BalanceBlocker,BalanceDisabled,MinQueuedItems,ActionsID)

@receiver(post_save, sender=TpActions)
def post_save_Actions(sender, instance, **kwargs):
    action = TpActions.objects.get(pk=instance.pk)
    ActionsId = action.tag
    Overwrite = True
    Identifier = action.action
    BalanceId = action.balance_tag
    BalanceUuid = ""
    BalanceType = action.balance_type
    Directions = action.directions
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
    SetActions(ActionsId, Overwrite, Identifier, BalanceId, BalanceUuid, BalanceType, Directions, Units, ExpiryTime,
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

@receiver(post_save, sender=TpDerivedChargers)
def post_save_DerivedChargers(sender, instance, **kwargs):
    derivedcharger = TpDerivedChargers.objects.get(pk=instance.pk)
    Direction = derivedcharger.direction
    Tenant = derivedcharger.tenant
    Category = derivedcharger.category
    Account = derivedcharger.account
    Subject = derivedcharger.subject
    DestinationIds = derivedcharger.destination_ids
    RunID = derivedcharger.runid
    RunFilters = derivedcharger.run_filters
    RequestTypeField = derivedcharger.req_type_field
    DirectionField = derivedcharger.direction_field
    TenantField = derivedcharger.tenant_field
    CategoryField = derivedcharger.category_field
    AccountField =derivedcharger.account_field
    SubjectField = derivedcharger.subject_field
    DestinationField = derivedcharger.destination_field
    SetupTimeField = derivedcharger.setup_time_field
    PDDField = derivedcharger.pdd_field
    AnswerTimeField = derivedcharger.answer_time_field
    UsageField = derivedcharger.usage_field
    SupplierField = derivedcharger.supplier_field
    DisconnectCauseField = derivedcharger.disconnect_cause_field
    CostField = derivedcharger.cost_field
    RatedField = derivedcharger.rated_field
    transaction.on_commit(lambda :SetDerivedChargers(Direction, Tenant, Category, Account, Subject, DestinationIds, RunID,
                       RunFilters, RequestTypeField, DirectionField, TenantField, CategoryField,
                       AccountField, SubjectField, DestinationField, SetupTimeField, PDDField, AnswerTimeField,
                       UsageField, SupplierField, DisconnectCauseField, CostField, RatedField))


@receiver(pre_delete, sender=TpDerivedChargers)
def pre_delete_DerivedChargers(sender, instance, **kwargs):
    derivedcharger = TpDerivedChargers.objects.get(pk=instance.pk)
    Direction = derivedcharger.direction
    Tenant = derivedcharger.tenant
    Category = derivedcharger.category
    Account = derivedcharger.account
    Subject = derivedcharger.subject
    RemDerivedChargers(Direction, Tenant, Category, Account, Subject)

@receiver(post_save, sender=TpCdrStats)
def post_save_CdrStats(sender, instance, **kwargs):
    cdrstats = TpCdrStats.objects.get(pk=instance.pk)
    Id = cdrstats.tag
    QueueLength = cdrstats.queue_length
    TimeWindow = cdrstats.time_window
    SaveInterval = cdrstats.save_interval
    Metrics = cdrstats.metrics
    SetupInterval = cdrstats.setup_interval
    TOR = cdrstats.tors
    CdrHost = cdrstats.cdr_hosts
    CdrSource = cdrstats.cdr_sources
    ReqType = cdrstats.req_types
    Direction = cdrstats.directions
    Tenant = cdrstats.tenants
    Category = cdrstats.categories
    Account = cdrstats.accounts
    Subject = cdrstats.subjects
    DestinationIds = cdrstats.destination_ids
    UsageInterval = cdrstats.usage_interval
    PddInterval = cdrstats.pdd_interval
    Supplier = cdrstats.suppliers
    DisconnectCause = cdrstats.disconnect_causes
    MediationRunIds = cdrstats.mediation_runids
    RatedAccount = cdrstats.rated_accounts
    RatedSubject = cdrstats.rated_subjects
    CostInterval = cdrstats.cost_interval
    ActionTriggers = cdrstats.action_triggers
    transaction.on_commit(lambda :AddQueue(Id, QueueLength, TimeWindow, SaveInterval, Metrics, SetupInterval, TOR, CdrHost, CdrSource, ReqType,
             Direction, Tenant, Category, Account, Subject, DestinationIds, UsageInterval, PddInterval, Supplier,
             DisconnectCause, MediationRunIds, RatedAccount, RatedSubject, CostInterval, ActionTriggers))

@receiver(pre_delete, sender=TpCdrStats)
def pre_delete_CdrStats(sender, instance, **kwargs):
    cdrstats = TpCdrStats.objects.get(pk=instance.pk)
    qID = cdrstats.tag
    RemoveQueue(qID)

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
    filter = Filters.objects.get(pk=instance.pk)
    Tenant = filter.tenant
    ID = filter.id
    Type = filter.filter_type
    FieldName = filter.filter_field_name
    Values = filter.filter_field_values
    ActivationInterval = filter.activation_interval
    transaction.on_commit(lambda :SetFilter(Tenant,ID,Type,FieldName,Values,ActivationInterval))

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

def Supplier_Parse(supplier):
    sup_array =[]

    for sup in supplier:
        print(sup.supplier_id)
        Supplier_Json = {
            "ID": sup.supplier_id if sup.supplier_id is not "" else "",  # SupplierID
            "FilterIDs": [sup.supplier_filter_ids] if sup.supplier_filter_ids is not "" else None,
            "AccountIDs": [sup.supplier_account_ids] if sup.supplier_account_ids is not "" else None,         # []string
            "RatingPlanIDs":[sup.supplier_ratingplan_ids] if sup.supplier_ratingplan_ids is not "" else None,      # []string // used when computing price
            "ResourceIDs": [sup.supplier_resource_ids] if sup.supplier_resource_ids is not "" else None,        # []string // queried in some strategies
            "StatIDs": [sup.supplier_stat_ids] if sup.supplier_stat_ids is not "" else None,            # []string // queried in some strategies
            "Weight": float(sup.supplier_weight) if sup.supplier_weight is not "" else float(0.0),       # float64
            "Blocker": False if sup.supplier_blocker == 1 else True,           # bool // do not process further supplier after this one
            "SupplierParameters": sup.supplier_parameters if sup.supplier_parameters is not "" else ""    # string
        }
        sup_array.append(Supplier_Json)
    print(sup_array)
    return sup_array

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

def LoadDestination(ID, TPid):
    payload = {"id": 1,"method":"ApierV1.LoadDestination","params":[{"TPid":TPid,"ID": ID}]}
    r = requests.post(SERVER,headers=HEAD,data=json.dumps(payload))

def RemoveDestination(ID):
    payload = {"id": 1,"method":"ApierV1.RemoveDestination","params":[{"DestinationIDs":[ID]}]}
    r = requests.post(SERVER,headers=HEAD,data=json.dumps(payload))

def RemoveRatingProfile(Direction,Tenant,Category,Subject):
    payload = {
        "id":1,
        "method":"ApierV1.RemoveRatingProfile",
        "params":[{
            "Direction":Direction,
            "Tenant":Tenant,
            "Category":Category,
            "Subject":Subject
        }]
    }
    r= requests.post(SERVER,headers = HEAD,data=json.dumps(payload))
    print(r)
    print(r.content)

def LoadRatingProfile(Direction,Tenant,Category,Subject,RatingPlanId):
    payload = {"id":1,
               "method":"ApierV1.LoadRatingProfile",
               "params":[{"TPid":"CgratesPay",
                          "LoadId":"CSVLOAD",
                          "Direction":Direction,
                          "Tenant":Tenant,
                          "Category":Category,
                          "Subject":Subject,
                          "RatingPlanActivations":[{"ActivationTime":"2018-01-01T00:00:00Z",
                                                    "RatingPlanId":RatingPlanId,
                                                    "FallbackSubjects":"",
                                                    "CdrStatQueueIds":""}]}]}
    r= requests.post(SERVER,headers = HEAD,data=json.dumps(payload))
    print(r.content)

def SetRatingProfile(Tenant,Category,Direction,Subject,Overwrite,ActivationTime,RatingPlanId,FallbackSubjects,CdrStatQueueIds):
    payload = {
        "id":1,
        "method":"ApierV1.SetRatingProfile",
        "params":[{
            "Tenant":Tenant,
            "Category":Category,
            "Direction":Direction,
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
                     BalanceType,BalanceDirections,BalanceDestinationIds,BalanceWeight,BalanceExpirationDate,BalanceTimingTags,
                     BalanceRatingSubject,BalanceCategories,BalanceSharedGroups,BalanceBlocker,BalanceDisabled,MinQueuedItems,
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
                   "BalanceDirections":[BalanceDirections],
                   "BalanceDestinationIds":[BalanceDestinationIds],
                   "BalanceWeight": float(BalanceWeight),
                   "BalanceExpirationDate":BalanceExpirationDate,
                   "BalanceTimingTags":[BalanceTimingTags],
                   "BalanceRatingSubject":BalanceRatingSubject,
                   "BalanceCategories":[BalanceCategories],
                   "BalanceSharedGroups":[BalanceSharedGroups],
                   "BalanceBlocker":BalanceBlocker,
                   "BalanceDisabled":BalanceDisabled,
                   "MinQueuedItems": int(MinQueuedItems),
                   "ActionsID": ActionsID
               }]
    }
    r = requests.post(SERVER,headers=HEAD,data=json.dumps(payload))

def SetActions(ActionsId,Overwrite,Identifier,BalanceId,BalanceUuid,BalanceType,Directions,Units,
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
                "Directions":Directions,
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

def SetDerivedChargers(Direction, Tenant, Category, Account, Subject, DestinationIds, RunID,
                       RunFilters,RequestTypeField,DirectionField,TenantField,CategoryField,
                       AccountField,SubjectField,DestinationField,SetupTimeField,PDDField,AnswerTimeField,
                       UsageField,SupplierField,DisconnectCauseField,CostField,RatedField):
    payload= {
        "id":1,
        "method":"ApierV1.SetDerivedChargers",
        "params":[{
            "Direction":Direction,
            "Tenant":Tenant,
            "Category":Category,
            "Account":Account,
            "Subject":Subject,
            "DestinationIds":DestinationIds,
            "DerivedChargers":[{
                "RunID":RunID,
                "RunFilters":RunFilters,
                "RequestTypeField":RequestTypeField,
                "DirectionField":DirectionField,
                "TenantField":TenantField,
                "CategoryField":CategoryField,
                "AccountField":AccountField,
                "SubjectField":SubjectField,
                "DestinationField":DestinationField,
                "SetupTimeField":SetupTimeField,
                "PDDField":PDDField,
                "AnswerTimeField":AnswerTimeField,
                "UsageField":UsageField,
                "SupplierField":SupplierField,
                "DisconnectCauseField":DisconnectCauseField,
                "CostField":CostField,
                "RatedField":RatedField
            }]
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

def RemDerivedChargers(Direction, Tenant, Category, Account, Subject):
    payload = {
        "id":1,
        "method":"ApierV1.RemDerivedChargers",
        "params":[{
            "Direction":Direction,
            "Tenant":Tenant,
            "Category":Category,
            "Account":Account,
            "Subject":Subject
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)


def AddQueue(Id,QueueLength,TimeWindow,SaveInterval,Metrics,SetupInterval,TOR,CdrHost,CdrSource,ReqType,
             Direction,Tenant,Category,Account,Subject,DestinationIds,UsageInterval,PddInterval,Supplier,
             DisconnectCause,MediationRunIds,RatedAccount,RatedSubject,CostInterval,ActionTriggers):
    payload = {
        "id":1,
        "method":"CDRStatsV1.AddQueue",
        "params":[{
            "Id":Id,
            "QueueLength":int(QueueLength),
            "TimeWindow":int(TimeWindow),
            "SaveInterval":int(SaveInterval),
            "Metrics":[Metrics],
            "SetupInterval":[SetupInterval],
            "TOR":[TOR],
            "CdrHost":[CdrHost],
            "CdrSource":[CdrSource],
            "ReqType":[ReqType],
            "Direction":[Direction],
            "Tenant":[Tenant],
            "Category":[Category],
            "Account":[Account],
            "Subject":[Subject],
            "DestinationIds":[DestinationIds],
            "UsageInterval":[UsageInterval],
            "PddInterval":[PddInterval],
            "Supplier":[Supplier],
            "DisconnectCause":[DisconnectCause],
            "MediationRunIds":[MediationRunIds],
            "RatedAccount":[RatedAccount],
            "RatedSubject":[RatedSubject],
            "CostInterval":[float(CostInterval)],
            "Triggers":[{
                "ID":ActionTriggers
            }]
        }]
    }
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)


def RemoveQueue(qID):
    payload = {
        "id":1,
        "method":"CDRStatsV1.RemoveQueue",
        "params":[qID]
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

def SetFilter(Tenant,ID,Type,FieldName,Values,ActivationInterval):
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
    Values = Values.split(';')
    payload = {
        "id":1,
        "method":"ApierV1.SetFilter",
        "params":[{
            "Tenant":Tenant,
            "ID":ID,
            "Rules":[{
                "Type":Type,
                "FieldName":FieldName,
                "Values":Values
            }],
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
            "ActivationInterval":None,
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
    r = requests.post(SERVER, headers=HEAD, data=json.dumps(payload))
    print(r.content)

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