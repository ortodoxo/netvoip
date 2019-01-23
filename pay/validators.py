import csv
import os
import io
import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


REQUIRED_HEADER  = ['NPANXX','Interstate','Intrastate','Indeterminate']

def csv_file_validator(value):
    filename, ext = os.path.splitext(value.name)
    if  str(ext) != '.csv':
         raise ValidationError("Must be a csv file")
    decoded_file = value.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)
    reader = csv.reader(io_string, delimiter=';', quotechar='|')
    header_ = next(reader)[0].split(',')
    if header_[-1] == '':
        header_.pop()
    required_header = REQUIRED_HEADER
    if required_header != header_:
        raise ValidationError("Invalid File. Please use valid CSV Header ('NPANXX','Interstate','Intrastate','Indeterminate') and/or Staff Upload Template.")

# let open the file eagin with another reader
    reader = csv.reader(io_string, delimiter=',')
    for row in reader:
        if re.match('^(1[2-9]|[2-9])([0-9]{2})([2-9][0-9]{2})',row[0]) == None:
            raise ValidationError("The prefix will be valid")
    return True

def activation_time_validate(value):
    #validate the datetime format of cgrates 2014-01-14T00:00:00Z
    if re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z',value) == None:
        raise  ValidationError("The date time for cgrates need to be valid")
    return  True