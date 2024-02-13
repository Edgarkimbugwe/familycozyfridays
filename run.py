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


# function to add data in the activity_scores worksheet
def add_activity(date, activity, players):
    # Get the Activity_scores worksheet
    worksheet = SHEET.get_worksheet(0)

    # Get the last activity ID from the worksheet
    last_activity_id = worksheet.cell(worksheet.row_count, 1).value

    # generate unique ID for the activity
    activity_id = int(last_activity_id) + 1 if last_activity_id else 1

    # Prepare data to append to the worksheet
    row_data = [activity_id, date, activity] + ['' for _ in range(len(players))]
    
    # Append the row to the worksheet
    worksheet.append_row(row_data)


# function to update scores for a specific activity
def update_scores(activity_id, players, scores):
    # Get the Activity_scores worksheet
    worksheet = SHEET.get_worksheet(0)

    try:
        # Find the column index corresponding to the player
        player_column = worksheet.find(player).col

        # Update the score for the players in the specified activity row
        worksheet.update_cell(activity_id + 1, player_column, score)
    except gspread.exceptions.CellNotFound:
        # If player not found, add a new column for the player
        worksheet.add_cols(1)
        player_column = worksheet.col_count
        worksheet.update_cell(1, player_column, player)
        worksheet.update_cell(activity_id + 1, player_column, score)

