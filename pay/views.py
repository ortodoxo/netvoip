from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf.urls import url
from django.core.paginator import Paginator
from pay.models import TpAccountActions, Cdrs, CgratesAPI, Balance, CostModel, TpSuppliers, Suppliers_Query, User
from pay.exception import CostError, BalanceError, SupplierError
from django.views import View
from .forms import LoginForm, BalanceAddForm, CostForm, SupplierQuery
from django.db.models import Sum, Avg
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

class Cdrs_for_Page(LoginRequiredMixin,View):
    login_url = '../login'
    template_name = 'pay/dashboard.html'
    context = {}
    costlist = []
    datelist = []
    page = None

    def get(self, request, *args, **kwargs):
        self.costlist = []
        self.datelist = []
        if self.request.user.is_superuser:
            cdrserver = Cdrs.objects.filter(tenant=self.request.user.tenant) \
                .exclude(run_id='*raw') \
                .exclude(extra_info='REPLY_TIMEOUT') \
                .extra(select={"setup_time": "DATE_FORMAT(setup_time,'%%Y-%%m-%%d')"})\
                .values('setup_time', 'account') \
                .annotate(acd=Avg('usage')/60000000000) \
                .annotate(acc=Avg('cost')) \
                .annotate(cost=Sum('cost')) \
                .annotate(usage=Sum('usage')/60000000000) \
                .order_by('-setup_time')
        else:
            cdrserver = Cdrs.objects.filter(tenant=self.request.user.tenant) \
                .exclude(run_id='*raw') \
                .exclude(extra_info='REPLY_TIMEOUT') \
                .extra(select={"setup_time": "DATE_FORMAT(setup_time,'%%Y-%%m-%%d')"}) \
                .values('setup_time',  'account') \
                .filter(account=self.request.user.username) \
                .annotate(acd=Avg('usage')/60000000000) \
                .annotate(acc=Avg('cost')) \
                .annotate(cost=Sum('cost')) \
                .annotate(usage=Sum('usage')/60000000000) \
                .order_by('-setup_time')
        self.page = Paginator(cdrserver, 2)
        num = kwargs['page']
        cdrserver = self.page.page(num)
        for data in cdrserver:
            self.costlist.append(str(data['cost']))
            self.datelist.append(str(data['setup_time']))
        self.context['costs'] = self.costlist
        self.context['dates'] = self.datelist
        self.context['cdrs'] = cdrserver
        self.context['pages'] = self.page
        return render(request,self.template_name, context=self.context)

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
    context = {'error':'','balance_error':'','expresion':'','mensage':''}


    def get_object(self, id):
        object = get_object_or_404(TpAccountActions, pk=id)
        return object

    def get(self, request, *args, **kwargs):
        AccountActions = self.get_object(kwargs['id'])
        balance = Balance()
        try:
            balance.GetAccount(AccountActions.tenant,AccountActions.account)
        except BalanceError as e:
            messages.error(request,e.mensage)

        self.initial = {'balanceid':AccountActions.account,'tenant':AccountActions.tenant,'account':AccountActions.account,
                        'value':round(balance.Value,2), 'balancetype':balance.BalanceType, 'balanceuuid':balance.BalanceUuid,'balanceid':balance.BalanceId,
                        'expirytime':balance.ExpiryTime,'ratingsubject':balance.RatingSubject,'categories':balance.Categories,
                        'destinationids':balance.DestinationIds,'timingids':balance.TimingIds,'weight':balance.Weight,'sharedgroups':balance.SharedGroups,
                        'disabled':balance.Disabled}
        self.context['Value'] = balance.Value
        self.context['UnitCounters'] = balance.UnitCounters
        self.context['Tenant'] = AccountActions.tenant
        self.context['ID'] = AccountActions.id
        self.context['Account'] = AccountActions.account
        form = self.form_class(initial=self.initial)
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        self.context['form'] = form
        balance_error = False
        if form.is_valid():
            tenant = form.cleaned_data['tenant']
            account = form.cleaned_data['account']
            balance = Balance()
            try:
                balance.GetAccount(tenant,account)
                form.cleaned_data['balanceid'] = balance.BalanceId
                form.cleaned_data['balanceuuid'] = balance.BalanceUuid
                json = balance.SetBalance(form.cleaned_data['tenant'],form.cleaned_data['account'],form.cleaned_data['balancetype'],form.cleaned_data['balanceuuid'],form.cleaned_data['balanceid'],form.cleaned_data['value'])
            except BalanceError as e:
                balance_error = True
                self.context['balance_error'] = balance_error
                self.context['expresion'] = e.expresion
                self.context['mensage'] = e.mensage
                fullmsg = str(e.expresion)
                fullmsg += ' '+str(e.mensage)
                messages.error(request,fullmsg)
                return HttpResponseRedirect(reverse('balance_add',kwargs={'id':kwargs['id'],'tenant':kwargs['tenant']}))
            messages.success(request,'The balance has be update succesfully')
            return HttpResponseRedirect(reverse('balance_add',kwargs={'id':kwargs['id'],'tenant':kwargs['tenant']}))
        else:
            for field in form.errors:
                form.fields[field].widget.attrs.update({'class':'form-control is-invalid'})
            self.context['error'] = form.errors
            messages.error(request,form.errors)
            return HttpResponseRedirect(reverse('balance_add',kwargs={'id':kwargs['id'],'tenant':kwargs['tenant']}))

