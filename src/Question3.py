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

    # Split the input string based on 1 or more whitespaces "\s+" to obtain an array of strings that form the words in the input
    # Join the list of strings with a single whitespace as the delimiter, thereby eliminating additional whitespaces in between
    # Strip() on the resultant string to remove leading & trailing whitespaces
    return " ".join(re.split("\s+", entry)).strip()

def calculate_sum(accumulator, value):
    '''
    A function to be passed in as argument to reduce() for calculating summation of values
    '''
    return accumulator + value

def calculate_total_quantity(record):
    '''
    Calculate the total quantity from the "Quantity" field/header from the record parameter

    :param record: A collection in the form of list of dictionaries like [{...}, {....}, {....}]
    :return: The sum of values (in float) for the "Quantity" header for all dictionaries in the collection
    '''
    return reduce(calculate_sum, [float(entry["Quantity"]) for entry in record])

def calculate_total_revenue(record):
    '''
    Calculate the total revenue by summing the products of the values for "Quantity" and "Price" from the record parameter

    :param record: A collection in the form of list of dictionaries like [{...}, {...}, {...}]
    :return: The sum of revenue for all dictionaries in the collection, or 0 if 'record' is an empty collection
    '''
    if len(record) > 0:
        return reduce(calculate_sum, [float(entry["Quantity"]) * float(entry["Price"]) for entry in record])
    return 0

'''
This function is used to create various functions to be applied to the csv data for filtering purposes

Function currying is utilised, where the outer function(?) returns another function reference to be applied for
more specification of the filtering criteria

create_filter_function_by_header() is to designate the header (or column of the csv file) where the filtering is to be performed.
create_filter_function_by_value() is to designate the value to be compared against the entries of the csv file to filter the records.
get_filtered_list() is the actual function that returns the actual filtered list based on the specified predicates/criteria
'''
def create_filter_function_by_header(header):
    '''
    Create a function to filter the data of the csv file based on the designated header

    :param header: The header to be used as a predicate for filtering the records
    :return: A function for filtering the data of the csv file based on the designated value
    '''
    def create_filter_function_by_value(value):
        '''
        Create a function to filter the data of the csv file based on the designated value

        :param value: The value to be used as a predicate for filtering the records
        :return: A function to obtain a list of dictionaries containing the filtered records
        '''
        def get_filtered_list(data):
            '''
            Filter the data parameter (list of dictionaries) based on the predicates designated by the two outer functions

            :param data: The data of the csv file to be filtered (in the form of a list of dictionaries)
            :return: A list of dictionaries containing only the records for the designated header and value
            '''
            return list((filter(lambda x: x[header] == value, data)))
        return get_filtered_list
    
    return create_filter_function_by_value

# An exception to the primary data filtering approach, as it uses a different predicate for comparing the entries
# It filters on the "Date" field based on the specified month, which is a specific slice from the string of the actual data entries
def create_date_filter_function_on_month(month):
    '''
    Create a function to filter the data of the csv file on the "Date" field, based on the designated month value

    :param month: The month value to be used as a predicate for filtering the records
    :return: A function to obtain a list of dictionaries containing the filtered records
    '''
    def get_filtered_list(data):
        '''
        Filter the data parameter based on the 'month' predicated designated by the outer function

        :param data: The data of the csv file to be filtered (in the form of a list of dictionaries)
        :return: A list of dictionaries containing only the records for the designated header and value
        '''
        return list(filter(lambda record: int(record["Date"][3:5]) == int(month), data)) # or just compare the string?
    return get_filtered_list

''' These two functions are extracted to fulfill the recursive requirement '''
def print_quantity_based_summary(zip_list):
    '''
    Print a summary based on the "Quantity" header from the zip_list parameter recursively
    '''
    if (len(zip_list) == 0):
        print()
    else:
        print(f"{zip_list[0][0]}: {zip_list[0][1]:.2f} units sold")
        print_quantity_based_summary(zip_list[1:])

def print_revenue_based_summary(zip_list):
    '''
    Print a summary based on the calculated revenue from the zip_list parameter recursively
    '''
    if (len(zip_list) == 0):
        print()
    else:
        print(f"{zip_list[0][0]}: ${zip_list[0][1]:.2f} generated")
        print_revenue_based_summary(zip_list[1:])

def main():
    header, data = parse_CSV("restaurant_sales_data.csv")
    sanitised_data = [{sanitise_data_input(key): sanitise_data_input(value) for key, value in record.items()} for record in data]

    # Overall Summary
    # print_list = apply_function_for_list(print)
    # map(print_list, header)
    print("Header of the dataset")
    print("---------------------")
    print(*header, sep=" | ")
    print()

    # Dict of header -> set of unique values of the column
    header_to_values = {
        h: set([record[h] for record in sanitised_data]) 
        for h in header
    }
    # List of filter functions on header
    header_filter_functions = list(map(create_filter_function_by_header, header))
    # Dict of header to the respective filter function on header
    header_to_header_filter_func = {
        header_key: header_func 
        for header_key, header_func in zip(header, header_filter_functions)
    }
    # Dict of header to the respective list of filter functions on their unique values
    header_to_unique_value_filter_func = {
        key: list(map(value, header_to_values[key])) 
        for key, value in header_to_header_filter_func.items()
    }
    # Function variable for mapping
    filter_from_dataset = lambda func: func(sanitised_data)
 
    ''' Question 3: Who is the best performing manager in terms of revenue '''
    print("Analysis based on Manager (Question 3)")
    print("--------------------------------------")

    manager_unique_values = header_to_values["Manager"]
    manager_filtered_records = list(map(filter_from_dataset, header_to_unique_value_filter_func["Manager"]))
    manager_total_revenue = list(map(calculate_total_revenue, manager_filtered_records))

    print("Managers employed by the restaurant company: ")
    print(*manager_unique_values, sep=" | ", end="\n\n")

    print("Revenue generated by each manager")
    print_revenue_based_summary(list(zip(manager_unique_values, manager_total_revenue)))
    
    manager_revenue = {}
    for record in sanitised_data:
        price = float(record["Price"])
        quantity = float(record["Quantity"])
        revenue = price * quantity

        manager_name = record["Manager"]

        if manager_name in manager_revenue:
            manager_revenue[manager_name] += revenue
        else:
            manager_revenue[manager_name] = revenue
    best_manager, best_revenue = max(manager_revenue.items(), key=lambda item: item[1])

    # print("Total revenue by manager:")
    # for manager, revenue in manager_revenue.items():
    #     print(f"- {manager}: {revenue:.2f}")

    print("\nBest Performing Manager")
    print(f"{best_manager} because his revenue is the highest ({best_revenue:.2f})")

if __name__ == "__main__":
    main()


