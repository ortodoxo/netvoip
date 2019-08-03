from django import forms
from django.forms import ModelForm, Select, TimeInput
from pay.models import TpRatingProfiles, TpAccountActions, TpTimings, TpActionTriggers, TpActionPlans, \
    TpChargers, TpSharedGroups, TpSuppliers, TpAttributes, Filters, TpResources, TpThresholds, TpStats
from pay.validators import activation_time_validate, destinations_validate, usage_validate
from django.db import connection


def upload_attribute_id():
    cursor = connection.cursor()
    cursor.execute("SELECT id,id FROM tp_attributes")
    row = (('*none','*none'),)
    row += cursor.fetchall()
    return row

def upload_rating_plan():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT tag, tag FROM tp_rating_plans")
    row = cursor.fetchall()
    return row

def upload_filter_id():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT id,id FROM tp_filters")
    row = cursor.fetchall()
    return row

def upload_action_triggers():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT tag, tag FROM tp_action_triggers")
    row = cursor.fetchall()
    return row

def upload_rating_profile():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT tenant, tenant FROM tp_rating_profiles")
    row = cursor.fetchall()
    return row

def user_tenant():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT tenant, tenant FROM pay_user")
    row = cursor.fetchall()
    return row

def user_username():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT username, username FROM pay_user")
    row = cursor.fetchall()
    return row

def upload_category():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT category, category FROM tp_rating_profiles")
    row = cursor.fetchall()
    return row

def upload_subject():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT subject,subject FROM tp_rating_profiles")
    row = cursor.fetchall()
    return row

def upload_account():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT account, account FROM tp_account_actions")
    row = cursor.fetchall()
    return row

def upload_actions_plan():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT tag, tag FROM tp_action_plans")
    row = cursor.fetchall()
    return row

def upload_actions_id():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT tag, tag FROM tp_actions")
    row = cursor.fetchall()
    return row

def get_filter():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT id, id FROM tp_filters")
    row = cursor.fetchall()
    return  row

def get_supplier_id():
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT id, id FROM tp_suppliers")
    row = cursor.fetchall()
    return row

class CreateTpRatingProfiles(ModelForm):
    class Meta:
        models = TpRatingProfiles
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(CreateTpRatingProfiles,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(choices=user_tenant()))
        self.fields['rating_plan_tag'] = forms.CharField(widget=forms.Select(choices=upload_rating_plan()))

class CreateTpAccountActions(ModelForm):

    class Meta:
        models = TpAccountActions
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(CreateTpAccountActions,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(choices=user_tenant()))
        self.fields['action_plan_tag'] = forms.CharField(widget=forms.Select(choices=upload_actions_plan()))
        self.fields['action_triggers_tag'] = forms.CharField(widget=forms.Select(choices=upload_action_triggers()))

class CreateTpActionTriggers(ModelForm):
    class Meta:
        models = TpActionTriggers
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(CreateTpActionTriggers,self).__init__(*args,**kwargs)
        self.fields['actions_tag'] = forms.CharField(widget=forms.Select(choices=upload_actions_id()))

class CreateTpActionPlans(ModelForm):
    class Meta:
        models = TpActionPlans
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(CreateTpActionPlans,self).__init__(*args,**kwargs)
        self.fields['actions_tag'] = forms.CharField(widget=forms.Select(choices=upload_actions_id()))

class CreateChargers(ModelForm):
    class Meta:
        model = TpChargers
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(CreateChargers,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(choices=user_tenant()))
        self.fields['filter_ids'] = forms.CharField(widget=forms.Select(choices=upload_filter_id()))
        self.fields['attribute_ids'] = forms.CharField(widget=forms.Select(choices=upload_attribute_id()))

class CreateTpTimings(ModelForm):
    class Meta:
        models = TpTimings
        fields = '__all__'
        widgets = {
            'time': TimeInput(format=['%H:%M:%S'])
        }

class CreateTpSharedGroups(ModelForm):
    class Meta:
        models = TpSharedGroups
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(CreateTpSharedGroups,self).__init__(*args,**kwargs)
        self.fields['account'] = forms.CharField(widget=forms.Select(choices=upload_account()))

