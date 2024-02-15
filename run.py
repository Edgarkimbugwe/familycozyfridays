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


def add_activity(date, activity, players):
    worksheet = SHEET.get_worksheet(0)

    # Find the last non-empty row in the first column
    values_list = worksheet.col_values(1)
    last_activity_id = max([int(val) for val in values_list[1:] if val]) if values_list else 0
    activity_id = last_activity_id + 1

    row_data = [activity_id, date, activity]

    existing_headers = worksheet.row_values(1)

    for player in players:
        player_lower = player.strip().lower()
        if player_lower not in map(str.lower, existing_headers):
            existing_headers.append(player.strip())

    # Update the headers row with the updated list of players
    header_range = f'A1:{chr(ord("A") + len(existing_headers) - 1)}1'
    header_cells = worksheet.range(header_range)
    for i, header in enumerate(existing_headers):
        header_cells[i].value = header
    worksheet.update_cells(header_cells)

    worksheet.append_row(row_data)


# Function to update scores for a specific activity
def update_scores(activity_id, player, score):
    # Get the Activity_scores worksheet
    worksheet = SHEET.get_worksheet(0)

    # Get the list of player names from the first row of the worksheet
    players = worksheet.row_values(1)

    # Remove leading and trailing spaces from player names
    players_cleaned = [p.strip().lower() for p in players]

    if player.strip().lower() not in players_cleaned:
        print(f"'{player}' is not registered as a player. Please add the name as a player first.")
        return

    try:
        # Find the column index corresponding to the player (case-insensitive)
        player_column = players_cleaned.index(player.strip().lower()) + 1

        # Update the score for the players in the specified activity row
        worksheet.update_cell(activity_id + 1, player_column, score)

        
    except ValueError:
        # If player not found, add a new column for the player
        worksheet.add_cols(1)
        player_column = worksheet.col_count
        worksheet.update_cell(1, player_column, player)
        worksheet.update_cell(activity_id + 1, player_column, score)


# Function to calculate overall scores
def calculate_overall_scores():
    # Get the overall scores worksheet
    worksheet = SHEET.get_worksheet(1)

    # Get all players from the first row (excluding the 'ID' column)
    players = worksheet.row_values(1)[1:]

    # Get all activities and scores from the activity_scores worksheet
    activity_scores = SHEET.get_worksheet(0).get_all_values()[1:]

    # Initialize a dictionary to score total scores for each player
    overall_scores = {players: 0 for player in players}

    # Iterate over each activity and update overall scores for each player
    for activity in activity_scores:
        for i, player_scores in enumerate(activity[3:], start=1):
            overall_scores[players[i-1]] += int(player_scores) if player_score else 0

    return overall_scores


# Main function to handle user input
def main():
    while True:
        print("\n1. Add Activity and Players")
        print("2. Update Scores")
        print("3. Overall Scores")
        print("4. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            date = input("Enter the date: ")
            activity = input("Enter the activity/game: ")
            players = input("Enter player names (separated by coma): ").split(',')
            add_activity(date, activity, players)
        elif choice == '2':
            activity_id = int(input("Enter activity ID: "))
            player = input("Enter player name: ")
            score = int(input("Enter score: "))
            update_scores(activity_id, player, score)
        elif choice == '3':
            overall_scores = calculate_overall_scores
            print("Overall Scores:")
            for player, score in overall_scores.items():
                print(f"{player}: {score}")
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()