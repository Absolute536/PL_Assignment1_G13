# for the quantity right, in my opinion err we shouldn't round it.
# because they make multiple orders into one row per day ? so it will be less accurate if we round it i feel...

import csv
from functools import reduce
import re


def create_filter_function_by_header(header):
    def create_filter_function_by_value(value):
        record_value = value

        def get_record_value():
            return record_value

        def filter_function(data):
            return filter(lambda x: x[header] == value, data)

        return (get_record_value, filter_function)

    return create_filter_function_by_value


def calculate_total_quantity(accumulator, quantity):
    return accumulator + quantity


def parse_CSV(path):
    read_dictionary = csv.DictReader(open(path))
    return (read_dictionary.fieldnames, list(read_dictionary))


def sanitise_data_input(entry: str):
    return " ".join(re.split("\s+", entry)).strip()


def main():
    header, data = parse_CSV("restaurant_sales_data.csv")
    sanitised_data = [
        {
            sanitise_data_input(key): sanitise_data_input(value)
            for key, value in record.items()
        }
        for record in data
    ]

    # Question 3:  Who is the best performing manager (in terms of revenue)
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
