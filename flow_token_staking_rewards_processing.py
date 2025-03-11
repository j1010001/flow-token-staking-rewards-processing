import json, getopt, sys, csv, requests
from datetime import datetime, timedelta

def process_arguments():
    
    # Initialize variables before try block
    input_rewards_file = None
    input_prices_file = None
    
    # Remove 1st argument from the
    # list of command line arguments
    argumentList = sys.argv[1:]

    # Options. when using getopt, you need to specify whether an option requires a value
    #  by adding a colon (:) after the option letter in the options string.
    options = "ha:r:p:"
    
    # Long options
    long_options = ["Help", "Account-address=", "Input-rewards=", "Input-prices="]

    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        # checking each argument
        for currentArgument, currentValue in arguments:
    
            if currentArgument in ("-h", "--Help"):
                print ("Process flow token rewards JSON file and merge with token prices CSV file, using CLOSE price for the day.\n"
                       "The token rewards are downloaded using find API\n"
                        "https://api.find.xyz/swagger/index.html#/Simple/get_simple_v1_rewards\n"
                        "--------------------------------\n"
                        "HTTP request example command:\n"
                       "curl -X 'GET' 'https://yolo-shy-dew.flow-mainnet.quiknode.pro/262cd027471e9ff80f8de60b5e0adf23524b7352/addon/906/simple/v1/rewards?from=2024-01-01&to=2024-12-31&user=0xACCOUNT_ADDRESS' \
  -H 'accept: application/json' > flow_rewards_tax_2025_0xACCOUNT_ADDRESS.json\n"
                        "--------------------------------\n"
                       "prices file needs to be downloaded from coinmarketcap.com\n"
                       "https://coinmarketcap.com/currencies/flow/historical-data/\n"
                       "make sure to select correct currency before downloading the file!\n"
                       "--------------------------------\n"
                       "usage: python process.py -r <rewards_file> -p <prices_file>")   

            elif currentArgument in ("-a", "--Account-address"):
                #query the data from the API directly
                account_address = currentValue
                print("Account address: %s" % currentValue)
                
            elif currentArgument in ("-r", "--Input-rewards"):
                input_rewards_file = currentValue
                #print("Debug - Argument:", currentArgument)
                #print("Debug - Value:", currentValue)
                print("JSON input rewards file: %s" % currentValue)
                
            elif currentArgument in ("-p", "--Input-prices"):
                input_prices_file = currentValue;
                print (("CSV input prices file: % s") % currentValue)

                
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

    return account_address, input_rewards_file, input_prices_file


