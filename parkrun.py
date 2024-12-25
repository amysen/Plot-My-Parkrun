import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from getpass import getpass  # For secure password input

# Prompt for Parkrun ID and password
parkrun_id = input("Enter your Parkrun ID (numbers only): ")  # Parkrun ID instead of email
password = getpass("Enter your password: ")  # Secure password input

# Start a session
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

# Log in
login_url = "https://www.parkrun.com/signin/"
payload = {"username": parkrun_id, "password": password}
response = session.post(login_url, data=payload, headers=headers)

if response.status_code != 200:
    print("Failed to log in. Check your credentials.")
    exit()

# Access the results page
results_url = f"https://www.parkrun.org.uk/parkrunner/{parkrun_id}/all/"
response = session.get(results_url, headers=headers)

if response.status_code != 200:
    print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
    exit()

# Parse the page
soup = BeautifulSoup(response.text, "html.parser")

# Locate all tables on the page
tables = soup.find_all("table")

# Check if there are at least three tables on the page
if len(tables) < 3:
    print(f"Less than 3 tables found on the page. Found {len(tables)} tables.")
    exit()

# Select the 3rd table 'All Results' (index 2)
table = tables[2]

# Check if the table was found
if not table:
    print("No table associated with the 'All Results' caption found on the page.")
    exit()

# Extract table rows
rows = table.find("tbody").find_all("tr")

# Parse the data from rows
data = []
for row in rows:
    columns = row.find_all("td")
    event = columns[0].text.strip()  # 1st column: Event e.g Mile End parkrun
    run_date = columns[1].text.strip()  # 2nd column: Run Date e.g. 25/12/2024
    run_number = columns[2].text.strip() # 3rd column: Run Number e.g. 602
    pos = columns[3].text.strip() # 4th column: Overall Position e.g. 50
    run_time = columns[4].text.strip()  # 5th column: Time e.g. 30:02 (mins:seconds)
    age_grade = columns[5].text.strip() # 6th column: Age Grade e.g. 46.79%
    pb = columns[6].text.strip() # 7th column: PB status e.g. PB or NULL
    data.append((event, run_date, run_number, pos, run_time, age_grade, pb))

# Create a DataFrame
df = pd.DataFrame(data, columns=["Event", "Run Date", "Run Number", "Position", "Time", "Age Grade", "PB"])
print(df)

# Convert 'Run Date' to datetime and 'Time' to seconds
df['Run Date'] = pd.to_datetime(df['Run Date'], format='%d/%m/%Y')
df['Time'] = df['Time'].apply(lambda x: sum(int(i) * 60 ** (1 - idx) for idx, i in enumerate(x.split(':'))))
df['Time'] = df['Time'] / 60  # Convert seconds to minutes

# Sort by 'Run Date'
df = df.sort_values(by='Run Date')

# Save to CSV
# df.to_csv("parkrun_results.csv", index=False)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(df['Run Date'], df['Time'], marker='o', linestyle='-', color='b', label='Time Progression')
plt.title('Time Progression Over Runs')
plt.xlabel('Run Date')
plt.ylabel('Time (minutes)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

# Display the plot
plt.show()
