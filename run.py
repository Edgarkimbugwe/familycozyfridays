import os
import gspread
import sys
import datetime
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
LIGHT_GREEN = '\033[92m'
LIGHT_CYAN = '\033[96m'
LIGHT_YELLOW = '\033[93m'

APP = "Family Cozy Fridays"

EXIT_MESSAGE = """
This App was developed by Edgar Kimbugwe for PP3
as part of the FULL STACK SOFTWARE DEVELOPMENT DIPLOMA
at Code Institute.

Connect with me:
https://github.com/Edgarkimbugwe
www.linkedin.com/in/edgar-kimbugwe-b87687296
"""


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def logo():
    """
    Logo generated from 
    https://patorjk.com/software/taag/#p=display&h=2&v=0&f=Doom&t=FamilyCozyFridays
    """
    print(LIGHT_CYAN + r"""

     _____                   ______      _      _                    
    /  __ \                  |  ___|    (_)    | |                   
    | /  \/  ___  ____ _   _ | |_  _ __  _   __| |  __ _  _   _  ___ 
    | |     / _ \|_  /| | | ||  _|| '__|| | / _` | / _` || | | |/ __|
    | \__/\| (_) |/ / | |_| || |  | |   | || (_| || (_| || |_| |\__ \
     \____/ \___//___| \__, |\_|  |_|   |_| \__,_| \__,_| \__, ||___/
                        __/ |                              __/ |     
                       |___/                              |___/      

    """ + RESET)
    print(LIGHT_GREEN
          + f"Welcome to Family Cozy Fridays."
            f"\nAn app to store all your activities/scores while playing games with family" 
            f"\nPlease make use of the Menu below." + RESET)


def add_activity(date, activity):
    clear_terminal()
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


def add_players(players_list):
    clear_terminal()
    worksheet = SHEET.get_worksheet(0)

    existing_headers = worksheet.row_values(1)

    # Display existing player names
    print(BLUE + "\nAlready existing player names:" + RESET, ", ".join(existing_headers[3:]))

    # Check if the number of existing players is already 6
    if len(existing_headers[3:]) >= 6:
        print(RED + "You cannot add more than 6 players." + RESET)
        return

    # Prompt the user to add new player names
    while True:
        new_player = input(LIGHT_CYAN + "\nEnter player name (max 5 characters): \n" + RESET)
        new_player = new_player.strip()[:5]

        if new_player.lower() in map(str.lower, existing_headers):
            print(RED + "Player name exists, add another name." + RESET)
        else:
            existing_headers.append(new_player)
            players_list.append(new_player)
            print(BLUE + f"Player '{new_player}' added successfully." + RESET)

        if len(existing_headers[3:]) >= 6:
            print(RED + "You have reached the maximum number of players (6)." + RESET)
            break

        add_another = input(LIGHT_CYAN + "\nDo you want to add another player? (Y/N): \n" + RESET)
        if add_another.lower() != 'y':
            break

    # Update the headers row with the updated list of players
    header_range = f'A1:{chr(ord("A") + len(existing_headers) - 1)}1'
    header_cells = worksheet.range(header_range)
    for i, header in enumerate(existing_headers):
        header_cells[i].value = header
    worksheet.update_cells(header_cells)


def delete_player(player, players):
    clear_terminal()
    player_lower = player.strip().lower()
    if player_lower in map(str.lower, players):
        player_index = [i for i, p in enumerate(players) if p.lower() == player_lower][0]
        player_column = player_index + 4  # Adjusted for the offset of player names starting from the 4th column
        activity_worksheet = SHEET.get_worksheet(0)

        # Ask for confirmation before deleting the player
        confirm = input(RED + f"All score data for '{players[player_index]}' will be lost. Are you sure you want to delete'{players[player_index]}'? (Y/N): \n" + RESET).lower()
        if confirm != 'y':
            print(BLUE + "Deletion canceled." + RESET)
            return

        # Delete the player's column from the activity worksheet
        activity_worksheet.delete_columns(player_column)
        # Remove the player from the players list
        del players[player_index]
        # Update the leaderboard worksheet to remove the player's total score
        calculate_totals()
        print()
        print(BLUE + f"Player '{player}' deleted successfully." + RESET)
    else:
        print(RED + f"Player '{player}' not found. Enter a name from the list above" + RESET)
        delete_player(input(LIGHT_CYAN + "\nEnter player name to delete: \n" + RESET), players)


# Function to update scores for a specific activity
def update_scores(activity_id, player, score):
    clear_terminal()
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
    