def fetch_rewards_from_api(account_address):
    """
    Fetch rewards data from the Find API for a given account address.
    Returns the JSON response data.
    """
    # Get the current year's date range
    previous_year = datetime.now().year -1
    start_date = f"{previous_year}-01-01"
    end_date = f"{previous_year}-12-31"
    
    url = "https://yolo-shy-dew.flow-mainnet.quiknode.pro/262cd027471e9ff80f8de60b5e0adf23524b7352/addon/906/simple/v1/rewards"
    params = {
        "from": start_date,
        "to": end_date,
        "user": account_address
    }
    headers = {
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        #DEBUG
        print("Request URL:", response.url)  # Add this to debug the final URL
        print("Response status:", response.status_code)
        print("response.json():", response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching rewards data: {e}")
        sys.exit(1)

def process_rewards_data(rewards_data):
    """
    Process the rewards JSON data and return a dictionary of dates and their corresponding staking rewards.
    If there are multiple staking rewards in a same day (staking for multiple nodes), the rewards are aggregated.
    """
    aggregated_rewards = {}

    rewards = rewards_data["delegation_rewards"] #dictionary

    # filtered out only the fields I need
    filtered_rewards = []
    for x in rewards:
        #DEBUG
        #print(x["timestamp"], " ", x["amount"])

        date = x["timestamp"][:10] #only keep first 10 characters from the timestamp
        #print(date)
        filtered_rewards.append(date + str(x["amount"]))
        
        if aggregated_rewards.get(date) == None:
            aggregated_rewards[date] = x["amount"]
            #print("result:", aggregarted_rewards[x["timestamp"]])
            #print("result:", aggregarted_rewards[date])
        else:
            print("timestamp already found")
            #print("result current:", aggregarted_rewards[x["timestamp"]])
            aggregated_rewards[date] = aggregated_rewards[date] + x["amount"]
            #print("result new:", aggregarted_rewards[x["timestamp"]])

    return aggregated_rewards
    
def process_rewards_file(input_rewards_file):
    """
    Process the rewards JSON file and return a dictionary of dates and their corresponding staking rewards.
    If there are multiple staking rewards in a same day (staking for multiple nodes), the rewards are aggregated.
    """
    aggregated_rewards = {}
    with open(input_rewards_file, 'r') as f:
        data = json.load(f)
            
    return process_rewards_data(data)

def process_prices_file(input_prices_file):
    """
    Process the prices CSV file and return a dictionary of dates and their corresponding prices, using CLOSE price for the day.
    Returns None if no file is specified.
    """
    
    print("Info: Input prices file specified.")
    # create a dictionary of prices
    # csv format: timeOpen;timeClose;timeHigh;timeLow;name;open;high;low;close;volume;marketCap;timestamp
    prices = {}
    with open(input_prices_file, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        next(reader)  # Skip the header row
        for row in reader:
            # truncate the date to first 10 characters
            date = row[0][:10]
            # using close price for the day, which is the 9th column
            price = row[8]
            prices[date] = price
    
    # DEBUG : print the prices - each entry on a new line
    #for date, price in prices.items():
        #print(f"{date}: {price}")
    
    return prices

def merge_rewards_and_prices(aggregated_rewards, prices):
    """
    Merge rewards and prices data into a single dictionary.
    Each entry contains the reward amount and corresponding token price for that date.
    Only includes dates that exist in the rewards dictionary.
    """
    merged_data = {}

    for date in aggregated_rewards.keys():  # Only iterate through dates in aggregated_rewards
        reward = aggregated_rewards[date]
        if prices is not None:
            price = prices.get(date, 0)  # Default to 0 if no price exists for this date
        else:
            price = "NA"
        merged_data[date] = {'reward': reward, 'price': price}

    # Example of how to access the data:
    for date, data in merged_data.items():
        print(f"Date: {date}, Reward: {data['reward']}, Price: {data['price']}")

    return merged_data

"""
########################################################
Main program
########################################################
"""
account_address, rewards_file, prices_file = process_arguments()

if account_address is not None:
    print("Fetching rewards data from the API...")
    rewards_data = fetch_rewards_from_api(account_address)
    aggregated_rewards = process_rewards_data(rewards_data)
else:
    if rewards_file is None:
        print("Error: No account address or input rewards file specified."
        " Use -a or --Account-address to specify account address."
        "or use -i or --Input-rewards to specify the rewards file.")
        sys.exit(1)
    else:
        print("Reading rewards data from the file: %s" % rewards_file)
    aggregated_rewards = process_rewards_file(rewards_file)

if prices_file is None:
    print("Info: No input prices file specified, continuing without token prices."
          "Use -p or --Input-prices to specify the file."
          "you can get the file from: https://coinmarketcap.com/currencies/flow/historical-data/"
          "make sure to select correct currency before downloading the file!")
    prices = None
else:
    prices = process_prices_file(prices_file)
    #merge the rewards and prices dictionaries
    print("Merging rewards and prices...")
    
merged_data = merge_rewards_and_prices(aggregated_rewards, prices)

#write the data to a CSV file
with open('staking_rewards_exported.csv','w') as f:
    w = csv.writer(f)
    # Write header row first
    w.writerow(['Date', 'Staking Reward', 'Closing Token Price'])
    # Write data rows
    w.writerows((key, value['reward'], value['price']) for key, value in merged_data.items())