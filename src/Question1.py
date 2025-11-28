import csv
from functools import reduce
import re

# === Helper Functions ===

def load_csv_file(filename):
    """ Reads the CSV file directly. """
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        # Return headers and data list directly
        return reader.fieldnames, list(reader)

def clean_text(text):
    """ Removes extra spaces from strings. """
    return " ".join(re.split(r"\s+", text)).strip()

def get_product_filter(prod_name):
    """ Returns a function that filters data for a specific product name. """
    # This closure 'remembers' the product name
    return lambda data_list: list(filter(lambda x: x["Product"] == prod_name, data_list))

def get_total(records, value_func):
    """ Calculates sum of a specific field using map and reduce. """
    if not records:
        return 0.0
    # Map the records to values, then reduce to a sum
    values = map(value_func, records)
    return reduce(lambda acc, x: acc + x, values)

def find_max_recursive(data_list, key_func):
    """
    Finds the item with the highest value recursively.
    """
    # Base case: if only one item is left, it's the max
    if len(data_list) == 1:
        return data_list[0]
    
    # Recursive step: find max of the rest of the list
    rest_max = find_max_recursive(data_list[1:], key_func)
    current = data_list[0]
    
    # Compare current item vs the max of the remaining items
    if key_func(current) > key_func(rest_max):
        return current
    else:
        return rest_max

# === Main Execution ===

def main():
    # 1. Load Data
    # Separating function (load_csv_file) from data
    headers, raw_rows = load_csv_file("restaurant_sales_data.csv")
    
    if not raw_rows:
        return

    # 2. Clean Data
    # Using list comprehension to clean every value in the dictionary
    clean_rows = [
        {clean_text(k): clean_text(v) for k, v in row.items()} 
        for row in raw_rows
    ]
    
    # 3. Get List of Unique Products
    products = sorted(list(set(map(lambda x: x["Product"], clean_rows))))
    
    print(f"--- Restaurant Sales Analysis ---")
    print(f"Processing {len(products)} unique product categories...\n")
    
    # 4. Create Filter Functions
    # Making a list of functions (one for each product)
    filters = list(map(get_product_filter, products))
    
    # 5. Apply Filters
    # Map the filter functions to the data to get groups
    grouped_data = list(map(lambda f: f(clean_rows), filters))
    
    # 6. Calculate Totals
    # Define simple lambdas to extract the numbers we need
    get_qty = lambda r: float(r["Quantity"])
    get_rev = lambda r: float(r["Price"]) * float(r["Quantity"])
    
    # Map our calculation function across the grouped data
    total_qtys = list(map(lambda rows: get_total(rows, get_qty), grouped_data))
    total_revs = list(map(lambda rows: get_total(rows, get_rev), grouped_data))
    
    # Combine results into tuples: (Product, Quantity, Revenue)
    results = list(zip(products, total_qtys, total_revs))
    
    # 7. Find Best Sellers (Using Recursion)
    # We pass a lambda key to tell the function what value to compare
    
    # Index 1 is Quantity
    best_qty_item = find_max_recursive(results, lambda x: x[1])
    
    # Index 2 is Revenue
    best_rev_item = find_max_recursive(results, lambda x: x[2])
    
    # 8. Display Results
    print(" Top Seller by Quantity")
    print(f"   Product: {best_qty_item[0]}")
    print(f"   Units:   {best_qty_item[1]:.2f}")
    
    print("\n Top Seller by Revenue")
    print(f"   Product: {best_rev_item[0]}")
    print(f"   Revenue: ${best_rev_item[2]:.2f}")
    
    print("\n Detailed Breakdown:")
    print("-" * 45)
    for p, q, r in results:
        print(f"{p:<20} | Qty: {q:>8.2f} | Rev: ${r:>10.2f}")
    
    # For outlier in Products' Prices
    print("\nProducts' Unique Prices")
    print(products)
    unique_prices = list(map(lambda record: set((entry["Price"]) for entry in record), grouped_data))
    print(unique_prices)

if __name__ == "__main__":
    main()