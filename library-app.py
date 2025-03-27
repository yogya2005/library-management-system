#!/usr/bin/env python3
# Library Management System - Database Application

import sqlite3
import os
import datetime
import sys
import time
from getpass import getpass
from tabulate import tabulate

# Database configuration
DB_FILE = "library.db"

class LibrarySystem:
    def __init__(self, db_file):
        """Initialize the library system with database connection"""
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.current_user = None
        self.user_type = None
        
    def connect_db(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
            
    def close_db(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            
    def execute_query(self, query, params=(), fetch=True, commit=False):
        """Execute a SQL query with parameters"""
        try:
            self.cursor.execute(query, params)
            
            if commit:
                self.conn.commit()
                
            if fetch:
                return self.cursor.fetchall()
            return True
        except sqlite3.Error as e:
            print(f"Query execution error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None
            
    def login(self):
        """Handle user login"""
        clear_screen()
        print("\n===== LIBRARY SYSTEM LOGIN =====\n")
        print("1. Login as Member")
        print("2. Login as Staff")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            email = input("Enter your email: ")
            password = getpass("Enter your password: ")
            
            query = "SELECT * FROM Member WHERE Email = ? AND Password = ?"
            result = self.execute_query(query, (email, password))
            
            if result and len(result) > 0:
                self.current_user = dict(result[0])
                self.user_type = "member"
                print(f"\nWelcome, {self.current_user['FirstName']} {self.current_user['LastName']}!")
                input("Press Enter to continue...")
                return True
            else:
                print("\nInvalid credentials. Please try again.")
                input("Press Enter to continue...")
                return False
                
        elif choice == '2':
            email = input("Enter your staff email: ")
            password = getpass("Enter your password: ")
            
            # In a real application, staff would have passwords too
            # For demo purposes, we're just checking if the email exists
            query = "SELECT * FROM Staff WHERE Email = ?"
            result = self.execute_query(query, (email,))
            
            if result and len(result) > 0:
                self.current_user = dict(result[0])
                self.user_type = "staff"
                print(f"\nWelcome, {self.current_user['FirstName']} {self.current_user['LastName']}!")
                input("Press Enter to continue...")
                return True
            else:
                print("\nInvalid credentials. Please try again.")
                input("Press Enter to continue...")
                return False
                
        elif choice == '3':
            return "exit"
            
        else:
            print("\nInvalid choice. Please try again.")
            input("Press Enter to continue...")
            return False
            
    def find_item(self):
        """Find an item in the library"""
        clear_screen()
        print("\n===== FIND LIBRARY ITEM =====\n")
        print("Search by:")
        print("1. Title")
        print("2. Author/Creator")
        print("3. Item Type")
        print("4. Return to Main Menu")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            search_term = input("Enter title to search for: ")
            query = """
            SELECT i.ItemID, i.Title, i.Status, i.ItemType, i.Location, 
                   CASE 
                       WHEN i.ItemType = 'Book' THEN b.Author
                       WHEN i.ItemType = 'Ebook' THEN e.Author
                       WHEN i.ItemType = 'Magazine' THEN m.Publisher
                       WHEN i.ItemType = 'Journal' THEN j.Publisher
                       WHEN i.ItemType = 'Media' THEN md.Artist
                       ELSE 'Unknown'
                   END as Creator
            FROM LibraryItem i
            LEFT JOIN Book b ON i.ItemID = b.ItemID
            LEFT JOIN Ebook e ON i.ItemID = e.ItemID
            LEFT JOIN Magazine m ON i.ItemID = m.ItemID
            LEFT JOIN Journal j ON i.ItemID = j.ItemID
            LEFT JOIN Media md ON i.ItemID = md.ItemID
            WHERE i.Title LIKE ?
            ORDER BY i.Title
            """
            results = self.execute_query(query, (f'%{search_term}%',))
            
        elif choice == '2':
            search_term = input("Enter author/creator to search for: ")
            query = """
            SELECT i.ItemID, i.Title, i.Status, i.ItemType, i.Location, 
                   CASE 
                       WHEN i.ItemType = 'Book' THEN b.Author
                       WHEN i.ItemType = 'Ebook' THEN e.Author
                       WHEN i.ItemType = 'Magazine' THEN m.Publisher
                       WHEN i.ItemType = 'Journal' THEN j.Publisher
                       WHEN i.ItemType = 'Media' THEN md.Artist
                       ELSE 'Unknown'
                   END as Creator
            FROM LibraryItem i
            LEFT JOIN Book b ON i.ItemID = b.ItemID AND i.ItemType = 'Book'
            LEFT JOIN Ebook e ON i.ItemID = e.ItemID AND i.ItemType = 'Ebook'
            LEFT JOIN Magazine m ON i.ItemID = m.ItemID AND i.ItemType = 'Magazine'
            LEFT JOIN Journal j ON i.ItemID = j.ItemID AND i.ItemType = 'Journal'
            LEFT JOIN Media md ON i.ItemID = md.ItemID AND i.ItemType = 'Media'
            WHERE b.Author LIKE ? OR e.Author LIKE ? OR m.Publisher LIKE ? 
                  OR j.Publisher LIKE ? OR md.Artist LIKE ?
            ORDER BY i.Title
            """
            params = (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', 
                     f'%{search_term}%', f'%{search_term}%')
            results = self.execute_query(query, params)
            
        elif choice == '3':
            print("\nItem Types:")
            print("1. Book")
            print("2. Ebook")
            print("3. Magazine")
            print("4. Journal")
            print("5. Media (CD/DVD/Record)")
            
            type_choice = input("\nEnter your choice (1-5): ")
            item_types = {
                '1': 'Book',
                '2': 'Ebook',
                '3': 'Magazine',
                '4': 'Journal',
                '5': 'Media'
            }
            
            if type_choice in item_types:
                item_type = item_types[type_choice]
                query = """
                SELECT i.ItemID, i.Title, i.Status, i.ItemType, i.Location, 
                       CASE 
                           WHEN i.ItemType = 'Book' THEN b.Author
                           WHEN i.ItemType = 'Ebook' THEN e.Author
                           WHEN i.ItemType = 'Magazine' THEN m.Publisher
                           WHEN i.ItemType = 'Journal' THEN j.Publisher
                           WHEN i.ItemType = 'Media' THEN md.Artist
                           ELSE 'Unknown'
                       END as Creator
                FROM LibraryItem i
                LEFT JOIN Book b ON i.ItemID = b.ItemID
                LEFT JOIN Ebook e ON i.ItemID = e.ItemID
                LEFT JOIN Magazine m ON i.ItemID = m.ItemID
                LEFT JOIN Journal j ON i.ItemID = j.ItemID
                LEFT JOIN Media md ON i.ItemID = md.ItemID
                WHERE i.ItemType = ?
                ORDER BY i.Title
                """
                results = self.execute_query(query, (item_type,))
            else:
                print("\nInvalid choice.")
                input("Press Enter to continue...")
                return
                
        elif choice == '4':
            return
            
        else:
            print("\nInvalid choice. Please try again.")
            input("Press Enter to continue...")
            return
            
        # Display search results
        if results and len(results) > 0:
            # Format the results for tabulate
            headers = ["ID", "Title", "Creator", "Type", "Status", "Location"]
            table_data = []
            
            for item in results:
                table_data.append([
                    item['ItemID'],
                    item['Title'],
                    item['Creator'],
                    item['ItemType'],
                    item['Status'],
                    item['Location']
                ])
            
            print("\nSearch Results:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            # If member is logged in, offer to borrow an item
            if self.user_type == "member":
                borrow_choice = input("\nWould you like to borrow an item? (y/n): ")
                if borrow_choice.lower() == 'y':
                    item_id = input("Enter the ID of the item you want to borrow: ")
                    # Call borrow function
                    self.borrow_item(item_id)
        else:
            print("\nNo items found matching your search criteria.")
            
        input("\nPress Enter to continue...")
        
    def borrow_item(self, item_id=None):
        """Borrow an item from the library"""
        if self.user_type != "member":
            print("\nYou need to be logged in as a member to borrow items.")
            input("Press Enter to continue...")
            return
            
        clear_screen()
        print("\n===== BORROW LIBRARY ITEM =====\n")
        
        if not item_id:
            item_id = input("Enter the ID of the item you want to borrow: ")
        
        # Check if item exists and is available
        query = "SELECT * FROM LibraryItem WHERE ItemID = ?"
        item = self.execute_query(query, (item_id,))
        
        if not item or len(item) == 0:
            print(f"\nItem with ID {item_id} not found.")
            input("Press Enter to continue...")
            return
            
        item = dict(item[0])
        
        if item['Status'] != 'Available':
            print(f"\nItem '{item['Title']}' is not available for borrowing (Status: {item['Status']}).")
            input("Press Enter to continue...")
            return
            
        # Check if user already has active borrowings for this item
        query = """
        SELECT * FROM Borrowing 
        WHERE MemberID = ? AND ItemID = ? AND ReturnDate IS NULL
        """
        existing_borrow = self.execute_query(query, (self.current_user['MemberID'], item_id))
        
        if existing_borrow and len(existing_borrow) > 0:
            print(f"\nYou already have borrowed '{item['Title']}' and haven't returned it yet.")
            input("Press Enter to continue...")
            return
            
        # Calculate due date (14 days from today)
        borrow_date = datetime.date.today()
        due_date = borrow_date + datetime.timedelta(days=14)
        
        # Create borrowing record
        query = """
        INSERT INTO Borrowing (MemberID, ItemID, BorrowDate, DueDate)
        VALUES (?, ?, ?, ?)
        """
        result = self.execute_query(
            query, 
            (self.current_user['MemberID'], item_id, borrow_date, due_date),
            fetch=False,
            commit=True
        )
        
        if result:
            # Update item status
            update_query = "UPDATE LibraryItem SET Status = 'Borrowed' WHERE ItemID = ?"
            self.execute_query(update_query, (item_id,), fetch=False, commit=True)
            
            print(f"\nSuccessfully borrowed: {item['Title']}")
            print(f"Due date: {due_date}")
            print("\nPlease return the item by the due date to avoid fines.")
        else:
            print("\nFailed to borrow the item. Please try again.")
            
        input("\nPress Enter to continue...")
        
    def return_item(self):
        """Return a borrowed item"""
        if self.user_type != "member":
            print("\nYou need to be logged in as a member to return items.")
            input("Press Enter to continue...")
            return
            
        clear_screen()
        print("\n===== RETURN BORROWED ITEM =====\n")
        
        # Get user's active borrowings
        query = """
        SELECT b.BorrowID, i.ItemID, i.Title, i.ItemType, b.BorrowDate, b.DueDate
        FROM Borrowing b
        JOIN LibraryItem i ON b.ItemID = i.ItemID
        WHERE b.MemberID = ? AND b.ReturnDate IS NULL
        ORDER BY b.DueDate
        """
        borrowings = self.execute_query(query, (self.current_user['MemberID'],))
        
        if not borrowings or len(borrowings) == 0:
            print("\nYou don't have any active borrowings to return.")
            input("Press Enter to continue...")
            return
            
        # Display borrowings
        headers = ["Borrow ID", "Item ID", "Title", "Type", "Borrow Date", "Due Date"]
        table_data = []
        
        for borrow in borrowings:
            table_data.append([
                borrow['BorrowID'],
                borrow['ItemID'],
                borrow['Title'],
                borrow['ItemType'],
                borrow['BorrowDate'],
                borrow['DueDate']
            ])
        
        print("\nYour Active Borrowings:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Ask which item to return
        borrow_id = input("\nEnter the Borrow ID of the item you want to return (or 0 to cancel): ")
        
        if borrow_id == '0':
            return
            
        # Find the borrowing record
        found = False
        for borrow in borrowings:
            if str(borrow['BorrowID']) == borrow_id:
                found = True
                item_id = borrow['ItemID']
                break
                
        if not found:
            print(f"\nBorrow ID {borrow_id} not found in your active borrowings.")
            input("Press Enter to continue...")
            return
            
        # Process return
        return_date = datetime.date.today()
        
        # Update borrowing record
        query = """
        UPDATE Borrowing
        SET ReturnDate = ?
        WHERE BorrowID = ?
        """
        result = self.execute_query(query, (return_date, borrow_id), fetch=False, commit=True)
        
        if result:
            # Update item status
            update_query = "UPDATE LibraryItem SET Status = 'Available' WHERE ItemID = ?"
            self.execute_query(update_query, (item_id,), fetch=False, commit=True)
            
            # Check if return is late and create fine if needed
            due_date = datetime.datetime.strptime(borrow['DueDate'], '%Y-%m-%d').date()
            
            if return_date > due_date:
                days_late = (return_date - due_date).days
                fine_amount = days_late * 0.50  # $0.50 per day late
                
                # Check if a fine already exists for this borrowing
                check_query = "SELECT FineID FROM Fine WHERE BorrowID = ?"
                existing_fine = self.execute_query(check_query, (borrow_id,))
                
                if existing_fine and len(existing_fine) > 0:
                    # Update existing fine
                    update_query = """
                    UPDATE Fine
                    SET Amount = ?, Status = 'Unpaid', IssuedDate = ?
                    WHERE BorrowID = ?
                    """
                    self.execute_query(
                        update_query,
                        (fine_amount, return_date, borrow_id),
                        fetch=False,
                        commit=True
                    )
                    print(f"\nExisting fine updated to ${fine_amount:.2f} ({days_late} days late).")
                else:
                    # Create new fine
                    fine_query = """
                    INSERT INTO Fine (BorrowID, Amount, Status, IssuedDate)
                    VALUES (?, ?, ?, ?)
                    """
                    self.execute_query(
                        fine_query, 
                        (borrow_id, fine_amount, 'Unpaid', return_date),
                        fetch=False,
                        commit=True
                    )
                    print(f"\nA fine of ${fine_amount:.2f} has been issued ({days_late} days late).")
                
                print(f"\nItem returned successfully, but it was {days_late} days late.")
                print(f"A fine of ${fine_amount:.2f} has been issued.")
            else:
                print("\nItem returned successfully. Thank you!")
        else:
            print("\nFailed to return the item. Please try again.")
            
        input("\nPress Enter to continue...")
        
    def donate_item(self):
        """Donate an item to the library"""
        clear_screen()
        print("\n===== DONATE ITEM TO LIBRARY =====\n")
        
        # Collect basic item information
        while True:
            title = input("Enter item title: ")
            if title.strip():
                break
            print("Title cannot be empty. Please try again.")

        pub_date = input("Enter publication date (YYYY-MM-DD) or press Enter to skip: ")
        
        if not pub_date:
            pub_date = None
            
        print("\nItem Types:")
        print("1. Book")
        print("2. Ebook")
        print("3. Magazine")
        print("4. Journal")
        print("5. Media (CD/DVD/Record)")
        
        item_type_choice = input("\nSelect item type (1-5): ")
        
        item_types = {
            '1': 'Book',
            '2': 'Ebook',
            '3': 'Magazine',
            '4': 'Journal',
            '5': 'Media'
        }
        
        if item_type_choice not in item_types:
            print("\nInvalid item type selection.")
            input("Press Enter to continue...")
            return
            
        item_type = item_types[item_type_choice]
        
        # Insert into LibraryItem table first
        query = """
        INSERT INTO LibraryItem (Title, PublicationDate, Status, ItemType)
        VALUES (?, ?, 'Available', ?)
        """
        result = self.execute_query(query, (title, pub_date, item_type), fetch=False, commit=True)
        
        if not result:
            print("\nFailed to add item. Please try again.")
            input("Press Enter to continue...")
            return
            
        # Get the ID of the newly inserted item
        item_id = self.cursor.lastrowid
        
        # Collect type-specific information
        if item_type == 'Book':
            author = input("Enter author name: ")
            publisher = input("Enter publisher (or press Enter to skip): ")
            genre = input("Enter genre (or press Enter to skip): ")
            pages = input("Enter page count (or press Enter to skip): ")
            format_type = input("Enter format (Hardcover/Paperback/Other): ")
            
            # Insert into Book table
            query = """
            INSERT INTO Book (ItemID, Author, Publisher, Genre, PageCount, Format)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            self.execute_query(
                query, 
                (item_id, author, publisher, genre, pages if pages else None, format_type),
                fetch=False,
                commit=True
            )
            
        elif item_type == 'Ebook':
            author = input("Enter author name: ")
            publisher = input("Enter publisher (or press Enter to skip): ")
            genre = input("Enter genre (or press Enter to skip): ")
            file_format = input("Enter file format (e.g., EPUB, PDF): ")
            
            # Insert into Ebook table
            query = """
            INSERT INTO Ebook (ItemID, Author, Publisher, Genre, FileFormat)
            VALUES (?, ?, ?, ?, ?)
            """
            self.execute_query(
                query, 
                (item_id, author, publisher, genre, file_format),
                fetch=False,
                commit=True
            )
            
        elif item_type == 'Magazine':
            issue = input("Enter issue number: ")
            publisher = input("Enter publisher: ")
            category = input("Enter category (or press Enter to skip): ")
            
            # Insert into Magazine table
            query = """
            INSERT INTO Magazine (ItemID, IssueNumber, Publisher, Category)
            VALUES (?, ?, ?, ?)
            """
            self.execute_query(
                query, 
                (item_id, issue, publisher, category),
                fetch=False,
                commit=True
            )
            
        elif item_type == 'Journal':
            volume = input("Enter volume: ")
            issue = input("Enter issue: ")
            publisher = input("Enter publisher: ")
            field = input("Enter academic field: ")
            peer_reviewed = input("Is it peer-reviewed? (y/n): ").lower() == 'y'
            
            # Insert into Journal table
            query = """
            INSERT INTO Journal (ItemID, Volume, Issue, Publisher, Field, PeerReviewed)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            self.execute_query(
                query, 
                (item_id, volume, issue, publisher, field, peer_reviewed),
                fetch=False,
                commit=True
            )
            
        elif item_type == 'Media':
            media_type = input("Enter media type (CD/DVD/Record/Other): ")
            artist = input("Enter artist/creator: ")
            runtime = input("Enter runtime/duration: ")
            format_info = input("Enter format information: ")
            
            # Insert into Media table
            query = """
            INSERT INTO Media (ItemID, MediaType, Artist, Runtime, Format)
            VALUES (?, ?, ?, ?, ?)
            """
            self.execute_query(
                query, 
                (item_id, media_type, artist, runtime, format_info),
                fetch=False,
                commit=True
            )
            
        print(f"\nThank you for your donation! '{title}' has been added to our collection.")
        input("\nPress Enter to continue...")
        
    def find_event(self):
        """Find an event in the library"""
        clear_screen()
        print("\n===== FIND LIBRARY EVENT =====\n")
        print("Search by:")
        print("1. Upcoming Events")
        print("2. Event Type")
        print("3. Title")
        print("4. Date Range")
        print("5. Return to Main Menu")
        
        choice = input("\nEnter your choice (1-5): ")
        
        today = datetime.date.today()
        
        if choice == '1':
            # Find upcoming events
            query = """
            SELECT e.EventID, e.Title, e.EventType, e.EventDate, e.StartTime, e.EndTime, 
                   e.MaxAttendees, e.TargetAudience, r.RoomName,
                   (SELECT COUNT(*) FROM EventAttendance a WHERE a.EventID = e.EventID AND a.AttendanceStatus != 'Cancelled') as RegisteredAttendees
            FROM Event e
            JOIN Room r ON e.RoomID = r.RoomID
            WHERE e.EventDate >= ?
            ORDER BY e.EventDate, e.StartTime
            """
            results = self.execute_query(query, (today,))
            
        elif choice == '2':
            print("\nEvent Types:")
            print("1. Book Club")
            print("2. Art Show")
            print("3. Film Screening")
            print("4. Workshop")
            print("5. Other")
            
            type_choice = input("\nEnter your choice (1-5): ")
            event_types = {
                '1': 'BookClub',
                '2': 'ArtShow',
                '3': 'Screening',
                '4': 'Workshop',
                '5': 'Other'
            }
            
            if type_choice in event_types:
                event_type = event_types[type_choice]
                query = """
                SELECT e.EventID, e.Title, e.EventType, e.EventDate, e.StartTime, e.EndTime, 
                       e.MaxAttendees, e.TargetAudience, r.RoomName,
                       (SELECT COUNT(*) FROM EventAttendance a WHERE a.EventID = e.EventID AND a.AttendanceStatus != 'Cancelled') as RegisteredAttendees
                FROM Event e
                JOIN Room r ON e.RoomID = r.RoomID
                WHERE e.EventType = ? AND e.EventDate >= ?
                ORDER BY e.EventDate, e.StartTime
                """
                results = self.execute_query(query, (event_type, today))
            else:
                print("\nInvalid choice.")
                input("Press Enter to continue...")
                return
                
        elif choice == '3':
            title = input("Enter event title to search for: ")
            query = """
            SELECT e.EventID, e.Title, e.EventType, e.EventDate, e.StartTime, e.EndTime, 
                   e.MaxAttendees, e.TargetAudience, r.RoomName,
                   (SELECT COUNT(*) FROM EventAttendance a WHERE a.EventID = e.EventID AND a.AttendanceStatus != 'Cancelled') as RegisteredAttendees
            FROM Event e
            JOIN Room r ON e.RoomID = r.RoomID
            WHERE e.Title LIKE ? AND e.EventDate >= ?
            ORDER BY e.EventDate, e.StartTime
            """
            results = self.execute_query(query, (f'%{title}%', today))
            
        elif choice == '4':
            start_date = input("Enter start date (YYYY-MM-DD): ")
            end_date = input("Enter end date (YYYY-MM-DD): ")
            
            try:
                # Validate dates
                datetime.datetime.strptime(start_date, '%Y-%m-%d')
                datetime.datetime.strptime(end_date, '%Y-%m-%d')
                
                query = """
                SELECT e.EventID, e.Title, e.EventType, e.EventDate, e.StartTime, e.EndTime, 
                       e.MaxAttendees, e.TargetAudience, r.RoomName,
                       (SELECT COUNT(*) FROM EventAttendance a WHERE a.EventID = e.EventID AND a.AttendanceStatus != 'Cancelled') as RegisteredAttendees
                FROM Event e
                JOIN Room r ON e.RoomID = r.RoomID
                WHERE e.EventDate BETWEEN ? AND ?
                ORDER BY e.EventDate, e.StartTime
                """
                results = self.execute_query(query, (start_date, end_date))
            except ValueError:
                print("\nInvalid date format. Please use YYYY-MM-DD.")
                input("Press Enter to continue...")
                return
                
        elif choice == '5':
            return
            
        else:
            print("\nInvalid choice. Please try again.")
            input("Press Enter to continue...")
            return
            
        # Display search results
        if results and len(results) > 0:
            # Format the results for tabulate
            headers = ["ID", "Title", "Type", "Date", "Time", "Room", "Audience", "Spots Left"]
            table_data = []
            
            for event in results:
                spots_left = event['MaxAttendees'] - event['RegisteredAttendees']
                table_data.append([
                    event['EventID'],
                    event['Title'],
                    event['EventType'],
                    event['EventDate'],
                    f"{event['StartTime']} - {event['EndTime']}",
                    event['RoomName'],
                    event['TargetAudience'],
                    spots_left
                ])
            
            print("\nSearch Results:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            # If member is logged in, offer to register for an event
            if self.user_type == "member":
                register_choice = input("\nWould you like to register for an event? (y/n): ")
                if register_choice.lower() == 'y':
                    event_id = input("Enter the ID of the event you want to register for: ")
                    # Call register for event function
                    self.register_for_event(event_id)
        else:
            print("\nNo events found matching your search criteria.")
            
        input("\nPress Enter to continue...")
        
    def register_for_event(self, event_id=None):
        """Register for a library event"""
        if self.user_type != "member":
            print("\nYou need to be logged in as a member to register for events.")
            input("Press Enter to continue...")
            return
            
        clear_screen()
        print("\n===== EVENT REGISTRATION =====\n")
        
        if not event_id:
            event_id = input("Enter the ID of the event you want to register for: ")
        
        # Check if event exists and still has spots available
        query = """
        SELECT e.*, r.RoomName,
               (SELECT COUNT(*) FROM EventAttendance a WHERE a.EventID = e.EventID AND a.AttendanceStatus != 'Cancelled') as RegisteredAttendees
        FROM Event e
        JOIN Room r ON e.RoomID = r.RoomID
        WHERE e.EventID = ?
        """
        event = self.execute_query(query, (event_id,))
        
        if not event or len(event) == 0:
            print(f"\nEvent with ID {event_id} not found.")
            input("Press Enter to continue...")
            return
            
        event = dict(event[0])
        
        # Check if event date has already passed
        event_date = datetime.datetime.strptime(event['EventDate'], '%Y-%m-%d').date()
        today = datetime.date.today()
        
        if event_date < today:
            print(f"\nThis event ({event['Title']}) has already taken place on {event['EventDate']}.")
            input("Press Enter to continue...")
            return
            
        # Check if spots are available
        spots_left = event['MaxAttendees'] - event['RegisteredAttendees']
        
        if spots_left <= 0:
            print(f"\nSorry, the event '{event['Title']}' is already at full capacity.")
            input("Press Enter to continue...")
            return
            
        # Check if user is already registered
        query = """
        SELECT * FROM EventAttendance 
        WHERE EventID = ? AND MemberID = ?
        """
        existing_reg = self.execute_query(query, (event_id, self.current_user['MemberID']))
        
        if existing_reg and len(existing_reg) > 0:
            existing_reg = dict(existing_reg[0])
            if existing_reg['AttendanceStatus'] != 'Cancelled':
                print(f"\nYou are already registered for '{event['Title']}'.")
                input("Press Enter to continue...")
                return
            else:
                # If previously cancelled, update registration
                update_query = """
                UPDATE EventAttendance
                SET AttendanceStatus = 'Registered', RegistrationDate = ?
                WHERE EventID = ? AND MemberID = ?
                """
                result = self.execute_query(
                    update_query, 
                    (today, event_id, self.current_user['MemberID']),
                    fetch=False,
                    commit=True
                )
                
                if result:
                    print(f"\nYou have successfully re-registered for '{event['Title']}'")
                    print(f"Date: {event['EventDate']}")
                    print(f"Time: {event['StartTime']} - {event['EndTime']}")
                    print(f"Location: {event['RoomName']}")
                else:
                    print("\nFailed to register for the event. Please try again.")
                    
                input("\nPress Enter to continue...")
                return
        
        # Create registration
        query = """
        INSERT INTO EventAttendance (EventID, MemberID, RegistrationDate, AttendanceStatus)
        VALUES (?, ?, ?, 'Registered')
        """
        result = self.execute_query(
            query, 
            (event_id, self.current_user['MemberID'], today),
            fetch=False,
            commit=True
        )
        
        if result:
            print(f"\nYou have successfully registered for '{event['Title']}'")
            print(f"Date: {event['EventDate']}")
            print(f"Time: {event['StartTime']} - {event['EndTime']}")
            print(f"Location: {event['RoomName']}")
        else:
            print("\nFailed to register for the event. Please try again.")
            
        input("\nPress Enter to continue...")
        
    def volunteer(self):
        """Register as a library volunteer"""
        if self.user_type != "member":
            print("\nYou need to be logged in as a member to volunteer.")
            input("Press Enter to continue...")
            return
            
        clear_screen()
        print("\n===== VOLUNTEER FOR LIBRARY =====\n")
        
        # Check if already registered as volunteer
        query = "SELECT * FROM Volunteer WHERE MemberID = ?"
        existing = self.execute_query(query, (self.current_user['MemberID'],))
        
        if existing and len(existing) > 0:
            existing = dict(existing[0])
            print(f"You are already registered as a volunteer with status: {existing['Status']}")
            
            if existing['Status'] == 'Inactive':
                reactivate = input("\nWould you like to reactivate your volunteer status? (y/n): ")
                if reactivate.lower() == 'y':
                    update_query = """
                    UPDATE Volunteer
                    SET Status = 'Active', StartDate = ?
                    WHERE MemberID = ?
                    """
                    self.execute_query(
                        update_query, 
                        (datetime.date.today(), self.current_user['MemberID']),
                        fetch=False,
                        commit=True
                    )
                    print("\nYour volunteer status has been reactivated. Thank you!")
            else:
                update = input("\nWould you like to update your volunteer information? (y/n): ")
                if update.lower() == 'y':
                    # Keep asking for skills until a non-empty input is provided
                    while True:
                        skills = input(f"Enter your skills and interests (current: {existing['SkillsInterests']}): ")
                        if skills.strip():  # This checks if the input is not empty after removing whitespace
                            break
                        print("Skills and interests cannot be empty. Please try again.")

                    # Keep asking for availability until a non-empty input is provided
                    while True:
                        availability = input(f"Enter your availability hours (current: {existing['AvailabilityHours']}): ")
                        if availability.strip():  # This checks if the input is not empty after removing whitespace
                            break
                        print("Availability hours cannot be empty. Please try again.")
                    
                    update_query = """
                    UPDATE Volunteer
                    SET SkillsInterests = ?, AvailabilityHours = ?
                    WHERE MemberID = ?
                    """
                    self.execute_query(
                        update_query, 
                        (skills, availability, self.current_user['MemberID']),
                        fetch=False,
                        commit=True
                    )
                    print("\nYour volunteer information has been updated. Thank you!")
        else:
            # Collect volunteer information
            skills = input("Enter your skills and interests (e.g., reading to children, event assistance): ")
            availability = input("Enter your availability hours (e.g. Tuesday/Thursday: 6PM - 8PM): ")
            
            # Create volunteer record
            query = """
            INSERT INTO Volunteer (MemberID, SkillsInterests, AvailabilityHours, StartDate, Status)
            VALUES (?, ?, ?, ?, 'Active')
            """
            result = self.execute_query(
                query, 
                (self.current_user['MemberID'], skills, availability, datetime.date.today()),
                fetch=False,
                commit=True
            )
            
            if result:
                print("\nThank you for volunteering! A staff member will contact you soon.")
            else:
                print("\nFailed to register as volunteer. Please try again.")
                
        input("\nPress Enter to continue...")
        
    def ask_for_help(self):
        """Submit a help request to a librarian"""
        if self.user_type != "member":
            print("\nYou need to be logged in as a member to submit help requests.")
            input("Press Enter to continue...")
            return
            
        clear_screen()
        print("\n===== ASK FOR LIBRARIAN HELP =====\n")
        
        # Display user's existing open requests
        query = """
        SELECT r.RequestID, r.RequestDate, r.Description, r.Status, 
               s.FirstName || ' ' || s.LastName as StaffName
        FROM HelpRequest r
        LEFT JOIN Staff s ON r.StaffID = s.StaffID
        WHERE r.MemberID = ? AND r.Status != 'Resolved'
        ORDER BY r.RequestDate DESC
        """
        existing = self.execute_query(query, (self.current_user['MemberID'],))
        
        if existing and len(existing) > 0:
            print("Your Current Open Help Requests:")
            headers = ["ID", "Date", "Description", "Status", "Assigned To"]
            table_data = []
            
            for req in existing:
                table_data.append([
                    req['RequestID'],
                    req['RequestDate'],
                    req['Description'][:30] + ('...' if len(req['Description']) > 30 else ''),
                    req['Status'],
                    req['StaffName'] if req['StaffName'] else 'Not assigned yet'
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print()
            
        # Create new help request
        description = input("Describe what you need help with (or 'cancel' to go back): ")
        
        if description.lower() == 'cancel':
            return
            
        query = """
        INSERT INTO HelpRequest (MemberID, RequestDate, Description, Status)
        VALUES (?, ?, ?, 'Open')
        """
        result = self.execute_query(
            query, 
            (self.current_user['MemberID'], datetime.date.today(), description),
            fetch=False,
            commit=True
        )
        
        if result:
            print("\nYour help request has been submitted. A librarian will assist you soon.")
        else:
            print("\nFailed to submit help request. Please try again.")
            
        input("\nPress Enter to continue...")
        
    def staff_menu(self):
        """Display staff menu options"""
        while True:
            clear_screen()
            print(f"\n===== LIBRARY STAFF MENU =====")
            print(f"Logged in as: {self.current_user['FirstName']} {self.current_user['LastName']} ({self.current_user['Position']})\n")
            
            print("1. Process Item Return")
            print("2. Manage Help Requests")
            print("3. Manage Events")
            print("4. Process Acquisition Requests")
            print("5. Manage Volunteers")
            print("6. View/Manage Fines")
            print("7. Log Out")
            
            choice = input("\nEnter your choice (1-7): ")
            
            if choice == '1':
                self.process_return()
            elif choice == '2':
                self.manage_help_requests()
            elif choice == '3':
                self.manage_events()
            elif choice == '4':
                self.process_acquisitions()
            elif choice == '5':
                self.manage_volunteers()
            elif choice == '6':
                self.manage_fines()
            elif choice == '7':
                self.current_user = None
                self.user_type = None
                print("\nYou have been logged out.")
                input("Press Enter to continue...")
                break
            else:
                print("\nInvalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def member_menu(self):
        """Display member menu options"""
        while True:
            clear_screen()
            print(f"\n===== LIBRARY MEMBER MENU =====")
            print(f"Logged in as: {self.current_user['FirstName']} {self.current_user['LastName']}\n")
            
            print("1. Find an Item")
            print("2. Borrow an Item")
            print("3. Return an Item")
            print("4. Donate an Item")
            print("5. Find an Event")
            print("6. Register for an Event")
            print("7. Volunteer for the Library")
            print("8. Ask for Help from a Librarian")
            print("9. View My Account")
            print("10. Log Out")
            
            choice = input("\nEnter your choice (1-10): ")
            
            if choice == '1':
                self.find_item()
            elif choice == '2':
                self.borrow_item()
            elif choice == '3':
                self.return_item()
            elif choice == '4':
                self.donate_item()
            elif choice == '5':
                self.find_event()
            elif choice == '6':
                self.register_for_event()
            elif choice == '7':
                self.volunteer()
            elif choice == '8':
                self.ask_for_help()
            elif choice == '9':
                self.view_account()
            elif choice == '10':
                self.current_user = None
                self.user_type = None
                print("\nYou have been logged out.")
                input("Press Enter to continue...")
                break
            else:
                print("\nInvalid choice. Please try again.")
                input("Press Enter to continue...")
                
    def process_return(self):
        """Process an item return (staff function)"""
        clear_screen()
        print("\n===== PROCESS ITEM RETURN =====\n")
        
        member_email = input("Enter member email (or press Enter to search by item ID): ")
        
        if member_email:
            # Find member's active borrowings
            query = """
            SELECT b.BorrowID, m.FirstName || ' ' || m.LastName as MemberName, 
                   i.ItemID, i.Title, i.ItemType, b.BorrowDate, b.DueDate
            FROM Borrowing b
            JOIN Member m ON b.MemberID = m.MemberID
            JOIN LibraryItem i ON b.ItemID = i.ItemID
            WHERE m.Email = ? AND b.ReturnDate IS NULL
            ORDER BY b.DueDate
            """
            borrowings = self.execute_query(query, (member_email,))
            
            if not borrowings or len(borrowings) == 0:
                print(f"\nNo active borrowings found for member with email: {member_email}")
                input("Press Enter to continue...")
                return
                
            # Display borrowings
            headers = ["Borrow ID", "Member", "Item ID", "Title", "Type", "Borrow Date", "Due Date"]
            table_data = []
            
            for borrow in borrowings:
                table_data.append([
                    borrow['BorrowID'],
                    borrow['MemberName'],
                    borrow['ItemID'],
                    borrow['Title'],
                    borrow['ItemType'],
                    borrow['BorrowDate'],
                    borrow['DueDate']
                ])
            
            print("\nActive Borrowings:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            # Ask which item to return
            borrow_id = input("\nEnter the Borrow ID of the item being returned (or 0 to cancel): ")
            
            if borrow_id == '0':
                return
            
            # Find the borrowing record
            found = False
            for borrow in borrowings:
                if str(borrow['BorrowID']) == borrow_id:
                    found = True
                    item_id = borrow['ItemID']
                    break
                    
            if not found:
                print(f"\nBorrow ID {borrow_id} not found in the active borrowings list.")
                input("Press Enter to continue...")
                return
                
        else:
            # Search by item ID
            item_id = input("Enter the ID of the item being returned: ")
            
            # Check if item exists and is borrowed
            query = """
            SELECT i.ItemID, i.Title, i.Status, b.BorrowID, b.BorrowDate, b.DueDate,
                   m.FirstName || ' ' || m.LastName as MemberName
            FROM LibraryItem i
            JOIN Borrowing b ON i.ItemID = b.ItemID AND b.ReturnDate IS NULL
            JOIN Member m ON b.MemberID = m.MemberID
            WHERE i.ItemID = ?
            """
            borrow = self.execute_query(query, (item_id,))
            
            if not borrow or len(borrow) == 0:
                print(f"\nItem with ID {item_id} is not currently borrowed or does not exist.")
                input("Press Enter to continue...")
                return
                
            borrow = dict(borrow[0])
            borrow_id = borrow['BorrowID']
            
            print(f"\nItem: {borrow['Title']}")
            print(f"Borrowed by: {borrow['MemberName']}")
            print(f"Borrow date: {borrow['BorrowDate']}")
            print(f"Due date: {borrow['DueDate']}")
            
            confirm = input("\nProcess return for this item? (y/n): ")
            if confirm.lower() != 'y':
                return
        
        # Process return
        return_date = datetime.date.today()
        
        # Update borrowing record
        query = """
        UPDATE Borrowing
        SET ReturnDate = ?, StaffID = ?
        WHERE BorrowID = ?
        """
        result = self.execute_query(
            query, 
            (return_date, self.current_user['StaffID'], borrow_id),
            fetch=False,
            commit=True
        )
        
        if result:
            # Update item status
            update_query = "UPDATE LibraryItem SET Status = 'Available' WHERE ItemID = ?"
            self.execute_query(update_query, (item_id,), fetch=False, commit=True)
            
            # Get borrowing details to check for late return
            query = "SELECT BorrowDate, DueDate FROM Borrowing WHERE BorrowID = ?"
            borrow_details = self.execute_query(query, (borrow_id,))
            borrow_details = dict(borrow_details[0])
            
            due_date = datetime.datetime.strptime(borrow_details['DueDate'], '%Y-%m-%d').date()
            
            if return_date > due_date:
                days_late = (return_date - due_date).days
                fine_amount = days_late * 0.50  # $0.50 per day late
                
                # Check if a fine already exists for this borrowing
                check_query = "SELECT FineID FROM Fine WHERE BorrowID = ?"
                existing_fine = self.execute_query(check_query, (borrow_id,))
                
                if existing_fine and len(existing_fine) > 0:
                    # Update existing fine
                    update_query = """
                    UPDATE Fine
                    SET Amount = ?, Status = 'Unpaid', IssuedDate = ?
                    WHERE BorrowID = ?
                    """
                    self.execute_query(
                        update_query,
                        (fine_amount, return_date, borrow_id),
                        fetch=False,
                        commit=True
                    )
                    print(f"\nExisting fine updated to ${fine_amount:.2f} ({days_late} days late).")
                else:
                    # Create new fine
                    fine_query = """
                    INSERT INTO Fine (BorrowID, Amount, Status, IssuedDate)
                    VALUES (?, ?, ?, ?)
                    """
                    self.execute_query(
                        fine_query, 
                        (borrow_id, fine_amount, 'Unpaid', return_date),
                        fetch=False,
                        commit=True
                    )
                    print(f"\nA fine of ${fine_amount:.2f} has been issued ({days_late} days late).")
                
                print(f"\nItem returned successfully, but it was {days_late} days late.")
                print(f"A fine of ${fine_amount:.2f} has been issued.")
            else:
                print("\nItem returned successfully. Thank you!")
        else:
            print("\nFailed to return the item. Please try again.")
            
        input("\nPress Enter to continue...")
          
    def view_account(self):
        """View member account details"""
        if self.user_type != "member":
            return
            
        clear_screen()
        print(f"\n===== MY ACCOUNT =====")
        print(f"Name: {self.current_user['FirstName']} {self.current_user['LastName']}")
        print(f"Email: {self.current_user['Email']}")
        print(f"Member since: {self.current_user['MembershipDate']}")
        
        # Active borrowings
        query = """
        SELECT b.BorrowID, i.Title, i.ItemType, b.BorrowDate, b.DueDate,
               CASE 
                   WHEN b.DueDate < date('now') THEN 'Overdue'
                   ELSE 'On time' 
               END as Status
        FROM Borrowing b
        JOIN LibraryItem i ON b.ItemID = i.ItemID
        WHERE b.MemberID = ? AND b.ReturnDate IS NULL
        ORDER BY b.DueDate
        """
        borrowings = self.execute_query(query, (self.current_user['MemberID'],))
        
        print("\n--- Active Borrowings ---")
        if borrowings and len(borrowings) > 0:
            headers = ["ID", "Title", "Type", "Borrow Date", "Due Date", "Status"]
            table_data = []
            
            for borrow in borrowings:
                table_data.append([
                    borrow['BorrowID'],
                    borrow['Title'],
                    borrow['ItemType'],
                    borrow['BorrowDate'],
                    borrow['DueDate'],
                    borrow['Status']
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print("You have no active borrowings.")
        
        # Unpaid fines
        query = """
        SELECT f.FineID, f.Amount, f.IssuedDate, i.Title, b.BorrowDate, b.DueDate, b.ReturnDate
        FROM Fine f
        JOIN Borrowing b ON f.BorrowID = b.BorrowID
        JOIN LibraryItem i ON b.ItemID = i.ItemID
        WHERE b.MemberID = ? AND f.Status = 'Unpaid'
        ORDER BY f.IssuedDate
        """
        fines = self.execute_query(query, (self.current_user['MemberID'],))
        
        print("\n--- Unpaid Fines ---")
        if fines and len(fines) > 0:
            headers = ["Fine ID", "Amount", "Issued Date", "Item", "Return Date"]
            table_data = []
            
            total_fines = 0
            for fine in fines:
                table_data.append([
                    fine['FineID'],
                    f"${fine['Amount']:.2f}",
                    fine['IssuedDate'],
                    fine['Title'],
                    fine['ReturnDate']
                ])
                total_fines += fine['Amount']
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            print(f"Total unpaid fines: ${total_fines:.2f}")
        else:
            print("You have no unpaid fines.")
        
        # Upcoming event registrations
        query = """
        SELECT e.Title, e.EventDate, e.StartTime, e.EndTime, r.RoomName
        FROM EventAttendance a
        JOIN Event e ON a.EventID = e.EventID
        JOIN Room r ON e.RoomID = r.RoomID
        WHERE a.MemberID = ? AND a.AttendanceStatus = 'Registered' AND e.EventDate >= date('now')
        ORDER BY e.EventDate, e.StartTime
        """
        events = self.execute_query(query, (self.current_user['MemberID'],))
        
        print("\n--- Upcoming Event Registrations ---")
        if events and len(events) > 0:
            headers = ["Event", "Date", "Time", "Location"]
            table_data = []
            
            for event in events:
                table_data.append([
                    event['Title'],
                    event['EventDate'],
                    f"{event['StartTime']} - {event['EndTime']}",
                    event['RoomName']
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print("You have no upcoming event registrations.")
        
        print("\n--- Help Requests ---")
        query = """
        SELECT RequestID, RequestDate, Description, Status
        FROM HelpRequest
        WHERE MemberID = ? AND Status != 'Resolved'
        ORDER BY RequestDate DESC
        """
        requests = self.execute_query(query, (self.current_user['MemberID'],))
        
        if requests and len(requests) > 0:
            headers = ["ID", "Date", "Description", "Status"]
            table_data = []
            
            for req in requests:
                table_data.append([
                    req['RequestID'],
                    req['RequestDate'],
                    req['Description'][:40] + ('...' if len(req['Description']) > 40 else ''),
                    req['Status']
                ])
            
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
        else:
            print("You have no open help requests.")
            
        input("\nPress Enter to continue...")
        
    def manage_help_requests(self):
        """Manage help requests (staff function)"""
        if self.user_type != "staff":
            return
            
        clear_screen()
        print("\n===== MANAGE HELP REQUESTS =====\n")
        
        print("1. View Open Requests")
        print("2. View My Assigned Requests")
        print("3. View All Requests")
        print("4. Return to Staff Menu")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '4':
            return
            
        if choice == '1':
            query = """
            SELECT r.RequestID, r.RequestDate, m.FirstName || ' ' || m.LastName as MemberName,
                   r.Description, r.Status, s.FirstName || ' ' || s.LastName as StaffName
            FROM HelpRequest r
            JOIN Member m ON r.MemberID = m.MemberID
            LEFT JOIN Staff s ON r.StaffID = s.StaffID
            WHERE r.Status = 'Open'
            ORDER BY r.RequestDate
            """
            title = "Open Help Requests"
            requests = self.execute_query(query)
            
        elif choice == '2':
            query = """
            SELECT r.RequestID, r.RequestDate, m.FirstName || ' ' || m.LastName as MemberName,
                   r.Description, r.Status, s.FirstName || ' ' || s.LastName as StaffName
            FROM HelpRequest r
            JOIN Member m ON r.MemberID = m.MemberID
            LEFT JOIN Staff s ON r.StaffID = s.StaffID
            WHERE r.StaffID = ? AND r.Status != 'Resolved'
            ORDER BY r.RequestDate
            """
            title = "My Assigned Help Requests"
            requests = self.execute_query(query, (self.current_user['StaffID'],))
            
        elif choice == '3':
            query = """
            SELECT r.RequestID, r.RequestDate, m.FirstName || ' ' || m.LastName as MemberName,
                   r.Description, r.Status, s.FirstName || ' ' || s.LastName as StaffName
            FROM HelpRequest r
            JOIN Member m ON r.MemberID = m.MemberID
            LEFT JOIN Staff s ON r.StaffID = s.StaffID
            ORDER BY r.Status, r.RequestDate DESC
            """
            title = "All Help Requests"
            requests = self.execute_query(query)
            
        else:
            print("\nInvalid choice. Please try again.")
            input("Press Enter to continue...")
            return
            
        if not requests or len(requests) == 0:
            print(f"\nNo help requests found.")
            input("Press Enter to continue...")
            return
            
        # Display requests
        headers = ["ID", "Date", "Member", "Description", "Status", "Assigned To"]
        table_data = []
        
        for req in requests:
            table_data.append([
                req['RequestID'],
                req['RequestDate'],
                req['MemberName'],
                req['Description'][:30] + ('...' if len(req['Description']) > 30 else ''),
                req['Status'],
                req['StaffName'] if req['StaffName'] else 'Not assigned'
            ])
        
        print(f"\n{title}:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Ask which request to manage
        request_id = input("\nEnter Request ID to manage (or 0 to go back): ")
        
        if request_id == '0':
            return
            
        # Get specific request
        query = """
        SELECT r.*, m.FirstName || ' ' || m.LastName as MemberName,
               s.FirstName || ' ' || s.LastName as StaffName
        FROM HelpRequest r
        JOIN Member m ON r.MemberID = m.MemberID
        LEFT JOIN Staff s ON r.StaffID = s.StaffID
        WHERE r.RequestID = ?
        """
        request = self.execute_query(query, (request_id,))
        
        if not request or len(request) == 0:
            print(f"\nRequest ID {request_id} not found.")
            input("Press Enter to continue...")
            return
            
        request = dict(request[0])
        
        clear_screen()
        print(f"\n===== HELP REQUEST #{request['RequestID']} =====")
        print(f"Date: {request['RequestDate']}")
        print(f"Member: {request['MemberName']}")
        print(f"Status: {request['Status']}")
        print(f"Assigned To: {request['StaffName'] if request['StaffName'] else 'Not assigned'}")
        print(f"\nDescription: {request['Description']}")
        
        if request['Resolution']:
            print(f"\nResolution: {request['Resolution']}")
        
        print("\nAction Options:")
        print("1. Assign to Me")
        print("2. Update Status")
        print("3. Add Resolution")
        print("4. Go Back")
        
        action = input("\nEnter your choice (1-4): ")
        
        if action == '1':
            # Assign to current staff
            update_query = """
            UPDATE HelpRequest
            SET StaffID = ?, Status = CASE WHEN Status = 'Open' THEN 'InProgress' ELSE Status END
            WHERE RequestID = ?
            """
            self.execute_query(
                update_query,
                (self.current_user['StaffID'], request_id),
                fetch=False,
                commit=True
            )
            print("\nRequest has been assigned to you.")
            
        elif action == '2':
            # Update status
            print("\nNew Status:")
            print("1. Open")
            print("2. In Progress")
            print("3. Resolved")
            
            status_choice = input("Enter your choice (1-3): ")
            status_options = {
                '1': 'Open',
                '2': 'InProgress',
                '3': 'Resolved'
            }
            
            if status_choice in status_options:
                new_status = status_options[status_choice]
                closed_date = datetime.date.today() if new_status == 'Resolved' else None
                
                update_query = """
                UPDATE HelpRequest
                SET Status = ?, ClosedDate = ?
                WHERE RequestID = ?
                """
                self.execute_query(
                    update_query,
                    (new_status, closed_date, request_id),
                    fetch=False,
                    commit=True
                )
                print(f"\nStatus updated to '{new_status}'.")
            else:
                print("\nInvalid choice.")
                
        elif action == '3':
            # Add resolution
            resolution = input("\nEnter resolution details: ")
            
            update_query = """
            UPDATE HelpRequest
            SET Resolution = ?, Status = 'Resolved', ClosedDate = ?
            WHERE RequestID = ?
            """
            self.execute_query(
                update_query,
                (resolution, datetime.date.today(), request_id),
                fetch=False,
                commit=True
            )
            print("\nResolution added and request marked as Resolved.")
            
        input("\nPress Enter to continue...")
        
    def manage_events(self):
        """Manage library events (staff function)"""
        if self.user_type != "staff":
            return
            
        clear_screen()
        print("\n===== MANAGE LIBRARY EVENTS =====\n")
        
        print("1. View Upcoming Events")
        print("2. View Past Events")
        print("3. Create New Event")
        print("4. Manage Event Attendance")
        print("5. Return to Staff Menu")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '5':
            return
            
        today = datetime.date.today()
        
        if choice == '1' or choice == '2':
            # View events
            if choice == '1':
                # Upcoming events
                query = """
                SELECT e.EventID, e.Title, e.EventType, e.EventDate, e.StartTime, e.EndTime,
                       e.MaxAttendees, r.RoomName,
                       (SELECT COUNT(*) FROM EventAttendance a WHERE a.EventID = e.EventID AND a.AttendanceStatus != 'Cancelled') as RegisteredCount,
                       s.FirstName || ' ' || s.LastName as OrganizerName
                FROM Event e
                JOIN Room r ON e.RoomID = r.RoomID
                LEFT JOIN Staff s ON e.StaffID = s.StaffID
                WHERE e.EventDate >= ?
                ORDER BY e.EventDate, e.StartTime
                """
                title = "Upcoming Events"
                events = self.execute_query(query, (today,))
            else:
                # Past events
                query = """
                SELECT e.EventID, e.Title, e.EventType, e.EventDate, e.StartTime, e.EndTime,
                       e.MaxAttendees, r.RoomName,
                       (SELECT COUNT(*) FROM EventAttendance a WHERE a.EventID = e.EventID AND a.AttendanceStatus != 'Cancelled') as RegisteredCount,
                       s.FirstName || ' ' || s.LastName as OrganizerName
                FROM Event e
                JOIN Room r ON e.RoomID = r.RoomID
                LEFT JOIN Staff s ON e.StaffID = s.StaffID
                WHERE e.EventDate < ?
                ORDER BY e.EventDate DESC, e.StartTime
                LIMIT 20
                """
                title = "Past Events (Last 20)"
                events = self.execute_query(query, (today,))
                
            if not events or len(events) == 0:
                print(f"\nNo {title.lower()} found.")
                input("Press Enter to continue...")
                return
                
            # Display events
            headers = ["ID", "Title", "Type", "Date", "Time", "Room", "Attendance", "Organizer"]
            table_data = []
            
            for event in events:
                attendance = f"{event['RegisteredCount']}/{event['MaxAttendees']}"
                table_data.append([
                    event['EventID'],
                    event['Title'],
                    event['EventType'],
                    event['EventDate'],
                    f"{event['StartTime']} - {event['EndTime']}",
                    event['RoomName'],
                    attendance,
                    event['OrganizerName']
                ])
            
            print(f"\n{title}:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            # Ask which event to manage
            event_id = input("\nEnter Event ID to view longer description (or 0 to go back): ")
            
            if event_id == '0':
                return
                
            # Get specific event
            query = """
            SELECT e.*, r.RoomName, s.FirstName || ' ' || s.LastName as OrganizerName,
                   (SELECT COUNT(*) FROM EventAttendance a WHERE a.EventID = e.EventID AND a.AttendanceStatus != 'Cancelled') as RegisteredCount
            FROM Event e
            JOIN Room r ON e.RoomID = r.RoomID
            LEFT JOIN Staff s ON e.StaffID = s.StaffID
            WHERE e.EventID = ?
            """
            event = self.execute_query(query, (event_id,))
            
            if not event or len(event) == 0:
                print(f"\nEvent ID {event_id} not found.")
                input("Press Enter to continue...")
                return
                
            event = dict(event[0])
            
            clear_screen()
            print(f"\n===== EVENT DETAILS: {event['Title']} =====")
            print(f"Date: {event['EventDate']}")
            print(f"Time: {event['StartTime']} - {event['EndTime']}")
            print(f"Type: {event['EventType']}")
            print(f"Location: {event['RoomName']}")
            print(f"Target Audience: {event['TargetAudience']}")
            print(f"Organizer: {event['OrganizerName']}")
            print(f"Attendance: {event['RegisteredCount']}/{event['MaxAttendees']}")
            print(f"\nDescription: {event['Description']}")
            
            # Display event attendees
            query = """
            SELECT a.AttendanceID, m.FirstName || ' ' || m.LastName as MemberName,
                   m.Email, a.RegistrationDate, a.AttendanceStatus
            FROM EventAttendance a
            JOIN Member m ON a.MemberID = m.MemberID
            WHERE a.EventID = ?
            ORDER BY a.RegistrationDate
            """
            attendees = self.execute_query(query, (event_id,))
            
            if attendees and len(attendees) > 0:
                headers = ["ID", "Member", "Email", "Registration Date", "Status"]
                table_data = []
                
                for attendee in attendees:
                    table_data.append([
                        attendee['AttendanceID'],
                        attendee['MemberName'],
                        attendee['Email'],
                        attendee['RegistrationDate'],
                        attendee['AttendanceStatus']
                    ])
                
                print("\nRegistered Attendees:")
                print(tabulate(table_data, headers=headers, tablefmt="grid"))
            else:
                print("\nNo registered attendees for this event.")
                
            input("\nPress Enter to continue...")
            
        elif choice == '3':
            # Create new event
            clear_screen()
            print("\n===== CREATE NEW EVENT =====\n")
            
            title = input("Event Title: ")
            description = input("Event Description: ")
            
            # Get event date
            while True:
                event_date = input("Event Date (YYYY-MM-DD): ")
                try:
                    datetime.datetime.strptime(event_date, '%Y-%m-%d')
                    break
                except ValueError:
                    print("Invalid date format. Please use YYYY-MM-DD.")
                    
            # Get event time
            while True:
                start_time = input("Start Time (HH:MM): ")
                end_time = input("End Time (HH:MM): ")
                try:
                    start = datetime.datetime.strptime(start_time, '%H:%M').time()
                    end = datetime.datetime.strptime(end_time, '%H:%M').time()
                    if start >= end:
                        print("End time must be after start time.")
                    else:
                        break
                except ValueError:
                    print("Invalid time format. Please use HH:MM (24-hour format).")
                    
            max_attendees = input("Maximum Attendees: ")
            if not max_attendees.isdigit():
                max_attendees = 20  # Default value
            
            target_audience = input("Target Audience: ")
            
            # Event type selection
            print("\nEvent Types:")
            print("1. Book Club")
            print("2. Art Show")
            print("3. Film Screening")
            print("4. Workshop")
            print("5. Other")
            
            type_choice = input("\nSelect event type (1-5): ")
            event_types = {
                '1': 'BookClub',
                '2': 'ArtShow',
                '3': 'Screening',
                '4': 'Workshop',
                '5': 'Other'
            }
            event_type = event_types.get(type_choice, 'Other')
            
            # Room selection
            query = """
            SELECT r.RoomID, r.RoomName, r.Capacity, r.Location
            FROM Room r
            WHERE r.AvailabilityStatus = 'Available'
            ORDER BY r.RoomName
            """
            rooms = self.execute_query(query)
            
            if not rooms or len(rooms) == 0:
                print("\nNo available rooms found.")
                input("Press Enter to continue...")
                return
                
            headers = ["ID", "Room Name", "Capacity", "Location"]
            table_data = []
            
            for room in rooms:
                table_data.append([
                    room['RoomID'],
                    room['RoomName'],
                    room['Capacity'],
                    room['Location']
                ])
            
            print("\nAvailable Rooms:")
            print(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            room_id = input("\nSelect Room ID: ")
            
            # Create event
            query = """
            INSERT INTO Event (Title, Description, EventDate, StartTime, EndTime, MaxAttendees, 
                               EventType, TargetAudience, StaffID, RoomID)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            result = self.execute_query(
                query,
                (title, description, event_date, start_time, end_time, max_attendees,
                 event_type, target_audience, self.current_user['StaffID'], room_id),
                fetch=False,
                commit=True
            )
            
            if result:
                print("\nEvent created successfully!")
            else:
                print("\nFailed to create event. Please try again.")
                
            input("\nPress Enter to continue...")
            
        elif choice == '4':
            # Manage event attendance
            clear_screen()
            print("\n===== MANAGE EVENT ATTENDANCE =====\n")
            
            event_id = input("Enter Event ID: ")
            
            # Get event details
            query = """
            SELECT e.EventID, e.Title, e.EventDate, e.StartTime, e.EndTime, e.MaxAttendees,
                   r.RoomName,
                   (SELECT COUNT(*) FROM EventAttendance a WHERE a.EventID = e.EventID AND a.AttendanceStatus != 'Cancelled') as RegisteredCount
            FROM Event e
            JOIN Room r ON e.RoomID = r.RoomID
            WHERE e.EventID = ?
            """
            event = self.execute_query(query, (event_id,))
            
            if not event or len(event) == 0:
                print(f"\nEvent ID {event_id} not found.")
                input("Press Enter to continue...")
                return
                
            event = dict(event[0])
            
            print(f"\nEvent: {event['Title']}")
            print(f"Date: {event['EventDate']} ({event['StartTime']} - {event['EndTime']})")
            print(f"Location: {event['RoomName']}")
            print(f"Attendance: {event['RegisteredCount']}/{event['MaxAttendees']}")
            
            print("\n1. View and Manage Attendees")
            print("2. Add Attendee")
            print("3. Go Back")
            
            action = input("\nEnter your choice (1-4): ")
            
            if action == '1':
                # View attendees
                query = """
                SELECT a.AttendanceID, m.FirstName || ' ' || m.LastName as MemberName,
                       m.Email, a.RegistrationDate, a.AttendanceStatus
                FROM EventAttendance a
                JOIN Member m ON a.MemberID = m.MemberID
                WHERE a.EventID = ?
                ORDER BY a.RegistrationDate
                """
                attendees = self.execute_query(query, (event_id,))
                
                if attendees and len(attendees) > 0:
                    headers = ["ID", "Member", "Email", "Registration Date", "Status"]
                    table_data = []
                    
                    for attendee in attendees:
                        table_data.append([
                            attendee['AttendanceID'],
                            attendee['MemberName'],
                            attendee['Email'],
                            attendee['RegistrationDate'],
                            attendee['AttendanceStatus']
                        ])
                    
                    print("\nRegistered Attendees:")
                    print(tabulate(table_data, headers=headers, tablefmt="grid"))
                else:
                    print("\nNo registered attendees for this event.")

                # Update attendance status
                attendance_id = input("\nEnter Attendance ID to update status (or 0 to go back): ")

                if attendance_id == '0':
                    return
                
                # Get attendance record
                query = """
                SELECT a.*, m.FirstName || ' ' || m.LastName as MemberName
                FROM EventAttendance a
                JOIN Member m ON a.MemberID = m.MemberID
                WHERE a.AttendanceID = ? AND a.EventID = ?
                """
                attendance = self.execute_query(query, (attendance_id, event_id))
                
                if not attendance or len(attendance) == 0:
                    print(f"\nAttendance ID {attendance_id} not found for this event.")
                    input("Press Enter to continue...")
                    return
                    
                attendance = dict(attendance[0])
                
                print(f"\nMember: {attendance['MemberName']}")
                print(f"Current Status: {attendance['AttendanceStatus']}")
                
                print("\nNew Status:")
                print("1. Registered")
                print("2. Attended")
                print("3. Cancelled")
                
                status_choice = input("\nSelect new status (1-3): ")
                status_options = {
                    '1': 'Registered',
                    '2': 'Attended',
                    '3': 'Cancelled'
                }
                
                if status_choice in status_options:
                    new_status = status_options[status_choice]
                    
                    update_query = """
                    UPDATE EventAttendance
                    SET AttendanceStatus = ?
                    WHERE AttendanceID = ?
                    """
                    self.execute_query(
                        update_query,
                        (new_status, attendance_id),
                        fetch=False,
                        commit=True
                    )
                    
                    print(f"\nAttendance status updated to: {new_status}")
                else:
                    print("\nInvalid choice.")
                    
            elif action == '2':
                # Add attendee
                member_email = input("\nEnter member email to add: ")
                
                # Check if member exists
                query = "SELECT MemberID, FirstName, LastName FROM Member WHERE Email = ?"
                member = self.execute_query(query, (member_email,))
                
                if not member or len(member) == 0:
                    print(f"\nNo member found with email: {member_email}")
                    input("Press Enter to continue...")
                    return
                    
                member = dict(member[0])
                
                # Check if already registered
                query = """
                SELECT * FROM EventAttendance 
                WHERE EventID = ? AND MemberID = ?
                """
                existing = self.execute_query(query, (event_id, member['MemberID']))
                
                if existing and len(existing) > 0:
                    existing = dict(existing[0])
                    if existing['AttendanceStatus'] != 'Cancelled':
                        print(f"\nMember {member['FirstName']} {member['LastName']} is already registered for this event.")
                    else:
                        # Update from cancelled to registered
                        update_query = """
                        UPDATE EventAttendance
                        SET AttendanceStatus = 'Registered', RegistrationDate = ?
                        WHERE EventID = ? AND MemberID = ?
                        """
                        self.execute_query(
                            update_query,
                            (datetime.date.today(), event_id, member['MemberID']),
                            fetch=False,
                            commit=True
                        )
                        print(f"\nMember {member['FirstName']} {member['LastName']} has been re-registered for this event.")
                else:
                    # Check capacity
                    if event['RegisteredCount'] >= event['MaxAttendees']:
                        print("\nThis event has reached maximum capacity.")
                    else:
                        # Add attendance record
                        query = """
                        INSERT INTO EventAttendance (EventID, MemberID, RegistrationDate, AttendanceStatus)
                        VALUES (?, ?, ?, 'Registered')
                        """
                        result = self.execute_query(
                            query,
                            (event_id, member['MemberID'], datetime.date.today()),
                            fetch=False,
                            commit=True
                        )
                        
                        if result:
                            print(f"\nMember {member['FirstName']} {member['LastName']} has been registered for this event.")
                        else:
                            print("\nFailed to register member. Please try again.")
                    
            input("\nPress Enter to continue...")
            
        else:
            print("\nInvalid choice. Please try again.")
            input("Press Enter to continue...")
            
    def process_acquisitions(self):
        """Process acquisition requests (staff function)"""
        if self.user_type != "staff":
            return
            
        clear_screen()
        print("\n===== PROCESS ACQUISITION REQUESTS =====\n")
        
        print("1. View Pending Requests")
        print("2. View All Requests")
        print("3. Return to Staff Menu")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '3':
            return
            
        if choice == '1':
            query = """
            SELECT r.RequestID, r.Title, r.AuthorCreator, r.PublicationType, 
                   r.RequestDate, m.FirstName || ' ' || m.LastName as MemberName
            FROM AcquisitionRequest r
            JOIN Member m ON r.MemberID = m.MemberID
            WHERE r.Status = 'Pending'
            ORDER BY r.RequestDate
            """
            title = "Pending Acquisition Requests"
            
        elif choice == '2':
            query = """
            SELECT r.RequestID, r.Title, r.AuthorCreator, r.PublicationType, 
                   r.RequestDate, r.Status, m.FirstName || ' ' || m.LastName as MemberName
            FROM AcquisitionRequest r
            JOIN Member m ON r.MemberID = m.MemberID
            ORDER BY r.Status, r.RequestDate DESC
            """
            title = "All Acquisition Requests"
            
        else:
            print("\nInvalid choice. Please try again.")
            input("Press Enter to continue...")
            return
            
        requests = self.execute_query(query)
        
        if not requests or len(requests) == 0:
            print(f"\nNo acquisition requests found.")
            input("Press Enter to continue...")
            return
            
        # Display requests
        headers = ["ID", "Title", "Author/Creator", "Type", "Date", "Requested By"]
        if choice == '2':
            headers.insert(5, "Status")
            
        table_data = []
        
        for req in requests:
            row = [
                req['RequestID'],
                req['Title'],
                req['AuthorCreator'],
                req['PublicationType'],
                req['RequestDate'],
                req['MemberName']
            ]
            if choice == '2':
                row.insert(5, req['Status'])
                
            table_data.append(row)
        
        print(f"\n{title}:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Ask which request to process
        request_id = input("\nEnter Request ID to process (or 0 to go back): ")
        
        if request_id == '0':
            return
            
        # Get specific request
        query = """
        SELECT r.*, m.FirstName || ' ' || m.LastName as MemberName,
               s.FirstName || ' ' || s.LastName as StaffName
        FROM AcquisitionRequest r
        JOIN Member m ON r.MemberID = m.MemberID
        LEFT JOIN Staff s ON r.StaffID = s.StaffID
        WHERE r.RequestID = ?
        """
        request = self.execute_query(query, (request_id,))
        
        if not request or len(request) == 0:
            print(f"\nRequest ID {request_id} not found.")
            input("Press Enter to continue...")
            return
            
        request = dict(request[0])
        
        clear_screen()
        print(f"\n===== ACQUISITION REQUEST #{request['RequestID']} =====")
        print(f"Title: {request['Title']}")
        print(f"Author/Creator: {request['AuthorCreator']}")
        print(f"Publication Type: {request['PublicationType']}")
        print(f"Date Requested: {request['RequestDate']}")
        print(f"Requested By: {request['MemberName']}")
        print(f"Status: {request['Status']}")
        
        if request['StaffName']:
            print(f"Processed By: {request['StaffName']}")
            
        if request['Notes']:
            print(f"\nNotes: {request['Notes']}")
            
        if request['Status'] != 'Pending':
            print("\nThis request has already been processed.")
            input("Press Enter to continue...")
            return
            
        print("\nAction Options:")
        print("1. Approve Request")
        print("2. Reject Request")
        print("3. Add Notes")
        print("4. Go Back")
        
        action = input("\nEnter your choice (1-4): ")
        
        if action == '1' or action == '2':
            # Update request status
            new_status = 'Approved' if action == '1' else 'Rejected'
            notes = input("\nAdd any notes (optional): ")
            
            if not notes and request['Notes']:
                notes = request['Notes']
                
            update_query = """
            UPDATE AcquisitionRequest
            SET Status = ?, StaffID = ?, Notes = ?
            WHERE RequestID = ?
            """
            self.execute_query(
                update_query,
                (new_status, self.current_user['StaffID'], notes, request_id),
                fetch=False,
                commit=True
            )
            
            print(f"\nRequest has been {new_status.lower()}.")
            
        elif action == '3':
            # Add notes
            current_notes = request['Notes'] if request['Notes'] else ""
            print(f"Current notes: {current_notes}")
            
            new_notes = input("\nEnter additional notes: ")
            combined_notes = current_notes + "\n" + new_notes if current_notes else new_notes
            
            update_query = """
            UPDATE AcquisitionRequest
            SET Notes = ?
            WHERE RequestID = ?
            """
            self.execute_query(
                update_query,
                (combined_notes, request_id),
                fetch=False,
                commit=True
            )
            
            print("\nNotes have been updated.")
            
        input("\nPress Enter to continue...")
            
    def manage_volunteers(self):
        """Manage library volunteers (staff function)"""
        if self.user_type != "staff":
            return
            
        clear_screen()
        print("\n===== MANAGE LIBRARY VOLUNTEERS =====\n")
        
        print("1. View Active Volunteers")
        print("2. View All Volunteers")
        print("3. Return to Staff Menu")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '3':
            return
            
        if choice == '1':
            query = """
            SELECT v.VolunteerID, m.FirstName || ' ' || m.LastName as MemberName,
                   m.Email, m.Phone, v.SkillsInterests, v.AvailabilityHours, v.StartDate
            FROM Volunteer v
            JOIN Member m ON v.MemberID = m.MemberID
            WHERE v.Status = 'Active'
            ORDER BY v.StartDate DESC
            """
            title = "Active Volunteers"
            
        elif choice == '2':
            query = """
            SELECT v.VolunteerID, m.FirstName || ' ' || m.LastName as MemberName,
                   m.Email, m.Phone, v.SkillsInterests, v.Status, v.StartDate
            FROM Volunteer v
            JOIN Member m ON v.MemberID = m.MemberID
            ORDER BY v.Status, v.StartDate DESC
            """
            title = "All Volunteers"
            
        else:
            print("\nInvalid choice. Please try again.")
            input("Press Enter to continue...")
            return
            
        volunteers = self.execute_query(query)
        
        if not volunteers or len(volunteers) == 0:
            print(f"\nNo volunteers found.")
            input("Press Enter to continue...")
            return
            
        # Display volunteers
        if choice == '1':
            headers = ["ID", "Name", "Email", "Phone", "Skills/Interests", "Availability", "Start Date"]
        else:
            headers = ["ID", "Name", "Email", "Phone", "Skills/Interests", "Status", "Start Date"]
            
        table_data = []
        
        for vol in volunteers:
            if choice == '1':
                table_data.append([
                    vol['VolunteerID'],
                    vol['MemberName'],
                    vol['Email'],
                    vol['Phone'],
                    vol['SkillsInterests'][:30] + ('...' if len(vol['SkillsInterests']) > 30 else ''),
                    vol['AvailabilityHours'],
                    vol['StartDate']
                ])
            else:
                table_data.append([
                    vol['VolunteerID'],
                    vol['MemberName'],
                    vol['Email'],
                    vol['Phone'],
                    vol['SkillsInterests'][:30] + ('...' if len(vol['SkillsInterests']) > 30 else ''),
                    vol['Status'],
                    vol['StartDate']
                ])
        
        print(f"\n{title}:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Ask which volunteer to manage
        volunteer_id = input("\nEnter Volunteer ID to manage (or 0 to go back): ")
        
        if volunteer_id == '0':
            return
            
        # Get specific volunteer
        query = """
        SELECT v.*, m.FirstName || ' ' || m.LastName as MemberName, m.Email, m.Phone
        FROM Volunteer v
        JOIN Member m ON v.MemberID = m.MemberID
        WHERE v.VolunteerID = ?
        """
        volunteer = self.execute_query(query, (volunteer_id,))
        
        if not volunteer or len(volunteer) == 0:
            print(f"\nVolunteer ID {volunteer_id} not found.")
            input("Press Enter to continue...")
            return
            
        volunteer = dict(volunteer[0])
        
        clear_screen()
        print(f"\n===== VOLUNTEER DETAILS =====")
        print(f"Name: {volunteer['MemberName']}")
        print(f"Email: {volunteer['Email']}")
        print(f"Phone: {volunteer['Phone']}")
        print(f"Status: {volunteer['Status']}")
        print(f"Start Date: {volunteer['StartDate']}")
        print(f"Skills/Interests: {volunteer['SkillsInterests']}")
        print(f"Availability: {volunteer['AvailabilityHours']}")
        
        print("\nAction Options:")
        print("1. Update Status")
        print("2. Update Skills/Interests")
        print("3. Update Availability")
        print("4. Go Back")
        
        action = input("\nEnter your choice (1-4): ")
        
        if action == '1':
            # Update status
            current_status = volunteer['Status']
            new_status = 'Inactive' if current_status == 'Active' else 'Active'
            
            confirm = input(f"\nChange status from {current_status} to {new_status}? (y/n): ")
            
            if confirm.lower() == 'y':
                update_query = """
                UPDATE Volunteer
                SET Status = ?
                WHERE VolunteerID = ?
                """
                self.execute_query(
                    update_query,
                    (new_status, volunteer_id),
                    fetch=False,
                    commit=True
                )
                
                print(f"\nVolunteer status updated to: {new_status}")
                
        elif action == '2':
            # Update skills/interests
            print(f"Current Skills/Interests: {volunteer['SkillsInterests']}")
            new_skills = input("\nEnter new Skills/Interests: ")
            
            update_query = """
            UPDATE Volunteer
            SET SkillsInterests = ?
            WHERE VolunteerID = ?
            """
            self.execute_query(
                update_query,
                (new_skills, volunteer_id),
                fetch=False,
                commit=True
            )
            
            print("\nSkills/Interests updated successfully.")
            
        elif action == '3':
            # Update availability
            print(f"Current Availability: {volunteer['AvailabilityHours']}")
            new_availability = input("\nEnter new Availability: ")
            
            update_query = """
            UPDATE Volunteer
            SET AvailabilityHours = ?
            WHERE VolunteerID = ?
            """
            self.execute_query(
                update_query,
                (new_availability, volunteer_id),
                fetch=False,
                commit=True
            )
            
            print("\nAvailability updated successfully.")
            
        input("\nPress Enter to continue...")
            
    def manage_fines(self):
        """Manage library fines (staff function)"""
        if self.user_type != "staff":
            return
            
        clear_screen()
        print("\n===== MANAGE LIBRARY FINES =====\n")
        
        print("1. View Unpaid Fines")
        print("2. View All Fines")
        print("3. Search Fines by Member")
        print("4. Return to Staff Menu")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '4':
            return
            
        if choice == '1':
            query = """
            SELECT f.FineID, f.Amount, f.IssuedDate, f.Status,
                   m.FirstName || ' ' || m.LastName as MemberName, m.Email,
                   i.Title, b.DueDate, b.ReturnDate
            FROM Fine f
            JOIN Borrowing b ON f.BorrowID = b.BorrowID
            JOIN Member m ON b.MemberID = m.MemberID
            JOIN LibraryItem i ON b.ItemID = i.ItemID
            WHERE f.Status = 'Unpaid'
            ORDER BY f.IssuedDate
            """
            title = "Unpaid Fines"
            fines = self.execute_query(query)
            
        elif choice == '2':
            query = """
            SELECT f.FineID, f.Amount, f.IssuedDate, f.Status, f.PaidDate,
                   m.FirstName || ' ' || m.LastName as MemberName,
                   i.Title, b.DueDate, b.ReturnDate
            FROM Fine f
            JOIN Borrowing b ON f.BorrowID = b.BorrowID
            JOIN Member m ON b.MemberID = m.MemberID
            JOIN LibraryItem i ON b.ItemID = i.ItemID
            ORDER BY f.Status, f.IssuedDate DESC
            LIMIT 30
            """
            title = "All Fines (Last 30)"
            fines = self.execute_query(query)
            
        elif choice == '3':
            member_email = input("\nEnter member email: ")
            
            query = """
            SELECT f.FineID, f.Amount, f.IssuedDate, f.Status, f.PaidDate,
                   m.FirstName || ' ' || m.LastName as MemberName,
                   i.Title, b.DueDate, b.ReturnDate
            FROM Fine f
            JOIN Borrowing b ON f.BorrowID = b.BorrowID
            JOIN Member m ON b.MemberID = m.MemberID
            JOIN LibraryItem i ON b.ItemID = i.ItemID
            WHERE m.Email = ?
            ORDER BY f.Status, f.IssuedDate DESC
            """
            title = f"Fines for Member: {member_email}"
            fines = self.execute_query(query, (member_email,))
            
        else:
            print("\nInvalid choice. Please try again.")
            input("Press Enter to continue...")
            return
            
        if not fines or len(fines) == 0:
            print(f"\nNo fines found.")
            input("Press Enter to continue...")
            return
            
        # Display fines
        if choice == '1':
            headers = ["ID", "Amount", "Issued Date", "Member", "Item", "Due Date", "Return Date"]
        else:
            headers = ["ID", "Amount", "Issued Date", "Status", "Paid Date", "Member", "Item"]
            
        table_data = []
        total_unpaid = 0
        
        for fine in fines:
            if choice == '1':
                table_data.append([
                    fine['FineID'],
                    f"${fine['Amount']:.2f}",
                    fine['IssuedDate'],
                    fine['MemberName'],
                    fine['Title'],
                    fine['DueDate'],
                    fine['ReturnDate'] if fine['ReturnDate'] else 'Not returned'
                ])
                total_unpaid += fine['Amount']
            else:
                table_data.append([
                    fine['FineID'],
                    f"${fine['Amount']:.2f}",
                    fine['IssuedDate'],
                    fine['Status'],
                    fine['PaidDate'] if fine['PaidDate'] else 'N/A',
                    fine['MemberName'],
                    fine['Title']
                ])
                if fine['Status'] == 'Unpaid':
                    total_unpaid += fine['Amount']
        
        print(f"\n{title}:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        if choice == '1' or choice == '3':
            print(f"Total unpaid: ${total_unpaid:.2f}")
            
        # Ask which fine to manage
        fine_id = input("\nEnter Fine ID to process payment (or 0 to go back): ")
        
        if fine_id == '0':
            return
            
        # Get specific fine
        query = """
        SELECT f.*, m.FirstName || ' ' || m.LastName as MemberName, m.Email,
               i.Title, b.DueDate, b.ReturnDate
        FROM Fine f
        JOIN Borrowing b ON f.BorrowID = b.BorrowID
        JOIN Member m ON b.MemberID = m.MemberID
        JOIN LibraryItem i ON b.ItemID = i.ItemID
        WHERE f.FineID = ?
        """
        fine = self.execute_query(query, (fine_id,))
        
        if not fine or len(fine) == 0:
            print(f"\nFine ID {fine_id} not found.")
            input("Press Enter to continue...")
            return
            
        fine = dict(fine[0])
        
        if fine['Status'] == 'Paid':
            print(f"\nThis fine has already been paid on {fine['PaidDate']}.")
            input("Press Enter to continue...")
            return
            
        clear_screen()
        print(f"\n===== PROCESS FINE PAYMENT =====")
        print(f"Fine ID: {fine['FineID']}")
        print(f"Amount: ${fine['Amount']:.2f}")
        print(f"Issued Date: {fine['IssuedDate']}")
        print(f"Member: {fine['MemberName']} ({fine['Email']})")
        print(f"Item: {fine['Title']}")
        print(f"Due Date: {fine['DueDate']}")
        print(f"Return Date: {fine['ReturnDate']}")
        
        confirm = input("\nMark this fine as paid? (y/n): ")
        
        if confirm.lower() == 'y':
            paid_date = datetime.date.today()
            
            update_query = """
            UPDATE Fine
            SET Status = 'Paid', PaidDate = ?
            WHERE FineID = ?
            """
            self.execute_query(
                update_query,
                (paid_date, fine_id),
                fetch=False,
                commit=True
            )
            
            print(f"\nFine has been marked as paid on {paid_date}.")
            
        input("\nPress Enter to continue...")
        

def clear_screen():
    """Clear the terminal screen"""
    if os.name == 'nt':  # For Windows
        os.system('cls')
    else:  # For Mac and Linux
        os.system('clear')

def main():
    """Main function to run the library system"""
    # Create database connection
    library = LibrarySystem(DB_FILE)
    if not library.connect_db():
        print("Failed to connect to the database. Exiting...")
        sys.exit(1)
        
    # Main application loop
    while True:
        # If not logged in, show login screen
        if not library.current_user:
            login_result = library.login()
            
            if login_result == "exit":
                break
            elif not login_result:
                continue
                
        # Show appropriate menu based on user type
        if library.user_type == "member":
            library.member_menu()
        elif library.user_type == "staff":
            library.staff_menu()
            
    # Close database connection
    library.close_db()
    print("Thank you for using the Library Management System. Goodbye!")

if __name__ == "__main__":
    main()
