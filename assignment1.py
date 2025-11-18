import csv
import os
from functools import reduce
from functools import partial
import re
# maybe needed if we wanna partially apply a function with > 1 arguments, or we can just structure the function properly

# Establish the initial data (the list of dictionary containing the dataset)
def parse_CSV(path):
    read_dictionary = csv.DictReader(open(path))
    return (read_dictionary.fieldnames, list(read_dictionary))

def get_specific_header(key):
    def get_header(header):
        return [element for element in header if element == key]
    return get_header

def create_filter_function(header):
    def filter_function_by(value):
        def filter_function(data):
            # return [row[header] for row in data if row[header] == value]
            return filter(lambda x: x[header] == value, data)
        return filter_function
    return filter_function_by

def create_filter_function_by_header(header):
    def create_filter_function_by_value(value):
        def filter_function(data):
            return filter(lambda x: x[header] == value, data)
        return filter_function
    return create_filter_function_by_value

def sanitise_data_input(entry: str):
    return " ".join(re.split("\s+", entry)).strip()
    

def main():
    header, data = parse_CSV("restaurant_sales_data.csv")

    # Sanitise the csv data, by removing unwanted whitespaces in both the key and value of each dictionary in the dataset
    # Because some rows contain entries with leading + trailing whitespaces, and also extra whitespaces in between words
    # We can find + replace those manually. But hey, since this works, we don't need to (luckily)

    # Method 1
    # sanitised_data = [{" ".join(re.split("\s+", key)).strip(): " ".join(re.split("\s+", value)).strip() for key, value in record.items()} for record in data]

    # Method 2
    # sanitised_data = [dict(map(lambda item: (sanitise_data_input(item[0]), sanitise_data_input(item[1])), record.items())) for record in data]
    # note items() on dict give a list of tuple of key-value pair like [("Product", "Burgers"), ("Manager", "Name")], sth like that
    # so by using map on record.items(), we apply the sanitise function on each of those tuple
    # THEN, reconstruct the dictionary record through the map object

    # Method 3 (I think this is more readable)
    sanitised_data = [{sanitise_data_input(key): sanitise_data_input(value) for key, value in record.items()} for record in data]

    # print(sanitised_data)
    # print(data)
    
    # for header_value in header
    # use each header_value to each record in data like data[header_value]
    # then create a dict of header_value: set(data[header_value])
    # so that we get a dict of header_value -> unique values in the data for each header
    header_values = {h: set([record[h] for record in sanitised_data]) for h in header}
    
    # for k, v in header_values.items():
    #     print(k + ": " + str(v))

    # sanitized_header_values = {key: " ".join(re.split("\s+", str(value))).strip() for key, value in header_values.items()}
    # sanitized_header_values = {key: value for key, value in header_values.items()}
    # print(sanitized_header_values)

    # dict of product -> price
    product_price_dict = {record["Product"]: record["Price"] for record in sanitised_data}
    print(product_price_dict)
    

    # list of product_category
    product_category_set = set([product["Product"] for product in sanitised_data])
    print(product_category_set)

    # a series of filtered list based on product?
    # filtered_category_lists = []
    # for h in header:
    #     create_filter_function(h)
    #     filtered_category_lists.append(h)
    
    # for func in filtered_category_lists:
    #     p_func = partial(func, "Burger")
    #     p_func(data)

    filter_by_product = create_filter_function("Product")
    filter_by_burger = filter_by_product("Burgers")
    # print(list(filter_by_burger(data)))

    # filter_func_by_product = [create_filter_function("Product")(row) for row in product_category_set]
    # for product_func in filter_func_by_product:
    #     category_data = list(product_func(data))
    #     for d in category_data:
    #         print(d)

    # burger_sales_record = [x(data) for x in filter_func_by_product]


    # print(list(filter(lambda row: row["Product"] == "Burger")))
    # name = "   Remy   Monet  "
    # sanitize_name = " ".join(re.split("\s+", name)).strip()
    # print(sanitize_name)
    # print(len(sanitize_name))

    # testDict = dict({"   key1": "   value   1", "key2    ": "value      2"})
    # print(dict(map(lambda item: (sanitise_data_input(item[0]), sanitise_data_input(item[1])), testDict.items())))



if (__name__ == "__main__"):
    main()