def all_activity_scores():
    clear_terminal()
    activities = SHEET.get_worksheet(0).get_all_values()[1:]
    players = SHEET.get_worksheet(0).row_values(1)[3:]

    # Calculate the maximum length of activity name and date
    max_activity_length = max([len(activity[2]) for activity in activities])
    max_date_length = max([len(activity[1]) for activity in activities])

    # Print the header
    print("{:<3} {:<{max_date_length}} {:<{max_activity_length}} ".format("ID", "Date", "Activity", max_date_length=max_date_length, max_activity_length=max_activity_length), end="")
    for player in players:
        print("{:<5} ".format(player), end="")
    print()

    for idx, activity in enumerate(activities, start=1):
        activity_id, date, activity_name = activity[:3]
        scores = activity[3:]                

        # Print the activity details
        print("{:<3} {:<{max_date_length}} {:<{max_activity_length}} ".format(activity_id, date, activity_name, max_date_length=max_date_length, max_activity_length=max_activity_length), end="")
        for score in scores:
            print("{:<5} ".format(score), end="")
        print()


def update_activity_ids():
    worksheet = SHEET.get_worksheet(0)
    activities_data = worksheet.get_all_values()[1:]
    for i, activity in enumerate(activities_data, start=1):
        current_id = int(activity[0])
        if current_id != i:
            # Update the ID if it doesn't match the current index
            worksheet.update_cell(i + 1, 1, i)


def edit_or_delete_activity():
    activities_worksheet = SHEET.get_worksheet(0)
    activities_data = activities_worksheet.get_all_values()[1:]
    activities_headers = activities_worksheet.row_values(1)

    while True:
        # Display the list of activities
        all_activity_scores()

        # Get the ID of the activity to edit or delete
        while True:
            try:
                activity_id = int(input(LIGHT_CYAN + "\nEnter the ID of the activity to edit/delete: " + RESET))
                if not 1 <= activity_id <= len(activities_data):
                    raise ValueError("Invalid ID")
                break  # Exit the loop if input is successfully converted to an integer
            except ValueError:
                print(RED + "Please enter a valid integer ID." + RESET)

        # Find the activity with the specified ID
        activity_index = None
        for i, activity in enumerate(activities_data):
            if int(activity[0]) == activity_id:
                activity_index = i
                break

        if activity_index is None:
            print(RED + "Activity not found." + RESET)
            return

        print("\nActivity details:")
        for i, header in enumerate(activities_headers):
            print(f"{header}: {activities_data[activity_index][i]}")

        while True:
            choice = input(LIGHT_CYAN + "\nDo you want to edit or delete this activity? (edit/delete/abort): " + RESET)
            if choice.lower() == "edit":
                # Edit the activity
                print("\nEnter the new details for the activity:")
                while True:
                    new_date = input(LIGHT_CYAN + "Enter the new date (DD-MM-YY): \n" + RESET)
                    if len(new_date) == 8 and new_date.count('-') == 2:
                        day, month, year = new_date.split('-')
                        if day.isdigit() and month.isdigit() and year.isdigit():
                            day, month, year = int(day), int(month), int(year)
                            if 1 <= month <= 12 and 1 <= day <= 31:
                                break
                    print(RED + "Invalid date format or date out of range. Please enter the date in DD-MM-YY format." + RESET)

                new_activity = input(LIGHT_CYAN + "Enter the new activity name (max 20 characters): \n" + RESET)[:20]

                # Confirm the changes
                confirm_changes = input(LIGHT_CYAN + "\nAre you sure you want to make these changes? (Y/N): " + RESET).lower()
                if confirm_changes == 'y':
                    # Update the activity details
                    activities_data[activity_index][1] = new_date
                    activities_data[activity_index][2] = new_activity

                    # Update the worksheet
                    activities_worksheet.update([activities_data[activity_index][1:3]], f"B{activity_index + 2}:C{activity_index + 2}")

                    print(BLUE + "Activity updated successfully." + RESET)
                else:
                    print(BLUE + "Changes canceled." + RESET)
                break
            elif choice.lower() == "delete":
                # Warn the user before deletion
                confirm_delete = input(RED + "Warning: This action cannot be undone. Are you sure you want to delete this activity? (Y/N): " + RESET).lower()
                if confirm_delete == 'y':
                    # Delete the activity
                    activities_worksheet.delete_rows(activity_index + 2)  # Add 2 to account for 0-indexing and header row
                    update_activity_ids()
                    print(BLUE + "Activity deleted successfully." + RESET)
                else:
                    print(BLUE + "Deletion canceled." + RESET)
                break
            elif choice.lower() == "abort":
                print(BLUE + "Operation aborted." + RESET)
                break
            else:
                print(RED + "Invalid choice. Please enter 'edit', 'delete', or 'abort'." + RESET)

        # Ask if the user wants to edit/delete another activity or return to the main menu
        while True:
            another = input(LIGHT_CYAN + "\nDo you want to edit/delete another activity? (Y/N): " + RESET).lower()
            if another == 'y':
                break
            elif another == 'n':
                return
            else:
                print(RED + "Invalid choice. Please enter 'Y' or 'N'." + RESET)


