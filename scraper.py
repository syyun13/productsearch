import csv
from selenium import webdriver
from bs4 import BeautifulSoup

def search_filter(x):
    filters = {
        "1": "relevanceblender",
        "2": "price-asc-rank",
        "3": "price-desc-rank",
        "4": "date-desc-rank",
        "5": "review-rank"
    }
    return filters[x]

def get_url(keyword, s_filter):
    url_base = "https://www.amazon.com/s?k={}&ref=nb_sb_noss_1"
    keyword = keyword.replace(" ", "+")
    return url_base.format(keyword) + "&s=" + s_filter + "&page={}"

def get_data(product, include_zero):
    product_name = product.h2.a.text.strip()
    product_url = "https:://www.amazon.com" + product.h2.a.get("href")

    # Handle error for some products without price and ratings
    try:
        product_price = product.find("span", "a-price").find("span", "a-offscreen").text
        product_price = float(product_price[1:].replace(",", ""))
    except AttributeError:
        return
    try:
        product_rate = float(product.i.text.split()[0])
    except AttributeError:
        product_rate = 0

    # Do not include products with 0 ratings if user chose the option
    if include_zero.lower() == "n" and product_rate == 0:
        return
    else:
        return (product_name, product_price, product_rate, product_url)

def get_bestrate(list):
    # Find product with highest rating
    max_rating = 0
    max_item = []
    for item in list:
        if item[2] > max_rating:
            max_rating = item[2]
            max_item = item
    return max_item

def get_cheapest(list):
    # Find product with lowest price
    min_price = -100
    min_item = []
    for item in list:
        if min_price == -100:
            min_price = item[1]
            min_item = item
        else:
            if min_price > item[1]:
                min_price = item[1]
                min_item = item
    return min_item

def main():
    driver = webdriver.Chrome()
    data_list = []

    # What to search on Amazon
    keyword = input("Enter keyword: ")

    # Select search filters
    print("\nHow would you like to sort your results?")
    print("1. Featured")
    print("2. Price: Low to High")
    print("3. Price: High to Low")
    print("4. Newest Arrivals")
    print("5. Average Customer Reviews\n")
    n = input("Please type in only the number: ")

    # Repeat until the user types a correct input
    while(not n.isdigit() or int(n) < 1 or int(n) > 5):
        print("That option is not available. Please choose between 1 ~ 5.")
        print("How would you like to sort your results?")
        n = input("Please type in only the number: ")

    url = get_url(keyword, search_filter(n))

    include_zero = input("Include products with 0 rating?(y/n): ")

    # Repeat until the user types a correct input
    while(include_zero not in ["y", "Y", "n", "N"]):
        print("That option is not available.")
        include_zero = input("Include products with 0 rates?(y/n): ")

    print("\n#####  Fetching search results for " + keyword + "  #####\n")

    for page in range(1,11):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        search_results = soup.find_all("div", {"data-component-type": "s-search-result"})
        for product in search_results:
            product_data = get_data(product, include_zero)
            if product_data:
                data_list.append(product_data)
    
    driver.close()

    bestrated_item = get_bestrate(data_list)

    print(">>> Best Rated Item from your search results")
    print("Name: " + bestrated_item[0])
    print("Price: $" + str(bestrated_item[1]))
    print("Rating: " + str(bestrated_item[2]) + " out of 5.0")

    cheapest_item = get_cheapest(data_list)

    print("\n>>> Cheapest Item from your search results")
    print("Name: " + cheapest_item[0])
    print("Price: $" + str(cheapest_item[1]))
    print("Rating: " + str(bestrated_item[2]) + " out of 5.0")

    print("\nAll of your search results will be saved to a csv file.")
    filename = input("Filename: ")

    # Save as csv file
    with open(filename + ".csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Price", "Rating", "URL"])
        writer.writerows(data_list)

    print("\n####  " + filename + ".csv was successfully saved  ####\n")

    # End of program

main()