class CreateTpSupplier(ModelForm):
    class Meta:
        models = TpSuppliers
        fields = '__all__'


    def __init__(self,*args,**kwargs):
        super(CreateTpSupplier,self).__init__(*args,**kwargs)
        self.fields['tenant'] =  forms.CharField(widget=forms.Select(choices=user_tenant()))
        self.fields['supplier_ratingplan_ids'] = forms.CharField(widget=forms.Select(choices=upload_rating_plan()))

class CreateTpFilter(ModelForm):
    class Meta:
        models = Filters
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(CreateTpFilter,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(choices=user_tenant()))

class CreateTpAttributes(ModelForm):
    class Meta:
        models = TpAttributes
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(CreateTpAttributes,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(choices=user_tenant()))
        self.fields['filter_ids'] = forms.CharField(widget=forms.Select(choices=upload_filter_id()))


class CreateResource(ModelForm):
    class Meta:
        models = TpResources
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(CreateResource,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(choices=user_tenant()))
        self.fields['filter_ids'] = forms.CharField(widget=forms.Select(choices=upload_filter_id()))


class CreateThreshold(ModelForm):
    class Meta:
        models = TpThresholds
        fields = '__all__'

    def __init__(self,*args,**kwargs):
        super(CreateThreshold,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(choices=user_tenant()))
        self.fields['filter_ids'] = forms.CharField(widget=forms.Select(choices=upload_filter_id()))
        self.fields['action_ids'] = forms.CharField(widget=forms.Select(choices=upload_actions_id()))

class CreateStats(ModelForm):
    class Meta:
        model = TpStats
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super(CreateStats,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(choices=user_tenant()))
        self.fields['filter_ids'] = forms.CharField(widget=forms.Select(choices=upload_filter_id()))

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class BalanceAddForm(forms.Form):
    tenant          = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    account         = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    balanceuuid     = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}), disabled='disabled',required=False)
    balanceid       = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),disabled='disabled',required=False)
    balancetype     = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    expirytime      = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}), required=False, validators=[activation_time_validate])
    ratingsubject   = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Optional:The RatingSubject of the Balance'}), required=False)
    categories      = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Optional:Type of record specifies the kind of transmission this rate'}),required=False)
    destinationids  = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Optional:The destination id/tag described in the Destinations'}), required=False)
    timingids       = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Optional:A timing (one time or recurrent) at which the action group will be executed'}), required=False)
    weight          = forms.IntegerField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Optional:Specifies the order for these timings to be evaluated'}), required=False)
    sharedgroups    = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Optional:In case of the account uses any shared group for the balances.'}),required=False)
    overwrite       = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Optional: '}),required=False)
    blocker         = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Optional: '}),required=False)
    disabled        = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),required=False)
    value           = forms.DecimalField(decimal_places=2)

    def __init__(self, *args, **kwargs):
        super(BalanceAddForm,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(attrs={'class':'form-control'},choices=user_tenant()))

class CostForm(forms.Form):
    tenant          = forms.CharField(widget=forms.Select(attrs={'class':'form-control','placeholder':'Tenant Domain of Carrier'}))
    category        = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Type of record specifies the kind of transmission this rate'}))
    subject         = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'The RatingSubject of the Balance'}))
    answertime      = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'The start time for this time period '}),validators=[activation_time_validate])
    destination     = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Destinations 7-digit dialing: 1NXX xxxx (NPA)'}), validators=[destinations_validate])
    usage           = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Valid time units are "ns", "us" (or "µs"), "ms", "s", "m", "h"'}), validators=[usage_validate])

    def __init__(self, *args, **kwargs):
        super(CostForm,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(attrs={'class':'form-control'},choices=user_tenant()))


class SupplierQuery(forms.Form):
    tenant = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))
    id = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))
    time =forms.CharField(widget=forms.TextInput(attrs={'class':'form-control','placeholder': 'Time in place to call'}),required=False)
    accont = forms.ChoiceField(widget=forms.Select(attrs={'class': 'form-control'}))
    destinations = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destinations'}))

    def __init__(self, *args, **kwargs):
        super(SupplierQuery,self).__init__(*args,**kwargs)
        self.fields['tenant'] = forms.CharField(widget=forms.Select(attrs={'class':'form-control'},choices=user_tenant()))
        self.fields['id'] = forms.CharField(widget=forms.Select(attrs={'class':'form-control'},choices=get_supplier_id()))
        self.fields['accont'] = forms.CharField(widget=forms.Select(attrs={'class':'form-control'},choices=upload_account()))
