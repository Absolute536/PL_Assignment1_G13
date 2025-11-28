from functools import reduce
import re
import csv

def parse_CSV(path):
    '''
    Parse a CSV file given a file path

    :param path: The file path to the CSV file 
    :return: A tuple of two elements, (a list of headers, a list of dictionaries containing the data)
    '''
    read_dictionary = csv.DictReader(open(path))
    return (read_dictionary.fieldnames, list(read_dictionary))

def sanitise_data_input(entry: str):
    '''
    Sanitise the input string parameter

    :param entry: A string to be sanitised 
    :return: A string argument, with any leading & trailing whitespaces removed and also any additional whitespaces between words removed

    Example: 
    Pass in: "   Hello   World!        "
    Returns: "Hello World!"
    '''
    return " ".join(re.split("\s+", entry)).strip()

def calculate_sum(accumulator, value):

    return accumulator + value

def create_filter_function_by_header(header):

    def create_filter_function_by_value(value):

        def get_filtered_list(data):
            
            return list((filter(lambda x: x[header] == value, data)))
        
        return get_filtered_list
    
    return create_filter_function_by_value

def main():
    header, data = parse_CSV("restaurant_sales_data.csv")
    sanitised_data = [{sanitise_data_input(key): sanitise_data_input(value) for key, value in record.items()} for record in data]

if __name__ == "__main__":
    main()


