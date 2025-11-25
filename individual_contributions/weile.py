# My version of the solution
# It's kinda messy cuz I deliberately used all the map(), reduce(), filter(), etc. as per the assignment requirement
# Idk if this is "functional" enough, but the answers should be correct (do double check this :P)

from functools import reduce
import re
import csv
from collections import Counter

def parse_CSV(path):
    read_dictionary = csv.DictReader(open(path))
    return (read_dictionary.fieldnames, list(read_dictionary))

def sanitise_data_input(entry: str):
    return " ".join(re.split("\s+", entry)).strip()

def calculate_sum(accumulator, value):
    return accumulator + value

def calculate_total_quantity(record):
    return reduce(calculate_sum, [float(entry["Quantity"]) for entry in record])

def calculate_total_revenue(record):
    if len(record) > 0:
        return reduce(calculate_sum, [float(entry["Quantity"]) * float(entry["Price"]) for entry in record])
    return 0

def create_product_filter_function(product_name):
    def get_filtered_list(data):
        return list(filter(lambda record: record["Product"] == product_name, data))
    return get_filtered_list

def create_city_filter_function(city):
    def get_filtered_list(data):
        return list(filter(lambda record: record["City"] == city, data))
    return get_filtered_list

def create_manager_filter_funtion(manager):
    def get_filtered_list(data):
        return list(filter(lambda record: record["Manager"] == manager, data))
    return get_filtered_list

def create_purchase_type_filter_funtion(purchase_type):
    def get_filtered_list(data):
        return list(filter(lambda record: record["Purchase Type"] == purchase_type, data))
    return get_filtered_list

def create_payment_method_filter_funtion(payment_method):
    def get_filtered_list(data):
        return list(filter(lambda record: record["Payment Method"] == payment_method, data))
    return get_filtered_list

