import csv
from .models import TpDestinations,TpRates


def uplaod_ratedeck(file):
    with open(file) as csvfile:
        # the file need to be Prefix,Inter,Intra,Indet
        reader = csv.DictReader(csvfile)
        for row in reader:
            destination = TpDestinations.objects.create(prefix=row['Prefix'])
            rates = TpRates.objects.create(rate=row['Inter'])
            rates.rate=row['Intra']
            rates.rate=row['Indet']



