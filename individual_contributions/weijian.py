import csv
from functools import reduce
import re
import sys

# === DATA HANDLING FUNCTIONS ===

def parse_CSV(path):
    """
    Parses CSV and separates data. 
    Concept: Separating functions and data 
    """
    try:
        with open(path, mode='r', encoding='utf-8-sig') as f:
            read_dictionary = csv.DictReader(f)
            # Concept: List Comprehensions  for converting to list immediately
            return (read_dictionary.fieldnames, [row for row in read_dictionary])
    except FileNotFoundError:
        print(f"Error: File {path} not found.")
        return ([], [])

def sanitise_data_input(entry: str):
    """
    Sanitises string input.
    Concept: Pure function
    """
    return " ".join(re.split(r"\s+", entry)).strip()

# === FUNCTIONAL TOOLS & HIGHER ORDER FUNCTIONS ===

def create_product_filter_function(product_name):
    """
    Creates a specific filter function.
    Concepts: 
    - Returning functions 
    - Lambdas 
    """
    # Concept: Filtering  inside a closure
    return lambda data: list(filter(lambda record: record["Product"] == product_name, data))

def calculate_sum(accumulator, value):
    return accumulator + value

def get_quantity(record):
    return float(record["Quantity"])

def get_revenue(record):
    return float(record["Price"]) * float(record["Quantity"])

def calculate_metric_total(records, mapper_func):
    """
    Generic function to calculate totals.
    Concepts:
    - Passing functions as arguments 
    - Mapping 
    - Reducing 
    """
    if not records:
        return 0.0
    # Map the specific metric (quantity or revenue) then reduce to a sum
    mapped_values = map(mapper_func, records)
    return reduce(calculate_sum, mapped_values)

# === RECURSION (CRITICAL ADDITION) ===

def recursive_find_best(items, compare_func):
    """
    Finds the best item in a list using recursion instead of max().
    Concept: Recursion 
    
    :param items: List of items to search
    :param compare_func: Lambda to determine which of two items is 'better'
    :return: The winning item
    """
    # Base case: if list has one item, it is the best
    if len(items) == 1:
        return items[0]
    
    # Recursive step: find best in the rest of the list
    rest_best = recursive_find_best(items[1:], compare_func)
    
    # Compare head of list with the best of the rest
    return compare_func(items[0], rest_best)

# === MAIN ===

def main():
    # 1. Load Data
    import os
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the main project directory
    csv_path = os.path.join(script_dir, "..", "restaurant_sales_data.csv")
    
    header, raw_data = parse_CSV(csv_path)
    
    if not raw_data:
        return

    # 2. Sanitise Data using List Comprehension (Concept )
    data = [
        {sanitise_data_input(k): sanitise_data_input(v) for k, v in record.items()} 
        for record in raw_data
    ]
    
    # 3. Get Unique Products
    unique_products = sorted(list(set(map(lambda r: r["Product"], data))))
    
    # 4. Create List of Functions (Concept )
    # We create a list of filter functions, one for each product
    filter_funcs = list(map(create_product_filter_function, unique_products))
    
    # 5. Apply Functions to Data
    # Apply each filter function to the main dataset
    grouped_data = list(map(lambda func: func(data), filter_funcs))
    
    # 6. Calculate Totals using Functional Map
    # Partial application logic for mapping
    total_quantities = list(map(lambda r: calculate_metric_total(r, get_quantity), grouped_data))
    total_revenues = list(map(lambda r: calculate_metric_total(r, get_revenue), grouped_data))
    
    # Zip into final structure: (Product, Quantity, Revenue)
    product_performance = list(zip(unique_products, total_quantities, total_revenues))

    print("=== PRODUCT CATEGORY ANALYSIS ===")
    
    # 7. Find Best Selling using RECURSION (Concept )
    # We define lambdas to compare two tuples and return the "larger" one
    
    # Find max by index 1 (Quantity)
    best_qty = recursive_find_best(
        product_performance, 
        lambda x, y: x if x[1] > y[1] else y
    )
    
    # Find max by index 2 (Revenue)
    best_rev = recursive_find_best(
        product_performance, 
        lambda x, y: x if x[2] > y[2] else y
    )

    # 8. Output Results
    print(f"\n Best Selling by QUANTITY: {best_qty[0]}")
    print(f"   Units: {best_qty[1]:.2f}")
    
    print(f"\n Best Selling by REVENUE:  {best_rev[0]}")
    print(f"   Total: ${best_rev[2]:.2f}")

    print("\nFull Breakdown:")
    for p in product_performance:
        print(f"{p[0]:15} | Qty: {p[1]:8.2f} | Rev: ${p[2]:10.2f}")




