import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

start_time = time.time()


# Start a session
session = requests.Session()

url = "https://etenders.gov.in/eprocure/app?page=FrontEndTendersByOrganisation&service=page"

# Make initial request to get cookies
response = session.get(url)

# Get the cookies from the response
cookies = session.cookies.get_dict()

# Add the cookies to the headers
headers = {
    'Cookie': '; '.join([f"{name}={value}" for name, value in cookies.items()])
}

# Make a new request with the headers
response = session.get(url, headers=headers)

html_content = response.content

soup = BeautifulSoup(html_content, 'html.parser')
table = soup.find('table', {'id': 'table'})

tender_data = []
for row in table.find_all('tr')[1:-1]:
    columns = row.find_all('td')
    if len(columns) == 1:
        continue
    elif len(columns) >= 2:
        try:
            org_name = columns[1].text.strip()
            tender_count = int(columns[2].text.strip())
        except ValueError:
            print("Unable to convert tender count to integer")
            continue
    else:
        print("Invalid columns list length")
        continue

    for i in range(tender_count):
        tender_index = 2+i
        if tender_index >= len(columns):
            continue
        tender_row = columns[tender_index].find('a')
        if tender_row is None:
            continue
        tender_url = 'https://etenders.gov.in' + tender_row['href']

        # Make a new request for each tender with the headers
        tender_response = session.get(tender_url, headers=headers)

        tender_soup = BeautifulSoup(tender_response.content, 'html.parser')

        table_tender = tender_soup.find('table', {'id': 'table'})

        detail_tender_data = []
        for row_tender in table_tender.find_all('tr')[1:-1]:
            columns_tender = row_tender.find_all('td')
           
            SNo = columns_tender[0].text.strip()
            ePublishedDate = columns_tender[1].text.strip()
            ClosingDate = columns_tender[2].text.strip()
            OpeningDate = columns_tender[3].text.strip()
            TitleAndRefNoTenderID = columns_tender[4].text.strip()
            OrganisationChain = columns_tender[5].text.strip()

            tender_data.append([SNo, ePublishedDate, ClosingDate, OpeningDate, TitleAndRefNoTenderID, OrganisationChain])

df = pd.DataFrame(tender_data, columns=['S.No', 'e-Published Date', 'Closing Date', 'Opening Date', 'Title and Ref.No./Tender ID', 'Organisation Chain'])
df.to_csv('tenders.csv', index=False)

end_time = time.time()
elapsed_time = end_time - start_time

if elapsed_time < 60:
    print(f"Elapsed time: {round(elapsed_time, 2)} seconds")
elif elapsed_time < 3600:
    print(f"Elapsed time: {round(elapsed_time/60, 2)} minutes")
else:
    print(f"Elapsed time: {round(elapsed_time/3600, 2)} hours")