def create_date_filter_function_on_month(month):
    def get_filtered_list(data):
        return list(filter(lambda record: int(record["Date"][3:5]) == int(month), data)) # or just compare the string?
    return get_filtered_list


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

    # dict of header -> set of unique values of the column
    header_to_values = {h: set([record[h] for record in sanitised_data]) for h in header}


    '''
    Ok, let's summarise the process from the experiment (Product)
    1. obtain unique values for the header in a list
    2. create a list of filter function for each of the unique values for that category by map() the unique values list with create_{header}_filter_function()
    3. get the filtered list of LISTS of RECORDS for each unique value for that category by applying each of the filter functions created to the sanitised_data
       the structure would be something like: [[{....}, {.....}, {.....}], [{....}, {.....}], [{....}, ...], ....]
    4. then we apply whatever function that we need to the filtered list for our desired operation/calculation
    5. for displaying the result, can use zip() on the initial unique values list and each of the resultant lists to create a list of tuples of the result, preserving the order
       note: on second thought, it's probably enought to just zip(unique values list, the desired resultant list) to print it and do it again for another resultant list
    
    Note: the ordering of the subsequent collections/list follows the initial set of unique values for the header category, and since set is unordered, we'll get a different ordering each time
          BUT
          we can still map the results by their position, since the subsequent lists are derived from the set
          just that need to zip() the set and the derived lists if we wanna do sorting to preserve the mapping correctly
    '''

    # Product based analysis
    print("Analysis based on Product")
    print("-------------------------")
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
    unique_product_values = set(record["Product"] for record in sanitised_data)

    # A list of filter_function for each of the unique product values
    product_filter_function_list = list(map(create_product_filter_function, unique_product_values))
    
    # A list of lists that contain records corresponding to each product ---> [[{.....}, {....}, {.....}], [{.....}], etc.]
    # product_filtered_records = [func(sanitised_data) for func in product_filter_function_list]
    filtered_records_on_product = list(map(lambda func: func(sanitised_data), product_filter_function_list))

    # A list containing the sum of total quantity corresponding to each product ---> [total quantity for product_1, total quantity for product_2, ... for every product type]
    # reduce_product_quantity_func = lambda record: reduce(calculate_sum, [float(entry["Quantity"]) for entry in record])
    # Note to self: this works because we call map(), so map() unpack the list of lists of records into individual list of records, which is then feed into calculate_total_quantity
    #               that does further unpacking into records
    sum_of_quantity_for_products = list(map(calculate_total_quantity, filtered_records_on_product))

    # A list containing the total revenue (price * quantity) for each product type ---> [total revenue for product_1, total revenue for product_2, ... and so on]
    # reduce_product_revenue_func = lambda record: reduce(calculate_sum, [float(entry["Quantity"]) * float(entry["Price"]) for entry in record])
    total_revenue_for_products = list(map(calculate_total_revenue, filtered_records_on_product))

    ''' This is to find out the outlier, can be an additional part '''
    unique_prices_for_each_product = list(map(lambda record: set(entry["Price"] for entry in record), filtered_records_on_product))
    prices_for_each_product = list(map(lambda record: list(entry["Price"] for entry in record), filtered_records_on_product))
    # print("Unique Prices: ", end="")
    # print(unique_prices_for_each_product) # so there are outlier for Prices in Chicken Sandwiches and Fries (so THAT'S WHY they don't match up after calculation)
    # print(prices_for_each_product)

    # price_occurrences = list(map(Counter, prices_for_each_product))
    # print(price_occurrences)
    ''' End of outlier investigation'''

    for product, sum, revenue in zip(unique_product_values, sum_of_quantity_for_products, total_revenue_for_products):
        print(product + ": " + f"{round(sum, 2):.2f} units sold " + "with $" + f"{round(revenue, 2):.2f} revenue generated")
    print()

    # Need to zip() the collection then sort, so that we preserve the ordering and consequently the identity of each collection
    # aggregate_product_result = zip(unique_product_values, sum_of_quantity_for_products, total_revenue_for_products)
    # We can't reuse the above collection to produce multiple sorted ones, cuz the first call to sorted() would exhaust the iterator for the collection already
    # making the next one return an [] empty list
    # also use sorted() instead of list.sort() for immutability
    sorted_aggregate_based_on_quantity = sorted(zip(unique_product_values, sum_of_quantity_for_products, total_revenue_for_products), key = lambda x: x[1], reverse=True)
    sorted_aggregate_based_on_revenue = sorted(zip(unique_product_values, sum_of_quantity_for_products, total_revenue_for_products), key = lambda x: x[2], reverse=True) 
    # print(sorted_aggregate_based_on_quantity)
    # print(sorted_aggregate_based_on_revenue)

    print("Top 3 best-selling products in terms of quantity sold across all citites")
    for i in range(len(sorted_aggregate_based_on_quantity) if len(sorted_aggregate_based_on_quantity) < 3 else 3):
        print("Top " + str(i + 1) + ": " + sorted_aggregate_based_on_quantity[i][0] + f" ({sorted_aggregate_based_on_quantity[i][1]:.2f} units sold)")
    print()

    print("Top 3 best-selling products in terms of total revenue generated across all cities")
    for i in range(len(sorted_aggregate_based_on_revenue) if len(sorted_aggregate_based_on_revenue) < 3 else 3):
        print("Top " + str(i + 1) + ": " + sorted_aggregate_based_on_revenue[i][0] + f" (${sorted_aggregate_based_on_revenue[i][2]:.2f} revenue)")
    print()


    ''' Question 2: Which location is the most profitable in terms of revenue & their monthly average revenue '''
    print("Analysis based on Branch Location (City)")
    print("----------------------------------------")
    
    # First we need to find out the sales data contain records for how many months (it's 2 duh, but let's try to find it programmitically)
    unique_date_values = set(record["Date"] for record in sanitised_data)
    unique_month_values_from_date = set(date[3:5] for date in unique_date_values) # the 3rd and 4th index contains the month (kinda fragile but whatever~)
    number_of_months_in_dataset = len(unique_month_values_from_date)
    
    unique_city_values = set(record["City"] for record in sanitised_data)
    city_filter_function_list = list(map(create_city_filter_function, unique_city_values))
    filtered_records_on_city = list(map(lambda func: func(sanitised_data), city_filter_function_list))

    total_revenue_for_cities = list(map(calculate_total_revenue, filtered_records_on_city))
    average_monthly_revenue_for_cities = list(map(lambda revenue: revenue / number_of_months_in_dataset, list(map(calculate_total_revenue, filtered_records_on_city))))

    print("Branch locations (city) of the restaurant company: ")
    print(*unique_city_values, sep=" | ", end="\n\n")
    for city, total_revenue, average_monthly_revenue in zip(unique_city_values, total_revenue_for_cities, average_monthly_revenue_for_cities):
        print(f"{city}:  ${total_revenue:.2f} total revenue with ${average_monthly_revenue:.2f} average monthly revenue")

    sorted_aggregate_based_on_total_revenue_for_cities = sorted(zip(unique_city_values, total_revenue_for_cities), key=lambda x: x[1], reverse=True)

    print("The most profitable branch (city) for the restaurant company in terms of revenue: ", end="")
    print(sorted_aggregate_based_on_total_revenue_for_cities[0][0])
    print()

    # print("The most profitable branch (city) for the restaurant company in terms of average monthly revenue: ", end="")
    # print(sorted_aggregate_based_on_average_monthly_revenue_for_cities[0][0])
    # well... actually the most profitable should only use total revenue, cuz average revenue is just total revenue / 2 (:P)

    
    print("Monthly Revenue for Branch Location in each City")
    
    date_filter_function_list_by_month = list(map(create_date_filter_function_on_month, unique_month_values_from_date))
    
    # Successful
    # It is a list of lists filtered by city, containing two lists of records grouped by month (11 & 12)
    #[[[november records], [december records]], [[november], [december]], ....]
    filtered_records_on_city_by_month = list(list(map(lambda func: func(record), date_filter_function_list_by_month)) for record in filtered_records_on_city)
    # List of lists of revenue per city by month ---> [[november revenue, december revenue], [novem...], ...]
    total_revenue_on_city_by_month = [list(map(calculate_total_revenue, city_record_month)) for city_record_month in filtered_records_on_city_by_month]
    
    for city, record in zip(unique_city_values, total_revenue_on_city_by_month):
        aggregate = zip(unique_month_values_from_date, record)
        for month, monthly_revenue in aggregate:
            print(f"{city}: ${monthly_revenue:.2f} (Month {month})")
    print()
 
    ''' Question 3: Who is the best performing manager in terms of revenue '''
    print("Analysis based on Manager")
    print("-------------------------")

    unique_manager_values = set(record["Manager"] for record in sanitised_data)
    manager_filter_function_list = list(map(create_manager_filter_funtion, unique_manager_values))
    filtered_records_by_manager = list(map(lambda func: func(sanitised_data), manager_filter_function_list))
    total_revenue_for_manager = list(map(calculate_total_revenue, filtered_records_by_manager))

    print("Managers employed by the restaurant company: ")
    print(*unique_manager_values, sep=" | ", end="\n\n")
    for manager, revenue in zip(unique_manager_values, total_revenue_for_manager):
        print(f"{manager}: ${revenue:.2f} generated")
    
    sorted_aggregate_on_revenue_by_manager = sorted(zip(unique_manager_values, total_revenue_for_manager), key=lambda x: x[1], reverse=True)
    print(f"Best performing manager by revenue is: {sorted_aggregate_on_revenue_by_manager[0][0]}")
    print()

    ''' Question 4: Customer preferred payment method and purchase type '''
    print("Analysis based on Payment Method & Purchase Type")
    print("------------------------------------------------")

    unique_payment_method_values = set(record["Payment Method"] for record in sanitised_data)
    unique_purchase_type_values = set(record["Purchase Type"] for record in sanitised_data)

    payment_method_filter_function_list = list(map(create_payment_method_filter_funtion, unique_payment_method_values))
    purchase_type_filter_function_list = list(map(create_purchase_type_filter_funtion, unique_purchase_type_values))

    filtered_records_by_payment_method = list(map(lambda func: func(sanitised_data), payment_method_filter_function_list))
    filtered_records_by_purchase_type = list(map(lambda func: func(sanitised_data), purchase_type_filter_function_list))

    print("Payment method accepted by the company: ")
    print(*unique_payment_method_values, sep=" | ", end="\n\n")
    for payment, record_list in zip(unique_payment_method_values, filtered_records_by_payment_method):
        print(f"{payment}: {len(record_list)} records")

    sorted_aggregate_based_on_payment_method = sorted(zip(unique_payment_method_values, list(map(len, filtered_records_by_payment_method))), key=lambda x: x[1], reverse=True)
    print(f"Preferred payment method by customer (most popular): {sorted_aggregate_based_on_payment_method[0][0]}\n")

    print("Purchase type offered by the company: ")
    print(*unique_purchase_type_values, sep=" | ", end="\n\n")
    for purchase, record_list in zip(unique_purchase_type_values, filtered_records_by_purchase_type):
        print(f"{purchase}: {len(record_list)} records")
    
    sorted_aggregate_based_on_purchase_type = sorted(zip(unique_purchase_type_values, list(map(len, filtered_records_by_purchase_type))), key=lambda x: x[1], reverse=True)
    print(f"Preferred purchase type by customer (most popular): {sorted_aggregate_based_on_purchase_type[0][0]}\n")
    
    ''' Question 5: Sales period based analysis (overall revenue increase or decrease over 2 months) '''
    print("Analysis based on Sales Period")
    print("------------------------------")

    print("Sales period (months) of the restaurant company recorded in dataset: ")
    print(*unique_month_values_from_date, sep=" | ", end="\n\n")

    filtered_records_by_month = list(map(lambda func: func(sanitised_data), date_filter_function_list_by_month))
    total_revenue_by_month = list(map(calculate_total_revenue, filtered_records_by_month))
    
    for month, revenue in sorted(zip(unique_month_values_from_date, total_revenue_by_month), key=lambda x: x[0]):
        print(f"Revenue in month ({month}): ${revenue:.2f}")

    overall_total_revenue = reduce(calculate_sum, total_revenue_by_month)
    print(f"Total Revenue Generated (Overall): ${overall_total_revenue:.2f}\n")

    print("Revenue performance for each month (difference)")
    sorted_aggregate_based_on_revenue_by_month = sorted(zip(unique_month_values_from_date, total_revenue_by_month), key=lambda x: x[0])
    for i in range(len(sorted_aggregate_based_on_revenue_by_month) - 1):
        diff = sorted_aggregate_based_on_revenue_by_month[i + 1][1] - sorted_aggregate_based_on_revenue_by_month[i][1]
        percentage = (diff / sorted_aggregate_based_on_revenue_by_month[i][1]) * 100
        sign = "+" if diff >= 0 else ""
        print(f"Revenue performance from month ({sorted_aggregate_based_on_revenue_by_month[i][0]}) to month ({sorted_aggregate_based_on_revenue_by_month[i + 1][0]}): {sign}{percentage:.2f} %")
    
    print()


if __name__ == "__main__":
    main()


