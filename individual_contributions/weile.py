from functools import reduce
import re
import csv

def parse_CSV(path):
    read_dictionary = csv.DictReader(open(path))
    return (read_dictionary.fieldnames, list(read_dictionary))

def create_filter_function_by_header(header):
    def create_filter_function_by_value(value):
        record_value = value

        def get_record_value():
            return record_value

        def filter_function(data):
            return filter(lambda x: x[header] == value, data)
        return (get_record_value, filter_function)
    return create_filter_function_by_value

def sanitise_data_input(entry: str):
    return " ".join(re.split("\s+", entry)).strip()

def calculate_total_quantity(accumulator, quantity):
    return accumulator + quantity

def main():
    pass

if __name__ == "__main__":
    main()