# FLOW token staking rewards processing
**Get staking rewards for an account for the previous year and add token price to each reward date**

> [!IMPORTANT]  
> Use at own risk - check the generated report is aligned with your records!

The token rewards are downloaded using [get_simple_v1_rewards find API](https://api.find.xyz/swagger/index.html#/Simple/get_simple_v1_rewards)
                        
File with FLOW token historical prices can be downloaded from [coinmarketcap.com](https://coinmarketcap.com/currencies/flow/historical-data/)
> make sure to select correct currency before downloading the file.

## How to use
> [!NOTE]
> This program requires python to be installed.
1) clone repo
2) Initialize python virtual environment
```
python3 -m venv ./venv
source ./venv/bin/activate
```
3) install required packages
```
pip3 install -r requirements.txt
```
5) get & save the token prices file
6) run:

```
python3 flow_token_staking_rewards_processing.py -a ACCOUNT_NUMBER -p Flow_2024-01-01-2024-12-31_historical_data_coinmarketcap_CAD.csv
```

**Example `staking_rewards_exported.csv` output CSV file:**

|Date|Staking Reward|Closing Token Price (CAD)|
|----|--------------|-------------------------|
|2024-10-02|3.9|0.7166169252|
|2024-09-25|3.8|0.8098495376|
|2024-09-18|3.7|0.7429451951|
|2024-09-11|3.6|0.7425934153|
|.|||
|.|||
|.|||
