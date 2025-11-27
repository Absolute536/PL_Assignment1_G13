import csv
from functools import reduce
import re


# Concept: Separating functions and data
def parse_CSV(path):
    try:
        with open(path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            return (reader.fieldnames, [row for row in reader])
    except FileNotFoundError:
        print(f"Error: File {path} not found.")
        return ([], [])


# Concept: Pure function
def sanitise_data_input(entry):
    if entry is None:
        return ""
    return " ".join(re.split(r"\s+", str(entry))).strip()


# Concept: Returning functions
def create_filter_function(column, value):
    return lambda data: list(filter(lambda row: row.get(column, "") == value, data))  # Concept: Lambdas + Filtering


# Concept: Recursion
def recursive_find_best(items, compare_func):
    if len(items) == 1:
        return items[0]
    rest_best = recursive_find_best(items[1:], compare_func)
    return compare_func(items[0], rest_best)


# Concept: Reducing
def calculate_sum(acc, val):
    return acc + val


def main():
    import os
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "restaurant_sales_data.csv") \
        if '__file__' in globals() else "restaurant_sales_data.csv"

    header, raw_data = parse_CSV(csv_path)
    if not raw_data:
        return

    # Concept: List Comprehension
    data = [
        {sanitise_data_input(k): sanitise_data_input(v) for k, v in record.items()}
        for record in raw_data
    ]

    categories = ["Payment Method", "Purchase Type"]

    for category in categories:
        print(f"\n=== CUSTOMER PREFERENCE BY {category.upper()} ===")

        # Concept: Mapping
        unique_values = sorted(list(set(map(lambda r: r.get(category, ""), data))))

        # Concept: Creating a list of functions
        filter_funcs = list(map(lambda val: create_filter_function(category, val), unique_values))

        # Concept: Passing functions as arguments
        grouped_data = list(map(lambda func: func(data), filter_funcs))

        # Concept: Mapping
        counts = list(map(len, grouped_data))

        # Concept: Reducing
        total_customers = reduce(calculate_sum, counts, 0)

        # Concept: List Comprehension
        percentages = [(val, (count / total_customers) * 100) for val, count in zip(unique_values, counts)]

        # Concept: Recursion + Lambdas
        most_preferred = recursive_find_best(percentages, lambda x, y: x if x[1] > y[1] else y)

        # Output
        print(f"\n Most Preferred: {most_preferred[0]} ({most_preferred[1]:.2f}%)\n")
        print("Full Breakdown (Quantity + Percentage):")
        
        for val, count in zip(unique_values, counts):
            pct = (count / total_customers) * 100
            print(f"{val:15} | {count:4d} customers | {pct:6.2f}%")



if __name__ == "__main__":
    main()