def exit_app():
    """
    This function displays an exit message to the user.
    The user is asked to confirm the selected option. 
    """
    confirm = input(LIGHT_CYAN + "Are you sure you want to quit? (Y/N): \n" + RESET).lower()
    if confirm == 'y':
        print()
        print()
        print(LIGHT_YELLOW + f"Thank you for using {APP} today!" + RESET)
        print(EXIT_MESSAGE)
        today = datetime.date.today()
        print(today)
        print(LIGHT_YELLOW + "\nCome back again when you are ready to store more scores" + RESET)
        print()
        print()
        # Close the database connection and ensure that all data is properly saved before exit.
        sys.exit(0)
    elif confirm == 'n':
        main()  # Redirect the user to the main menu
    else:
        print(RED + "Invalid choice! Please enter 'Y' or 'N'.")
        exit_app()


# Main function to handle user input
def main():
    logo()
    players = SHEET.get_worksheet(0).row_values(1)[3:]
    activities_data = SHEET.get_worksheet(0).get_all_values()[1:]
    while True:
        print("\n" + " " * 5 + "1. Add Activity")
        print(" " * 5 + "2. Add Player/s")
        print(" " * 5 + "3. Update Scores")
        print(" " * 5 + "4. Leaderboard")
        print(" " * 5 + "5. Edit/Delete Activity")
        print(" " * 5 + "6. Delete Player")
        print(" " * 5 + "7. Exit")
        print()
        choice = input(LIGHT_GREEN + "Enter your choice: \n" + RESET)
        
        clear_terminal()

        if choice == '1':
            while True:
                date = input(LIGHT_CYAN + "Enter the date (DD-MM-YY): \n" + RESET)
                if len(date) == 8 and date.count('-') == 2:
                    day, month, year = date.split('-')
                    if day.isdigit() and month.isdigit() and year.isdigit():
                        day, month, year = int(day), int(month), int(year)
                        if 1 <= month <= 12 and 1 <= day <= 31:
                            break
                print(RED + "Invalid date format or date out of range. Please enter the date in DD-MM-YY format." + RESET)

            activity = input(LIGHT_CYAN + "Enter the activity/game (max 20 characters): \n" + RESET)[:20]
            add_activity(date, activity)
        elif choice == '2':
            add_players(players)
        elif choice == '3':
            # Display list of activities
            print()
            print(LIGHT_CYAN + "Select the activity you want to update scores using the ID No." + RESET)
            print()

            all_activity_scores()          
            
            # get user input for activity ID, Player name and score
            while True:
                try:
                    activity_id = int(input(LIGHT_CYAN + "Enter activity ID: \n" + RESET))
                    if activity_id < 1 or activity_id > len(activities_data):
                        raise ValueError("Invalid ID")
                    break
                except ValueError:
                    print(RED + "Invalid ID. Please enter a valid activity ID." + RESET)

            for player in players:
                while True:
                    player_score = input(LIGHT_CYAN + f"Enter score for {player}: " + RESET)
                    try:
                        score = int(player_score)
                        update_scores(activity_id, player, score)
                        break
                    except ValueError:
                        print(RED + "Please enter a valid score (integer)." + RESET)
            print()
            print(BLUE + "All scores updated for this activity." + RESET)
        elif choice == '4':
            print()
            print(BLUE + "Collecting data....." + RESET)
            calculate_totals()
        elif choice == '5':
            print()
            print(BLUE + "Collecting data....." + RESET)
            print()
            edit_or_delete_activity()
        elif choice == '6':
            print("\nCurrent Players:")
            for header in players:
                print(header)
            player = input(LIGHT_CYAN + "\nEnter player name to delete: \n" + RESET)
            print()
            print(BLUE + f"Deleting '{player}'......" + RESET)
            delete_player(player.lower(), players)
        elif choice == '7':
            print()
            exit_app()
            break
        else:
            print(RED + "Invalid choice, please try again." + RESET)

if __name__ == "__main__":
    main()
