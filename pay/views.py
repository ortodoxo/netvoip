from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from pay.models import TpAccountActions, Cdrs, TpUsers, CgratesAPI, Balance, CostModel, TpSuppliers, Suppliers_Query
from django.views import View
from .forms import LoginForm, BalanceAddForm, CostForm, SupplierQuery
from datetime import datetime
import requests
import json


SERVER = 'http://192.168.100.142:2080/jsonrpc'
HEAD = {'content-type':'application/json'}

class AccountList(LoginRequiredMixin,ListView):
    model = TpAccountActions
    login_url = '../login'
    template_name = 'pay/Account.html'
    context_object_name = 'acconts'

    def get_queryset(self):
        return TpAccountActions.objects.filter(tenant=self.request.user.tenant)


class CdrsLIst(LoginRequiredMixin,ListView):
    model = Cdrs
    login_url = '../login'
    template_name = 'pay/dashboard.html'
    context_object_name = 'cdrs'


    def get_queryset(self):
        return Cdrs.objects.exclude(run_id='*raw').filter(tenant=self.request.user.tenant).order_by('setup_time')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(CdrsLIst,self).get_context_data(**kwargs)
        costlist = []
        datelist = []
        usage = []

        datecostquery = Cdrs.objects.exclude(run_id='*raw').values('setup_time','cost','usage').order_by('setup_time')
        for data in datecostquery:
            costlist.append(str(data['cost']))
            datelist.append(str(data['setup_time'].strftime('%I:%M:%S')))
            usage.append(str(data['usage']))

        context['costs'] = costlist
        context['dates'] = datelist
        context['usage'] = usage
        return context


class AccountDetail(LoginRequiredMixin,DetailView):
    model = TpAccountActions
    login_url = '../login'
    template_name = 'pay/AccountDetail.html'

    def get_object(self, id):
        object  = get_object_or_404(TpAccountActions, pk=id)
        return object

    def get(self, request, id):
        self.object = self.get_object(id)
        tenant = self.object.tenant
        account = self.object.account
        balance = Balance()
        balance.GetAccount(tenant,account)
        context = self.get_context_data(object=json)
        context['Uuid'] = balance.BalanceUuid
        context['Value']  = balance.Value
        context['UnitCounters'] = balance.UnitCounters
        context['Tenant'] = self.object.tenant
        context['ID'] = self.object.id
        return self.render_to_response(context)

class Balance_Add(LoginRequiredMixin, View):
    form_class = BalanceAddForm
    initial = {'key': 'value'}
    template_name = 'pay/balance_add.html'


    def get_object(self, id):
        object = get_object_or_404(TpAccountActions, pk=id)
        return object

    def get(self, request, *args, **kwargs):
        AccountActions = self.get_object(kwargs['id'])
        balance = Balance()
        balance.GetAccount(AccountActions.tenant,AccountActions.account)
        self.initial = {'balanceid':AccountActions.account,'tenant':AccountActions.tenant,'account':AccountActions.account,
                        'value':balance.Value, 'balancetype':balance.BalanceType, 'balanceuuid':balance.BalanceUuid,'balanceid':balance.BalanceId,
                        'directions':balance.Directions,'expirytime':balance.ExpiryTime,'ratingsubject':balance.RatingSubject,'categories':balance.Categories,
                        'destinationids':balance.DestinationIds,'timingids':balance.TimingIds,'weight':balance.Weight,'sharedgroups':balance.SharedGroups,
                        'disabled':balance.Disabled}
        context = {}
        context['Value'] = balance.Value
        context['UnitCounters'] = balance.UnitCounters
        context['Tenant'] = AccountActions.tenant
        context['ID'] = AccountActions.id
        context['Account'] = AccountActions.account
        form = self.form_class(initial=self.initial)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            tenant = form.cleaned_data['tenant']
            account = form.cleaned_data['account']
            balance = Balance()
            balance.GetAccount(tenant,account)
            form.cleaned_data['balanceid'] = balance.BalanceId
            form.cleaned_data['directions'] = balance.Directions
            form.cleaned_data['balanceuuid'] = balance.BalanceUuid
            print(form.cleaned_data['value'])
            json = balance.SetBalance(form.cleaned_data['tenant'],form.cleaned_data['account'],form.cleaned_data['balancetype'],form.cleaned_data['balanceuuid'],form.cleaned_data['balanceid'],form.cleaned_data['directions'],form.cleaned_data['value'])
            print(json)
            return HttpResponseRedirect('../index')
        return HttpResponseRedirect('../../../dashboard/')

class Cost(LoginRequiredMixin, View):
    form_class = CostForm
    model = TpAccountActions
    initial = {'key': 'value'}
    template_name = 'pay/Cost.html'
    costm = CostModel()

    def get(self, request, *args, **kwargs):
        context = {}
        context['Tenant'] = self.costm.Tenant
        context['Usage'] = self.costm.Usage
        context['Cost'] = self.costm.Cost
        context['ChargesUsage'] = self.costm.ChargesUsage
        context['ChargesCost'] = self.costm.ChargesCost
        context['ChargesCompressFactor'] = self.costm.ChargesCompressFactor
        form = self.form_class(initial=self.initial)
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            tenant = form.cleaned_data['tenant']
            category = form.cleaned_data['category']
            subject = form.cleaned_data['subject']
            answertime = form.cleaned_data['answertime']
            destination = form.cleaned_data['destination']
            usage = form.cleaned_data['usage']
            self.costm.GetCost(tenant,category,subject,answertime,destination,usage)
        return HttpResponseRedirect('../cost')


class SupplierGet(LoginRequiredMixin,View):
    form = SupplierQuery
    model = TpSuppliers
    initial = {'key': 'value'}
    template_name = 'pay/SupplierQuery.html'
    supplier_query = Suppliers_Query()

    def get(self,request,*args,**kwargs):
        context = {}
        context['form'] = self.form
        return render(request,self.template_name,context)

    def post(self,request,*args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            tenant = form.cleaned_data['tenant']
            id = form.cleaned_data['id']
            context = form.cleaned_data['context']
            time = form.cleaned_data['time']
            event = form.cleaned_data['event']
            json = self.supplier_query.GetSuppliers(tenant,id,context,time,event)
            print(json)
        return HttpResponseRedirect('../supplierquery')




class UsersList(LoginRequiredMixin,ListView):
    model = TpUsers
    login_url = '../login'
    template_name = 'pay/Users.html'
    context_object_name = 'users'

class UserDetail(DetailView):
    model = TpUsers
    template_name = 'pay/UserDetail.html'


class LoginView(View):
    form_class = LoginForm
    initial = {'key': 'value'}
    template_name = 'pay/index.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request,username=username, password=password)
            if user is not None:
                login(request,user)
                return HttpResponseRedirect('../dashboard')
            else:
                return HttpResponseRedirect('../')

class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('../')

