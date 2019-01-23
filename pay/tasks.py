from __future__ import absolute_import, unicode_literals
from celery import shared_task
from pay.models import RateDeck
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist
import csv
import requests
import json

SERVER = 'http://192.168.100.142:2080/jsonrpc'
HEAD = {'content-type':'application/json'}

@shared_task()
def delete_rating_plan(name):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tp_rating_plans WHERE tag LIKE %s",[name+'_%'])


@shared_task()
def uploadrate(ratedeck_pk):
    ListTpDestinations = []
    ListTpRates = []
    ListTpDestinationsRate = []
    ListTpRatinPlan = []
    tagid = 'CgratesPay'
    if RateDeck.objects.filter(pk = ratedeck_pk).exists():
        try:
            ratedeck = RateDeck.objects.get(pk=ratedeck_pk)
        except ObjectDoesNotExist:
            print("fuck dont existe when i send the id " + str(ratedeck_pk))
        with open(ratedeck.filename.path) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=str(','))
            for row in reader:
                ID = 'USA_'+row['NPANXX']
                Prefix = row['NPANXX']
                ListTpDestinations.append([tagid,ID ,Prefix])
                create_rate(row,ratedeck.carrier.rate,ListTpRates, tagid)
                create_destinationrates(row,ListTpDestinationsRate, tagid)
                create_rating_plan(row,ratedeck.carrier.nameid,tagid,ListTpRatinPlan)
            write_prefix(ListTpDestinations)
            write_rate(ListTpRates)
            write_destinationsrate(ListTpDestinationsRate)
            write_ratin_plan(ListTpRatinPlan)

            '''indet = ratedeck.carrier.nameid + str('_INDET')
            inter = ratedeck.carrier.nameid + str('_INTER')
            intra = ratedeck.carrier.nameid + str('_INTRA')
            LoadRatingPlan(intra,inter,indet)'''
        csvfile.close()
    else:
        print("No se ejecuto ni pinga por q no existe")


def write_ratin_plan(ListTp):
    RatingPlans = 'carrier/RatingPlans.csv'
    myFile = open(RatingPlans, 'w')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(ListTp)
    cursor = connection.cursor()
    cursor.execute("LOAD DATA LOCAL INFILE %s IGNORE INTO TABLE tp_rating_plans FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' (tpid, tag, destrates_tag, timing_tag, weight)",[RatingPlans])
    myFile.close()

def write_destinationsrate(ListTp):
    DestinationRates = 'carrier/DestinationRates.csv'
    myFile = open(DestinationRates, 'w')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(ListTp)
    cursor = connection.cursor()
    cursor.execute("LOAD DATA LOCAL INFILE %s IGNORE INTO TABLE tp_destination_rates FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' (tpid, tag, destinations_tag, rates_tag, rounding_method, rounding_decimals, max_cost, max_cost_strategy)",[DestinationRates])
    myFile.close()


def write_rate(ListTp):
    CsvRates = 'carrier/Rates.csv'
    myFile = open(CsvRates, 'w')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(ListTp)
    cursor = connection.cursor()
    cursor.execute("LOAD DATA LOCAL INFILE 'carrier/Rates.csv' IGNORE INTO TABLE tp_rates FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' (tpid, tag, connect_fee, rate, rate_unit, rate_increment, group_interval_start)")
    myFile.close()


def write_prefix(ListTp):
    CsvDestinations = 'carrier/Destinations.csv'
    myFile = open(CsvDestinations, 'w')
    with myFile:
        writer = csv.writer(myFile)
        writer.writerows(ListTp)
    cursor = connection.cursor()
    cursor.execute("LOAD DATA LOCAL INFILE 'carrier/Destinations.csv' IGNORE  INTO TABLE tp_destinations FIELDS TERMINATED BY ',' LINES TERMINATED BY '\r\n' (tpid, tag, prefix)")
    myFile.close()

def create_rate(data, carrier_rate, ListTp, tagid):
    InterstateTag = str('RT_'+str(data['Interstate']).split('.')[1]+'CNT')
    IntrastateTag = str('RT_'+str(data['Intrastate']).split('.')[1]+'CNT')
    IndeterminateTag = str('RT_'+str(data['Indeterminate']).split('.')[1]+'CNT')

    InterstateRate = data['Interstate']
    IntrastateRate = data['Intrastate']
    IndeterminateRate = data['Indeterminate']

    ListTp.append([tagid,InterstateTag,'0',InterstateRate,'60s',carrier_rate,'0s'])
    ListTp.append([tagid,IntrastateTag,'0',IntrastateRate,'60s',carrier_rate,'0s'])
    ListTp.append([tagid,IndeterminateTag,'0',IndeterminateRate,'60s',carrier_rate,'0s'])


def create_destinationrates(data, ListTp, tagid):
    IndetTag = str(data['Indeterminate']).split('.')[1]
    InterTag = str(data['Interstate']).split('.')[1]
    IntraTag = str(data['Intrastate']).split('.')[1]

    InterstateTag = str('RT_'+str(data['Interstate']).split('.')[1]+'CNT')
    IntrastateTag = str('RT_'+str(data['Intrastate']).split('.')[1]+'CNT')
    IndeterminateTag = str('RT_'+str(data['Indeterminate']).split('.')[1]+'CNT')

    tag_indet = str('DR_'+data['NPANXX']+'_'+IndetTag+'CNT')
    tag_inter = str('DR_'+data['NPANXX']+'_'+InterTag+'CNT')
    tag_intra = str('DR_'+data['NPANXX']+'_'+IntraTag+'CNT')

    tag_dest = str('USA_'+data['NPANXX'])

    ListTp.append([tagid,tag_indet,tag_dest,IndeterminateTag,'*up','4','0'])
    ListTp.append([tagid,tag_inter,tag_dest,InterstateTag,'*up','4','0'])
    ListTp.append([tagid,tag_intra,tag_dest,IntrastateTag,'*up','4','0'])


def create_rating_plan(data, carrier,tagid, ListTp):
    IndetTag = str(data['Indeterminate']).split('.')[1]
    InterTag = str(data['Interstate']).split('.')[1]
    IntraTag = str(data['Intrastate']).split('.')[1]

    tag_indet = str('DR_'+data['NPANXX']+'_'+IndetTag+'CNT')
    tag_inter = str('DR_'+data['NPANXX']+'_'+InterTag+'CNT')
    tag_intra = str('DR_'+data['NPANXX']+'_'+IntraTag+'CNT')

    carrier_indet = carrier + str('_INDET')
    carrier_inter = carrier + str('_INTER')
    carrier_intra = carrier + str('_INTRA')

    ListTp.append([tagid,carrier_indet, tag_indet,'*any',10.00])
    ListTp.append([tagid,carrier_inter,tag_inter,'*any',10.00])
    ListTp.append([tagid,carrier_intra,tag_intra,'*any',10.00])

def LoadRatingPlan(intra, inter, indet):
    payload = {"id": 1,"method":"ApierV1.LoadRatingPlan","params":[{"TPid":"CgratesPay", "RatingPlanId":intra}]}
    requests.post(SERVER,headers=HEAD,data=json.dumps(payload))
    payload = {"id": 1,"method":"ApierV1.LoadRatingPlan","params":[{"TPid":"CgratesPay", "RatingPlanId":inter}]}
    requests.post(SERVER,headers=HEAD,data=json.dumps(payload))
    payload = {"id": 1,"method":"ApierV1.LoadRatingPlan","params":[{"TPid":"CgratesPay", "RatingPlanId":indet}]}
    requests.post(SERVER,headers=HEAD,data=json.dumps(payload))


