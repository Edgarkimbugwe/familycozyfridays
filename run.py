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

players = []

RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def add_players(players_list):
    worksheet = SHEET.get_worksheet(0)

    existing_headers = worksheet.row_values(1)

    for player in players_list:
        player_lower = player.strip().lower()
        if player_lower not in map(str.lower, existing_headers):
            existing_headers.append(player.strip())
            players.append(player.strip())

    # Update the headers row with the updated list of players
    header_range = f'A1:{chr(ord("A") + len(existing_headers) - 1)}1'
    header_cells = worksheet.range(header_range)
    for i, header in enumerate(existing_headers):
        header_cells[i].value = header
    worksheet.update_cells(header_cells)

def add_activity(date, activity):
    worksheet = SHEET.get_worksheet(0)

    # Find the last non-empty row in the first column
    values_list = worksheet.col_values(1)
    if len(values_list) > 1:
        last_activity_id = max([int(val) for val in values_list[1:] if val])
    else:
        last_activity_id = 0
    activity_id = last_activity_id + 1

    row_data = [activity_id, date, activity]

    print()
    print(BLUE + f"Updating '{activity}' to the worksheet..." + RESET)
    worksheet.append_row(row_data)
    print()
    print(BLUE + f"'{activity}' added to the worksheet." + RESET)

def delete_player(player):
    activity_worksheet = SHEET.get_worksheet(0)
    leaderboard_worksheet = SHEET.get_worksheet(1)

    existing_headers = activity_worksheet.row_values(1)

    player_lower = player.strip().lower()
    if player_lower in map(str.lower, existing_headers):
        player_column = existing_headers.index(player) + 1

        # Delete the player's column from the activity worksheet
        activity_worksheet.delete_columns(player_column)

        # Remove the player from the players list
        global players
        players.remove(player.strip())

        # Update the leaderboard worksheet to remove the player's total score
        calculate_totals()

        print()
        print(BLUE + f"Player '{player}' deleted successfully." + RESET)
    else:
        print(RED + f"Player '{player}' not found." + RESET)

# Function to update scores for a specific activity
def update_scores(activity_id, player, score):
    # Get the Activity_scores worksheet
    worksheet = SHEET.get_worksheet(0)

    # Get the list of player names from the first row of the worksheet
    players_list = worksheet.row_values(1)

    # Remove leading and trailing spaces from player names
    players_cleaned = [p.strip().lower() for p in players_list]

    if player.strip().lower() not in players_cleaned:
        print()
        print(RED + f"'{player}' is not registered as a player." + RESET)
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


# Function to calculate overall scores and display the leaderboard
def calculate_totals():
    activity_worksheet = SHEET.get_worksheet(0)
    leaderboard_worksheet = SHEET.get_worksheet(1)

    # Get the list of player names from the first row of the 'activity_score' worksheet
    players = activity_worksheet.row_values(1)[3:]

    # Initialize a dictionary to store total scores for each player
    total_scores = {player: 0 for player in players}

    # Loop through each row in the activity worksheet to calculate total scores
    for row in activity_worksheet.get_all_values()[1:]:
        for i, score in enumerate(row[3:], start=3):
            # Skip non-integer scores
            try:
                if i - 3 < len(players):
                    total_scores[players[i - 3]] += int(score)
            except ValueError:
                continue

    # Sort players by their total scores in descending order
    sorted_players = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)

    # Update the leaderboard worksheet with the sorted players and their total scores
    print()
    print(BLUE + "Updating total scores and ranking the players...." + RESET)
    print()
    leaderboard_worksheet.clear()
    leaderboard_worksheet.append_row(['Position', 'Name', 'Total score'])
    
    # Calculate the maximum length of player names for formatting
    max_name_length = max([len(player) for player, _ in sorted_players])
    
    for i, (player, total_score) in enumerate(sorted_players, start=1):
        # Format the output to align the scores
        indent = max_name_length - len(player) + 5
        print(f"{i}. {player}{' '*indent} {total_score}")

        leaderboard_worksheet.append_row([i, player, total_score])

    print()
    print(BLUE + "Total scores calculated and updated to the leaderboard worksheet." + RESET)


# Main function to handle user input
def main():
    while True:
        print("\n1. Add Activity")
        print("2. Add Players")
        print("3. Update Scores")
        print("4. Leaderboard")
        print("5. Delete Player")
        print("6. Exit")
        print()
        choice = input("Enter your choice: \n")

        if choice == '1':
            date = input("Enter the date: \n")
            activity = input("Enter the activity/game: \n")
            add_activity(date, activity)
        elif choice == '2':
            players = input("Enter player names (separated by comma): \n").split(',')
            add_players(players)
        elif choice == '3':
            # Display list of activities
            print()
            print("Select the activity you want to update scores using the ID No.")
            print()

            activities = SHEET.get_worksheet(0).get_all_values()[1:]
            players = SHEET.get_worksheet(0).row_values(1)[3:]

            # Calculate the maximum length of activity name and date
            max_activity_length = max([len(activity[2]) for activity in activities])
            max_date_length = max([len(activity[1]) for activity in activities])

            # Print the header
            print("{:<8} {:<{max_date_length}} {:<{max_activity_length}} ".format("ID No.", "Date", "Activity", max_date_length=max_date_length, max_activity_length=max_activity_length), end="")
            for player in players:
                print("{:<12} ".format(player), end="")
            print()

            for idx, activity in enumerate(activities, start=1):
                activity_id, date, activity_name = activity[:3]
                scores = activity[3:]                

                # Print the activity details
                print("{:<8} {:<{max_date_length}} {:<{max_activity_length}} ".format(activity_id, date, activity_name, max_date_length=max_date_length, max_activity_length=max_activity_length), end="")
                for score in scores:
                    print("{:<12} ".format(score), end="")
                print()          
            
            # get user input for activity ID, Player name and score
            print()
            activity_id = int(input("Enter activity ID: \n"))

            for player in players:
                while True:
                    player_score = input(f"Enter score for {player}: ")
                    try:
                        score = int(player_score)
                        update_scores(activity_id, player, score)
                        break
                    except ValueError:
                        print(RED + "Please enter a valid score (integer)." + RESET)
            print()
            print(BLUE + "All scores updated for this activity." + RESET)
        elif choice == '4':
            calculate_totals()
        elif choice == '5':
            player = input("Enter player name to delete: \n")
            delete_player(player)
        elif choice == '6':
            print()
            print("Exiting...")
            break
        else:
            print(RED + "Invalid choice, please try again." + RESET)

if __name__ == "__main__":
    main()
