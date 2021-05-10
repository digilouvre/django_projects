import csv

from dl.models import ProvinceOrState

def run():
    fhand = open('dl/province_tax_rates2.csv')
    reader = csv.reader(fhand)

    ProvinceOrState.objects.all().delete()
    for row in reader:
        print(row)
        p = ProvinceOrState(name=row[0], code=row[1], rate=row[2])
        p.save
        print(p.id)