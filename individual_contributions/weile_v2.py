# V2 modifications: 
# Generalised the create_filter_function() like the initial experiment in base.py (except for create_date_filter_function_on_month)
# This reduces the functions we need and reduce hard-coding stuff (I guess?)
# Important Note: unique_values sets need to be derived from the header_to_values sets to preserve the ordering between them and the list of filter functions
# The results are the same as the first version so should be correct
# Still a little bit messy, but should be sufficient (I think?)
# More cleanup later

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
    # Function variable(?) for mapping
    filter_from_dataset = lambda func: func(sanitised_data)
    '''
    Ok, let's summarise the process from the experiment (Product)
    1. obtain unique values for the header in a list
    2. 
    3. create a list of filter function for each of the unique values for that category by map() the unique values list with create_{header}_filter_function()
    4. get the filtered list of LISTS of RECORDS for each unique value for that category by applying each of the filter functions created to the sanitised_data
       the structure would be something like: [[{....}, {.....}, {.....}], [{....}, {.....}], [{....}, ...], ....]
    5. then we apply whatever function that we need to the filtered list for our desired operation/calculation
    6. for displaying the result, can use zip() on the initial unique values list and each of the resultant lists to create a list of tuples of the result, preserving the order
       note: on second thought, it's probably enought to just zip(unique values list, the desired resultant list) to print it and do it again for another resultant list
    
    Note: the ordering of the subsequent collections/list follows the initial set of unique values for the header category, and since set is unordered, we'll get a different ordering each time
          BUT
          we can still map the results by their position, since the subsequent lists are derived from the set
          just that need to zip() the set and the derived lists if we wanna do sorting to preserve the mapping correctly
    
    Update (23/11/2025):
    We have a renewed process (still the same but with a list of functions)

    1. get the list of header in the dataset and construct a dictionary of header -> a set of unique values for the respective header
    2. get the list of data entries in the dataset
    3. sanitise the data entries in the dataset
    4. construct a list of filter functions by the header or fieldnames of the dataset using the list of header from (1.)
    5. construct a dictionary, keyed by the header of the dataset, with their respective filter functions on header as the value-pair
       (* since the list in 4. is built from the header list in 1., that list must be used to preserve the ordering)
    6. construct a dictionary of header -> list of filter functions on the unique values for the header by transforming the dictionary from (5.)
       (* the dictionary in 1. is used to construct the respective value-pair in the dictionary, subsequent processing must be derived from 
        header_to_values to properly preserve the ordering)

    With the structure obtained in (6.), we can access the list of filter functions by the values through the header (key).
    Then, the overall process to obtain answers to each question is as below (still the same as v1).
    1. construct a set of unique values for the designated header/fieldname through header_to_values (IMPORTANT)
    2. constuct a list of filter functions on the specific values under the header through the set in (1.)
    3. get the filtered records in the form of a list of lists of records [[{ }, { }, { }, ...], [{ }, { }], [{ }, { }, { }, { }], ...] 
       by applying the sanitised dataset to each of the filter functions in the list from (2.)
    4. perform whatever manipulations/function for the desired calculations/operations based on the filtered records
    5. display the result in the terminal by either calling the more general recursive printing functions defined above, or construct a more 
       specific operation
    '''

    # Product based analysis
    print("Analysis based on Product (Question 1)")
    print("--------------------------------------")
    print("Products Offered by the Restaurant Company: ")
    print(*header_to_values["Product"], sep=" | ")
    print()

    # Ok I think I know how to do this
    # unique_product_values
    # list of filter functions for product
    # list of lists of record for each product
    # then calculate on each list, pack into another list of sum
    # then use zip()
    # since it uses the order from unique_product_values (a set), every subsequent derivation follows that order
    # though it might be indeterministic for the set but the order is preserved, so zip will work

    ''' Question 1: What is the best selling item in terms of quantity and revenue across all locations '''
    # A set of unique values under "Product"
    product_unique_values = header_to_values["Product"]
    
    # A list of lists that contain records corresponding to each product ---> [[{.....}, {....}, {.....}], [{.....}], etc.]
    # product_filtered_records = [func(sanitised_data) for func in product_filter_function_list]
    product_filtered_records = list(map(filter_from_dataset, header_to_unique_value_filter_func["Product"]))

    # A list containing the sum of total quantity corresponding to each product ---> [total quantity for product_1, total quantity for product_2, ... for every product type]
    # reduce_product_quantity_func = lambda record: reduce(calculate_sum, [float(entry["Quantity"]) for entry in record])
    # Note to self: this works because we call map(), so map() unpack the list of lists of records into individual list of records, which is then feed into calculate_total_quantity
    #               that does further unpacking into records
    product_quantity_sum = list(map(calculate_total_quantity, product_filtered_records))

    # A list containing the total revenue (price * quantity) for each product type ---> [total revenue for product_1, total revenue for product_2, ... and so on]
    # reduce_product_revenue_func = lambda record: reduce(calculate_sum, [float(entry["Quantity"]) * float(entry["Price"]) for entry in record])
    product_total_revenue = list(map(calculate_total_revenue, product_filtered_records))

    ''' This is to find out the outlier, can be an additional part '''
    unique_prices_for_each_product = list(map(lambda record: set(entry["Price"] for entry in record), product_filtered_records))
    print("Unique Prices: ", end="")
    print(unique_prices_for_each_product, end="\n\n") # so there are outlier for Prices in Chicken Sandwiches and Fries (so THAT'S WHY they don't match up after calculation)
    ''' End of outlier investigation'''

    print("Quantity sold for each product")
    print_quantity_based_summary(list(zip(product_unique_values, product_quantity_sum)))

    print("Total revenue for each product")
    print_revenue_based_summary(list(zip(product_unique_values, product_total_revenue)))

    # Need to zip() the collection then sort, so that we preserve the ordering and consequently the identity of each collection
    # aggregate_product_result = zip(unique_product_values, sum_of_quantity_for_products, total_revenue_for_products)
    # We can't reuse the above collection to produce multiple sorted ones, cuz the first call to sorted() would exhaust the iterator for the collection already
    # making the next one return an [] empty list
    # also use sorted() instead of list.sort() for immutability
    sorted_product_aggregate_on_quantity = sorted(
        zip(product_unique_values, product_quantity_sum, product_total_revenue), 
        key = lambda x: x[1], 
        reverse=True
    )
    sorted_product_aggregate_on_revenue = sorted(
        zip(product_unique_values, product_quantity_sum, product_total_revenue), 
        key = lambda x: x[2], 
        reverse=True
    ) 

    print("Top 3 best-selling products in terms of quantity sold across all citites")
    for i in range(len(sorted_product_aggregate_on_quantity) if len(sorted_product_aggregate_on_quantity) < 3 else 3):
        print("Top " + str(i + 1) + ": " + sorted_product_aggregate_on_quantity[i][0] + f" ({sorted_product_aggregate_on_quantity[i][1]:.2f} units sold)")
    print()

    print("Top 3 best-selling products in terms of total revenue generated across all cities")
    for i in range(len(sorted_product_aggregate_on_revenue) if len(sorted_product_aggregate_on_revenue) < 3 else 3):
        print("Top " + str(i + 1) + ": " + sorted_product_aggregate_on_revenue[i][0] + f" (${sorted_product_aggregate_on_revenue[i][2]:.2f} revenue)")
    print()


    ''' Question 2: Which location is the most profitable in terms of revenue & their monthly average revenue '''
    print("Analysis based on Branch Location / City (Question 2)")
    print("-----------------------------------------------------")
    
    # First we need to find out the sales data contain records for how many months (it's 2 duh, but let's try to find it programmitically)
    date_unique_values = header_to_values["Date"]
    date_unique_month_values = set(date[3:5] for date in date_unique_values) # the 3rd and 4th index contains the month (kinda fragile but whatever~)
    months_recorded = len(date_unique_month_values)
    
    city_unique_values = header_to_values["City"]
    city_filtered_records = list(map(filter_from_dataset, header_to_unique_value_filter_func["City"]))

    city_total_revenue = list(map(calculate_total_revenue, city_filtered_records))
    city_average_monthly_revenue = list(
        map(
            lambda revenue: revenue / months_recorded, 
            list(map(calculate_total_revenue, city_filtered_records))
        )
    )

    print("Branch locations (city) of the restaurant company: ")
    print(*city_unique_values, sep=" | ", end="\n\n")

    print("Total revenue for each branch location (city)")
    print_revenue_based_summary(list(zip(city_unique_values, city_total_revenue)))

    print("Average monthly revenue for each branch location (city)")
    print_revenue_based_summary(list(zip(city_unique_values, city_average_monthly_revenue)))

    sorted_city_aggregate_on_total_revenue = sorted(
        zip(city_unique_values, city_total_revenue), 
        key=lambda x: x[1], 
        reverse=True
    )
    print("The most profitable branch (city) for the restaurant company in terms of revenue: ", end="")
    print(sorted_city_aggregate_on_total_revenue[0][0])
    print()
    # well... actually the most profitable should only use total revenue, cuz average revenue is just total revenue / 2 (:P)

    
    print("Monthly Revenue for Branch Location in each City")
    date_filter_function_list_by_month = list(map(create_date_filter_function_on_month, date_unique_month_values))

    # It is a list of lists filtered by city, containing two lists of records grouped by month (11 & 12)
    #[[[november records], [december records]], [[november], [december]], ....]
    city_filtered_records_by_month = list(
        list(map(lambda func: func(record), date_filter_function_list_by_month)) 
        for record in city_filtered_records
    )

    # List of lists of revenue per city by month ---> [[november revenue, december revenue], [novem...], ...]
    city_total_revenue_by_month = [
        list(map(calculate_total_revenue, city_record_month)) 
        for city_record_month in city_filtered_records_by_month
    ]
    
    for city, record in zip(city_unique_values, city_total_revenue_by_month):
        aggregate = zip(date_unique_month_values, record)
        for month, monthly_revenue in aggregate:
            print(f"{city}: ${monthly_revenue:.2f} (Month {month})")
    print()
 
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
    
    sorted_manager_aggregate_on_revenue = sorted(
        zip(manager_unique_values, manager_total_revenue), 
        key=lambda x: x[1], 
        reverse=True
    )
    print(f"Best performing manager by revenue is: {sorted_manager_aggregate_on_revenue[0][0]}")
    print()

    ''' Question 4: Customer preferred payment method and purchase type '''
    print("Analysis based on Payment Method & Purchase Type (Question 4)")
    print("-------------------------------------------------------------")

    payment_unique_values = header_to_values["Payment Method"]
    purchase_unique_values = header_to_values["Purchase Type"]

    payment_filtered_records = list(map(filter_from_dataset, header_to_unique_value_filter_func["Payment Method"]))
    purchase_filtered_records = list(map(filter_from_dataset, header_to_unique_value_filter_func["Purchase Type"]))

    print("Payment method accepted by the company: ")
    print(*payment_unique_values, sep=" | ", end="\n\n")

    print("Sales records for each payment method")
    for payment, record_list in zip(payment_unique_values, payment_filtered_records):
        print(f"{payment}: {len(record_list)} records")

    sorted_payment_aggregate = sorted(
        zip(payment_unique_values, list(map(len, payment_filtered_records))), 
        key=lambda x: x[1], 
        reverse=True
    )
    print(f"Preferred payment method by customer (most popular): {sorted_payment_aggregate[0][0]}\n")

    print("Purchase type offered by the company: ")
    print(*purchase_unique_values, sep=" | ", end="\n\n")

    print("Sales records for each purchase type")
    for purchase, record_list in zip(purchase_unique_values, purchase_filtered_records):
        print(f"{purchase}: {len(record_list)} records")
    
    sorted_purchase_aggregate = sorted(
        zip(purchase_unique_values, list(map(len, purchase_filtered_records))), 
        key=lambda x: x[1], 
        reverse=True
    )
    print(f"Preferred purchase type by customer (most popular): {sorted_purchase_aggregate[0][0]}\n")
    
    ''' Question 5: Sales period based analysis (overall revenue increase or decrease over 2 months) '''
    print("Analysis based on Sales Period (Question 5)")
    print("-------------------------------------------")

    print("Sales period (months) of the restaurant company recorded in dataset: ")
    print(*date_unique_month_values, sep=" | ", end="\n\n")

    month_filtered_records = list(map(filter_from_dataset, date_filter_function_list_by_month))
    month_total_revenue = list(map(calculate_total_revenue, month_filtered_records))
    
    print("Total revenue generated for each month")
    print_revenue_based_summary(sorted(zip(date_unique_month_values, month_total_revenue), key=lambda x: x[0]))

    overall_total_revenue = reduce(calculate_sum, month_total_revenue)
    print(f"Total Revenue Generated (Overall): ${overall_total_revenue:.2f}\n")

    print("Revenue performance for each month (difference)")

    # [(11, total revenue for the month), (12, total revenue for the month)]
    sorted_month_aggregate_on_revenue = sorted(
        zip(date_unique_month_values, month_total_revenue), 
        key=lambda x: x[0]
    )

    # -1 cuz we need to find difference between months (minimum 2)
    for i in range(len(sorted_month_aggregate_on_revenue) - 1):
        diff = sorted_month_aggregate_on_revenue[i + 1][1] - sorted_month_aggregate_on_revenue[i][1] # difference from next month to current
        percentage = (diff / sorted_month_aggregate_on_revenue[i][1]) * 100 # percentage increase/decrease based on current month
        sign = "+" if diff >= 0 else "" # sign just for display purposes
        print(f"Revenue performance from month ({sorted_month_aggregate_on_revenue[i][0]}) to month ({sorted_month_aggregate_on_revenue[i + 1][0]}): {sign}{percentage:.2f} %")
    
    print()

if __name__ == "__main__":
    main()