class Cost(LoginRequiredMixin, View):
    form_class = CostForm
    model = TpAccountActions
    initial = {'key': 'value'}
    template_name = 'pay/Cost.html'
    context = {}
    costm = CostModel()

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        self.context['form'] = form
        if form.is_valid():
            tenant = form.cleaned_data['tenant']
            category = form.cleaned_data['category']
            subject = form.cleaned_data['subject']
            answertime = form.cleaned_data['answertime']
            destination = form.cleaned_data['destination']
            usage = form.cleaned_data['usage']
            try:
                self.costm.GetCost(tenant,category,subject,answertime,destination,usage)
            except CostError as e:
                costerror = True
                self.context['costerror'] = costerror
                self.context['expresion'] = e.expresion
                self.context['mensage'] = e.mensage
                return render(request,self.template_name,self.context)

            self.context['sucess'] = True
            self.context['Tenant'] = self.costm.Tenant
            self.context['Usage'] = self.costm.Usage
            self.context['Cost'] = self.costm.Cost
            self.context['ChargesUsage'] = self.costm.ChargesUsage
            self.context['ChargesCost'] = self.costm.ChargesCost
            self.context['ChargesCompressFactor'] = self.costm.ChargesCompressFactor
            return render(request,self.template_name,self.context)
        else:
            for field in form.errors:
                form.fields[field].widget.attrs.update({'class':'form-control is-invalid'})

            return render(request,self.template_name,self.context)


class SupplierGet(LoginRequiredMixin,View):
    form = SupplierQuery
    model = TpSuppliers
    initial = {'key': 'value'}
    template_name = 'pay/SupplierQuery.html'
    supplier_query = Suppliers_Query()
    context = {}

    def get(self,request,*args,**kwargs):
        self.context['form'] = self.form
        return render(request,self.template_name,self.context)

    def post(self,request,*args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            tenant = form.cleaned_data['tenant']
            id = form.cleaned_data['id']
            time = form.cleaned_data['time']
            accont = form.cleaned_data['accont']
            destinations = form.cleaned_data['destinations']
            try:
                self.supplier_query.GetSuppliers(tenant,id,time,accont,destinations)
            except SupplierError as e:
                self.context['suppliererror'] = True
                self.context['expresion'] = e.expresion
                self.context['mensage'] = e.mensage
                return render(request,self.template_name,self.context)

            self.context['ProfileID'] = self.supplier_query.profileid
            self.context['Sorting'] = self.supplier_query.sorting
            self.context['SortedSuppliers'] = self.supplier_query.SortedSuppliers
            return render(request,'pay/SupplierResult.html',self.context)


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
                return HttpResponseRedirect('../dashboard/1/')
            else:
                messages.error(request,'Username or Password incorrect pleas try egain')
                return HttpResponseRedirect('../')

class LogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('../')

