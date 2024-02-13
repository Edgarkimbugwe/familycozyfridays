import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
# Open the Google Sheet by its name
SHEET = GSPREAD_CLIENT.open('family_cozy_fridays')
# Get the data from the sheet as a list of lists


#function to add data in the activity_scores worksheet
def add_activity(date, activity, players):
    worksheet = SHEET.get_worksheet(0)

    last_activity_id = worksheet.cell(worksheet.row_count, 1).value

    activity_id = int(last_activity_id) + 1 if last_activity_id else 1

    row_data = [activity_id, date, activity] + ['' for _ in range(len(players))]

    worksheet.append_row(row_data)


print(add_activity)

