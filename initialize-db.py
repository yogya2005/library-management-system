#!/usr/bin/env python3
# Library Database Initialization Script - Fixed

import sqlite3
import os
import sys

DB_FILE = "library.db"

def initialize_database():
    """Initialize the library database with schema and sample data"""
    # Check if database already exists
    if os.path.exists(DB_FILE):
        confirm = input(f"Database file {DB_FILE} already exists. Overwrite? (y/n): ")
        if confirm.lower() != 'y':
            print("Database initialization cancelled.")
            return False
        os.remove(DB_FILE)
        
    print(f"Creating new database: {DB_FILE}")
    
    # Connect to database
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        print("Database connection established.")
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return False
    
    try:
        # Execute schema SQL
        print("Creating tables and relationships...")
        with open('schema.sql', 'r') as schema_file:
            schema_sql = schema_file.read()
            cursor.executescript(schema_sql)
        
        # Execute sample data SQL
        print("Loading sample data...")
        with open('sample_data.sql', 'r') as data_file:
            data_sql = data_file.read()
            cursor.executescript(data_sql)
        
        conn.commit()
        print("Database initialization completed successfully!")
        
        # Get some statistics
        cursor.execute("SELECT COUNT(*) FROM Member")
        member_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM LibraryItem")
        item_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Event")
        event_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Borrowing")
        borrow_count = cursor.fetchone()[0]
        
        print(f"\nDatabase Summary:")
        print(f"- Members: {member_count}")
        print(f"- Library Items: {item_count}")
        print(f"- Events: {event_count}")
        print(f"- Borrowing Records: {borrow_count}")
        
        # Close connection
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
        conn.close()
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        return False
    except IOError as e:
        print(f"Error reading SQL files: {e}")
        conn.close()
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        return False

def extract_schema_sql():
    """Extract schema to SQL file"""
    print("Extracting schema SQL file...")
    
    # Write schema SQL
    with open('schema.sql', 'w') as schema_file:
        schema_file.write(SCHEMA_SQL)
    print("Schema SQL written to schema.sql")

def extract_sample_data_sql():
    """Extract sample data to SQL file"""
    print("Extracting sample data SQL file...")
    
    # Write sample data SQL
    with open('sample_data.sql', 'w') as data_file:
        data_file.write(SAMPLE_DATA_SQL)
    print("Sample data SQL written to sample_data.sql")

# Schema SQL (from library-schema.sql)
SCHEMA_SQL = """-- Library Database Schema

-- Member table for library patrons
CREATE TABLE Member (
    MemberID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Phone TEXT,
    Address TEXT,
    MembershipDate DATE NOT NULL DEFAULT CURRENT_DATE,
    Password TEXT NOT NULL
);

-- Staff table for library employees
CREATE TABLE Staff (
    StaffID INTEGER PRIMARY KEY AUTOINCREMENT,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Position TEXT NOT NULL,
    Department TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Phone TEXT,
    HireDate DATE NOT NULL,
    Salary DECIMAL(10,2),
    Schedule TEXT
);

-- Room table for library spaces
CREATE TABLE Room (
    RoomID INTEGER PRIMARY KEY AUTOINCREMENT,
    RoomName TEXT NOT NULL,
    Capacity INTEGER NOT NULL,
    Location TEXT NOT NULL,
    Facilities TEXT,
    AvailabilityStatus TEXT CHECK (AvailabilityStatus IN ('Available', 'Booked', 'Maintenance')) DEFAULT 'Available'
);

-- Event table for library activities
CREATE TABLE Event (
    EventID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    Description TEXT,
    EventDate DATE NOT NULL,
    StartTime TEXT NOT NULL,
    EndTime TEXT NOT NULL,
    MaxAttendees INTEGER NOT NULL,
    EventType TEXT CHECK (EventType IN ('BookClub', 'ArtShow', 'Screening', 'Workshop', 'Other')),
    TargetAudience TEXT,
    StaffID INTEGER,
    RoomID INTEGER,
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID),
    FOREIGN KEY (RoomID) REFERENCES Room(RoomID),
    CHECK (EndTime > StartTime)
);

-- LibraryItem base table for all library materials
CREATE TABLE LibraryItem (
    ItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    PublicationDate DATE,
    Status TEXT CHECK (Status IN ('Available', 'Borrowed', 'Reserved', 'Maintenance')) DEFAULT 'Available',
    AcquisitionDate DATE DEFAULT CURRENT_DATE,
    Location TEXT,
    ItemType TEXT CHECK (ItemType IN ('Book', 'Ebook', 'Magazine', 'Journal', 'Media')) NOT NULL
);

-- Book table extending LibraryItem
CREATE TABLE Book (
    ItemID INTEGER PRIMARY KEY,
    ISBN TEXT UNIQUE,
    Author TEXT NOT NULL,
    Publisher TEXT,
    Genre TEXT,
    PageCount INTEGER,
    Format TEXT CHECK (Format IN ('Hardcover', 'Paperback', 'Other')),
    FOREIGN KEY (ItemID) REFERENCES LibraryItem(ItemID) ON DELETE CASCADE
);

-- Ebook table extending LibraryItem
CREATE TABLE Ebook (
    ItemID INTEGER PRIMARY KEY,
    ISBN TEXT UNIQUE,
    Author TEXT NOT NULL,
    Publisher TEXT,
    Genre TEXT,
    FileFormat TEXT,
    FileSize TEXT,
    FOREIGN KEY (ItemID) REFERENCES LibraryItem(ItemID) ON DELETE CASCADE
);

-- Magazine table extending LibraryItem
CREATE TABLE Magazine (
    ItemID INTEGER PRIMARY KEY,
    IssueNumber TEXT,
    Publisher TEXT,
    Category TEXT,
    Frequency TEXT,
    FOREIGN KEY (ItemID) REFERENCES LibraryItem(ItemID) ON DELETE CASCADE
);

-- Journal table extending LibraryItem
CREATE TABLE Journal (
    ItemID INTEGER PRIMARY KEY,
    Volume TEXT,
    Issue TEXT,
    Publisher TEXT,
    Field TEXT,
    PeerReviewed BOOLEAN,
    FOREIGN KEY (ItemID) REFERENCES LibraryItem(ItemID) ON DELETE CASCADE
);

-- Media table extending LibraryItem
CREATE TABLE Media (
    ItemID INTEGER PRIMARY KEY,
    MediaType TEXT CHECK (MediaType IN ('CD', 'DVD', 'Record', 'Other')),
    Artist TEXT,
    Runtime TEXT,
    Format TEXT,
    FOREIGN KEY (ItemID) REFERENCES LibraryItem(ItemID) ON DELETE CASCADE
);

-- Borrowing table for checkout transactions
CREATE TABLE Borrowing (
    BorrowID INTEGER PRIMARY KEY AUTOINCREMENT,
    MemberID INTEGER NOT NULL,
    ItemID INTEGER NOT NULL,
    BorrowDate DATE NOT NULL DEFAULT CURRENT_DATE,
    DueDate DATE NOT NULL,
    ReturnDate DATE,
    StaffID INTEGER,
    FOREIGN KEY (MemberID) REFERENCES Member(MemberID),
    FOREIGN KEY (ItemID) REFERENCES LibraryItem(ItemID),
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID),
    CHECK (ReturnDate IS NULL OR ReturnDate >= BorrowDate)
);

-- Fine table for late returns
CREATE TABLE Fine (
    FineID INTEGER PRIMARY KEY AUTOINCREMENT,
    BorrowID INTEGER UNIQUE NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    Status TEXT CHECK (Status IN ('Paid', 'Unpaid')) DEFAULT 'Unpaid',
    IssuedDate DATE NOT NULL DEFAULT CURRENT_DATE,
    PaidDate DATE,
    FOREIGN KEY (BorrowID) REFERENCES Borrowing(BorrowID),
    CHECK (PaidDate IS NULL OR PaidDate >= IssuedDate)
);

-- AcquisitionRequest table for requested items
CREATE TABLE AcquisitionRequest (
    RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT NOT NULL,
    AuthorCreator TEXT,
    PublicationType TEXT NOT NULL,
    RequestDate DATE NOT NULL DEFAULT CURRENT_DATE,
    Status TEXT CHECK (Status IN ('Pending', 'Approved', 'Rejected')) DEFAULT 'Pending',
    MemberID INTEGER,
    StaffID INTEGER,
    Notes TEXT,
    FOREIGN KEY (MemberID) REFERENCES Member(MemberID),
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID)
);

-- EventAttendance table for event registrations
CREATE TABLE EventAttendance (
    AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    EventID INTEGER NOT NULL,
    MemberID INTEGER NOT NULL,
    RegistrationDate DATE NOT NULL DEFAULT CURRENT_DATE,
    AttendanceStatus TEXT CHECK (AttendanceStatus IN ('Registered', 'Attended', 'Cancelled')) DEFAULT 'Registered',
    FOREIGN KEY (EventID) REFERENCES Event(EventID),
    FOREIGN KEY (MemberID) REFERENCES Member(MemberID),
    UNIQUE (EventID, MemberID)
);

-- Volunteer table for library volunteers
CREATE TABLE Volunteer (
    VolunteerID INTEGER PRIMARY KEY AUTOINCREMENT,
    MemberID INTEGER UNIQUE NOT NULL,
    SkillsInterests TEXT,
    AvailabilityHours TEXT,
    StartDate DATE NOT NULL DEFAULT CURRENT_DATE,
    Status TEXT CHECK (Status IN ('Active', 'Inactive')) DEFAULT 'Active',
    FOREIGN KEY (MemberID) REFERENCES Member(MemberID)
);

-- HelpRequest table for assistance requests
CREATE TABLE HelpRequest (
    RequestID INTEGER PRIMARY KEY AUTOINCREMENT,
    MemberID INTEGER NOT NULL,
    StaffID INTEGER,
    RequestDate DATE NOT NULL DEFAULT CURRENT_DATE,
    Description TEXT NOT NULL,
    Status TEXT CHECK (Status IN ('Open', 'InProgress', 'Resolved')) DEFAULT 'Open',
    Resolution TEXT,
    ClosedDate DATE,
    FOREIGN KEY (MemberID) REFERENCES Member(MemberID),
    FOREIGN KEY (StaffID) REFERENCES Staff(StaffID),
    CHECK (ClosedDate IS NULL OR ClosedDate >= RequestDate)
);

-- Triggers for data integrity

-- Update item status when borrowed
CREATE TRIGGER update_item_status_borrowed
AFTER INSERT ON Borrowing
BEGIN
    UPDATE LibraryItem
    SET Status = 'Borrowed'
    WHERE ItemID = NEW.ItemID AND NEW.ReturnDate IS NULL;
END;

-- Update item status when returned
CREATE TRIGGER update_item_status_returned
AFTER UPDATE ON Borrowing
WHEN NEW.ReturnDate IS NOT NULL AND OLD.ReturnDate IS NULL
BEGIN
    UPDATE LibraryItem
    SET Status = 'Available'
    WHERE ItemID = NEW.ItemID;
END;

-- Create fine when item is returned late
CREATE TRIGGER create_fine_for_late_return
AFTER UPDATE ON Borrowing
WHEN NEW.ReturnDate IS NOT NULL AND NEW.ReturnDate > NEW.DueDate
BEGIN
    INSERT INTO Fine (BorrowID, Amount, Status, IssuedDate)
    VALUES (
        NEW.BorrowID,
        -- $0.50 per day late
        (julianday(NEW.ReturnDate) - julianday(NEW.DueDate)) * 0.50,
        'Unpaid',
        NEW.ReturnDate
    );
END;

-- Check event capacity before registration
CREATE TRIGGER check_event_capacity
BEFORE INSERT ON EventAttendance
BEGIN
    SELECT CASE
        WHEN (
            SELECT COUNT(*) 
            FROM EventAttendance 
            WHERE EventID = NEW.EventID AND AttendanceStatus != 'Cancelled'
        ) >= (
            SELECT MaxAttendees 
            FROM Event 
            WHERE EventID = NEW.EventID
        )
        THEN RAISE(ABORT, 'Event has reached maximum capacity')
    END;
END;

-- Indices for performance
CREATE INDEX idx_libraryitem_status ON LibraryItem(Status);
CREATE INDEX idx_borrowing_member ON Borrowing(MemberID);
CREATE INDEX idx_borrowing_item ON Borrowing(ItemID);
CREATE INDEX idx_borrowing_dates ON Borrowing(BorrowDate, DueDate, ReturnDate);
CREATE INDEX idx_event_date ON Event(EventDate);
CREATE INDEX idx_fine_status ON Fine(Status);
"""

# Sample data SQL (from sample-data.sql)
SAMPLE_DATA_SQL = """-- Sample data for Library Database

-- Member data
INSERT INTO Member (FirstName, LastName, Email, Phone, Address, MembershipDate, Password) VALUES
    ('John', 'Doe', 'yogya1', '555-123-4567', '123 Main St, Anytown', '2025-01-15', 'password'),
    ('Jane', 'Smith', 'yogya2', '555-234-5678', '456 Oak Ave, Someville', '2025-02-20', 'password'),
    ('Robert', 'Johnson', 'robert.j@email.com', '555-345-6789', '789 Pine Rd, Otherburg', '2025-03-10', 'robert2025'),
    ('Emily', 'Williams', 'emily.w@email.com', '555-456-7890', '321 Elm St, Anycity', '2025-01-05', 'emilypass'),
    ('Michael', 'Brown', 'michael.b@email.com', '555-567-8901', '654 Maple Dr, Somewhere', '2025-04-12', 'brownm123'),
    ('Sarah', 'Davis', 'sarah.davis@email.com', '555-678-9012', '987 Cedar Ln, Anystate', '2025-02-28', 'davis2025'),
    ('David', 'Miller', 'david.m@email.com', '555-789-0123', '159 Walnut St, Sometown', '2025-03-22', 'millerd'),
    ('Jennifer', 'Wilson', 'jennifer.w@email.com', '555-890-1234', '753 Birch Ave, Othertown', '2025-05-05', 'wilson22'),
    ('James', 'Taylor', 'james.t@email.com', '555-901-2345', '852 Pine St, Anyville', '2025-01-30', 'taylormade'),
    ('Patricia', 'Anderson', 'patricia.a@email.com', '555-012-3456', '426 Oak Dr, Somecity', '2025-04-15', 'anderson123'),
    ('William', 'Thomas', 'william.t@email.com', '555-987-6543', '968 Maple Ave, Otherplace', '2025-02-14', 'thomas456'),
    ('Elizabeth', 'Jackson', 'elizabeth.j@email.com', '555-876-5432', '135 Cedar St, Anyland', '2025-05-20', 'jackson789');

-- Staff data
INSERT INTO Staff (FirstName, LastName, Position, Department, Email, Phone, HireDate, Salary, Schedule) VALUES
    ('Alice', 'Cooper', 'Head Librarian', 'Administration', 'admin', '555-111-2222', '2015-06-10', 75000.00, 'Mon-Fri 9AM-5PM'),
    ('Bob', 'Martinez', 'Assistant Librarian', 'Reference', 'bob.martinez@library.org', '555-222-3333', '2017-03-15', 55000.00, 'Tue-Sat 10AM-6PM'),
    ('Carol', 'Wong', 'Cataloging Specialist', 'Technical Services', 'carol.wong@library.org', '555-333-4444', '2018-09-22', 52000.00, 'Mon-Fri 8AM-4PM'),
    ('Daniel', 'Garcia', 'IT Specialist', 'Technology', 'daniel.garcia@library.org', '555-444-5555', '2019-11-05', 65000.00, 'Mon-Fri 9AM-5PM'),
    ('Emma', 'Chen', 'Children''s Librarian', 'Youth Services', 'emma.chen@library.org', '555-555-6666', '2016-07-18', 58000.00, 'Wed-Sun 9AM-5PM'),
    ('Frank', 'Robinson', 'Circulation Manager', 'Circulation', 'frank.robinson@library.org', '555-666-7777', '2014-04-30', 60000.00, 'Mon-Fri 8AM-4PM'),
    ('Grace', 'Kim', 'Events Coordinator', 'Community Outreach', 'grace.kim@library.org', '555-777-8888', '2020-01-15', 48000.00, 'Tue-Sat 10AM-6PM'),
    ('Henry', 'Patel', 'Reference Librarian', 'Reference', 'henry.patel@library.org', '555-888-9999', '2017-08-22', 53000.00, 'Wed-Sun 10AM-6PM'),
    ('Irene', 'Nguyen', 'Digital Resources Librarian', 'Technical Services', 'irene.nguyen@library.org', '555-999-0000', '2019-03-11', 56000.00, 'Mon-Fri 9AM-5PM'),
    ('Jack', 'Wilson', 'Maintenance Supervisor', 'Facilities', 'jack.wilson@library.org', '555-000-1111', '2015-10-05', 45000.00, 'Mon-Fri 7AM-3PM');

-- Room data
INSERT INTO Room (RoomName, Capacity, Location, Facilities, AvailabilityStatus) VALUES
    ('Main Conference Room', 50, 'First Floor East Wing', 'Projector, Sound System, Tables, Chairs', 'Available'),
    ('Study Room A', 10, 'Second Floor North', 'Whiteboard, Table, Chairs', 'Available'),
    ('Study Room B', 8, 'Second Floor North', 'Whiteboard, Table, Chairs', 'Available'),
    ('Community Hall', 100, 'Ground Floor Central', 'Stage, Sound System, Seating, Lighting', 'Available'),
    ('Children''s Activity Room', 30, 'First Floor West Wing', 'Child-sized Furniture, Art Supplies, Reading Corner', 'Available'),
    ('Tech Lab', 20, 'Second Floor South', 'Computers, Projector, Smart Board', 'Available'),
    ('Quiet Reading Room', 25, 'Third Floor East', 'Comfortable Seating, Reading Lamps', 'Available'),
    ('Media Room', 15, 'First Floor South Wing', 'TV, DVD Player, Sound System, Couches', 'Available'),
    ('Maker Space', 20, 'Basement Level', '3D Printers, Craft Supplies, Work Benches', 'Available'),
    ('Garden Pavilion', 40, 'Outdoor East Garden', 'Covered Area, Tables, Chairs, Power Outlets', 'Available');

-- LibraryItem and subtype data
-- Books
INSERT INTO LibraryItem (Title, PublicationDate, Status, AcquisitionDate, Location, ItemType) VALUES
    ('The Great Gatsby', '1925-04-10', 'Available', '2020-03-15', 'Fiction Section - Shelf 3A', 'Book'),
    ('To Kill a Mockingbird', '1960-07-11', 'Available', '2020-03-15', 'Fiction Section - Shelf 3B', 'Book'),
    ('1984', '1949-06-08', 'Available', '2020-04-10', 'Fiction Section - Shelf 4A', 'Book'),
    ('Pride and Prejudice', '1813-01-28', 'Available', '2020-05-20', 'Fiction Section - Shelf 2C', 'Book'),
    ('The Hobbit', '1937-09-21', 'Available', '2020-06-15', 'Fantasy Section - Shelf 1B', 'Book'),
    ('The Catcher in the Rye', '1951-07-16', 'Available', '2020-07-05', 'Fiction Section - Shelf 4B', 'Book'),
    ('The Lord of the Rings', '1954-07-29', 'Available', '2020-07-05', 'Fantasy Section - Shelf 1A', 'Book'),
    ('Harry Potter and the Philosopher''s Stone', '1997-06-26', 'Available', '2020-08-12', 'Children''s Section - Shelf 5D', 'Book'),
    ('The Da Vinci Code', '2003-03-18', 'Available', '2020-09-30', 'Mystery Section - Shelf 7C', 'Book'),
    ('The Alchemist', '1988-01-01', 'Available', '2020-10-15', 'Fiction Section - Shelf 3D', 'Book');

INSERT INTO Book (ItemID, ISBN, Author, Publisher, Genre, PageCount, Format) VALUES
    (1, '9780743273565', 'F. Scott Fitzgerald', 'Scribner', 'Classic Fiction', 180, 'Paperback'),
    (2, '9780061120084', 'Harper Lee', 'Harper Perennial', 'Classic Fiction', 336, 'Paperback'),
    (3, '9780451524935', 'George Orwell', 'Signet Classic', 'Dystopian Fiction', 328, 'Paperback'),
    (4, '9780141439518', 'Jane Austen', 'Penguin Classics', 'Classic Fiction', 480, 'Paperback'),
    (5, '9780547928227', 'J.R.R. Tolkien', 'Houghton Mifflin', 'Fantasy', 366, 'Hardcover'),
    (6, '9780316769488', 'J.D. Salinger', 'Little, Brown and Company', 'Coming-of-age Fiction', 277, 'Hardcover'),
    (7, '9780618640157', 'J.R.R. Tolkien', 'Houghton Mifflin', 'Fantasy', 1178, 'Hardcover'),
    (8, '9780590353427', 'J.K. Rowling', 'Scholastic', 'Fantasy', 320, 'Hardcover'),
    (9, '9780307474278', 'Dan Brown', 'Anchor', 'Mystery Thriller', 597, 'Paperback'),
    (10, '9780062315007', 'Paulo Coelho', 'HarperOne', 'Fiction', 208, 'Paperback');

-- E-books
INSERT INTO LibraryItem (Title, PublicationDate, Status, AcquisitionDate, Location, ItemType) VALUES
    ('Digital Fortress', '1998-01-01', 'Available', '2021-01-10', 'Digital Collection', 'Ebook'),
    ('The Hunger Games', '2008-09-14', 'Available', '2021-01-15', 'Digital Collection', 'Ebook'),
    ('The Girl with the Dragon Tattoo', '2005-08-01', 'Available', '2021-02-20', 'Digital Collection', 'Ebook'),
    ('Gone Girl', '2012-06-05', 'Available', '2021-03-10', 'Digital Collection', 'Ebook'),
    ('The Martian', '2011-09-27', 'Available', '2021-04-05', 'Digital Collection', 'Ebook'),
    ('Ready Player One', '2011-08-16', 'Available', '2021-05-12', 'Digital Collection', 'Ebook'),
    ('The Silent Patient', '2019-02-05', 'Available', '2021-06-15', 'Digital Collection', 'Ebook'),
    ('Where the Crawdads Sing', '2018-08-14', 'Available', '2021-07-20', 'Digital Collection', 'Ebook'),
    ('Educated', '2018-02-20', 'Available', '2021-08-25', 'Digital Collection', 'Ebook'),
    ('Becoming', '2018-11-13', 'Available', '2021-09-30', 'Digital Collection', 'Ebook');

INSERT INTO Ebook (ItemID, ISBN, Author, Publisher, Genre, FileFormat, FileSize) VALUES
    (11, '9780312944926', 'Dan Brown', 'St. Martin''s Press', 'Techno-thriller', 'EPUB', '2.3 MB'),
    (12, '9780439023481', 'Suzanne Collins', 'Scholastic Press', 'Dystopian Fiction', 'EPUB', '3.1 MB'),
    (13, '9780307949486', 'Stieg Larsson', 'Knopf', 'Crime Thriller', 'EPUB', '4.2 MB'),
    (14, '9780307588371', 'Gillian Flynn', 'Crown Publishing', 'Psychological Thriller', 'EPUB', '2.8 MB'),
    (15, '9780553418026', 'Andy Weir', 'Crown Publishing', 'Science Fiction', 'EPUB', '3.5 MB'),
    (16, '9780307887436', 'Ernest Cline', 'Random House', 'Science Fiction', 'EPUB', '3.2 MB'),
    (17, '9781250301697', 'Alex Michaelides', 'Celadon Books', 'Psychological Thriller', 'EPUB', '2.7 MB'),
    (18, '9780735219090', 'Delia Owens', 'G.P. Putnam''s Sons', 'Literary Fiction', 'EPUB', '3.6 MB'),
    (19, '9780399590504', 'Tara Westover', 'Random House', 'Memoir', 'EPUB', '3.8 MB'),
    (20, '9781524763138', 'Michelle Obama', 'Crown Publishing', 'Autobiography', 'EPUB', '4.5 MB');

-- Magazines
INSERT INTO LibraryItem (Title, PublicationDate, Status, AcquisitionDate, Location, ItemType) VALUES
    ('National Geographic - March 2025', '2025-03-01', 'Available', '2025-03-05', 'Periodicals Section - Rack A', 'Magazine'),
    ('Time - April 2025', '2025-04-01', 'Available', '2025-04-05', 'Periodicals Section - Rack A', 'Magazine'),
    ('Scientific American - February 2025', '2025-02-01', 'Available', '2025-02-10', 'Periodicals Section - Rack B', 'Magazine'),
    ('The Economist - May 2025', '2025-05-01', 'Available', '2025-05-08', 'Periodicals Section - Rack B', 'Magazine'),
    ('Wired - June 2025', '2025-06-01', 'Available', '2025-06-07', 'Periodicals Section - Rack C', 'Magazine'),
    ('Vogue - July 2025', '2025-07-01', 'Available', '2025-07-05', 'Periodicals Section - Rack C', 'Magazine'),
    ('Sports Illustrated - March 2025', '2025-03-01', 'Available', '2025-03-12', 'Periodicals Section - Rack D', 'Magazine'),
    ('New Yorker - April 2025', '2025-04-01', 'Available', '2025-04-08', 'Periodicals Section - Rack D', 'Magazine'),
    ('Popular Science - May 2025', '2025-05-01', 'Available', '2025-05-10', 'Periodicals Section - Rack A', 'Magazine'),
    ('Forbes - June 2025', '2025-06-01', 'Available', '2025-06-09', 'Periodicals Section - Rack B', 'Magazine');

INSERT INTO Magazine (ItemID, IssueNumber, Publisher, Category, Frequency) VALUES
    (21, 'Vol. 243 No. 3', 'National Geographic Society', 'Science & Nature', 'Monthly'),
    (22, 'Vol. 201 No. 13', 'Time USA, LLC', 'News & Current Affairs', 'Weekly'),
    (23, 'Vol. 328 No. 2', 'Springer Nature', 'Science', 'Monthly'),
    (24, 'Vol. 446 No. 9347', 'The Economist Group', 'Business & Finance', 'Weekly'),
    (25, 'Vol. 31 No. 6', 'Condé Nast', 'Technology', 'Monthly'),
    (26, 'Vol. 213 No. 7', 'Condé Nast', 'Fashion', 'Monthly'),
    (27, 'Vol. 138 No. 3', 'Maven Coalition', 'Sports', 'Monthly'),
    (28, 'Vol. 99 No. 8', 'Condé Nast', 'Literature & Culture', 'Weekly'),
    (29, 'Vol. 305 No. 5', 'Bonnier Corporation', 'Science & Technology', 'Monthly'),
    (30, 'Vol. 206 No. 6', 'Forbes Media', 'Business & Finance', 'Monthly');

-- Journals
INSERT INTO LibraryItem (Title, PublicationDate, Status, AcquisitionDate, Location, ItemType) VALUES
    ('Nature - January 2025', '2025-01-05', 'Available', '2025-01-15', 'Academic Journals - Section J1', 'Journal'),
    ('The Lancet - February 2025', '2025-02-10', 'Available', '2025-02-20', 'Academic Journals - Section J2', 'Journal'),
    ('Journal of the American Medical Association - March 2025', '2025-03-07', 'Available', '2025-03-15', 'Academic Journals - Section J2', 'Journal'),
    ('IEEE Transactions on Pattern Analysis - April 2025', '2025-04-15', 'Available', '2025-04-25', 'Academic Journals - Section J3', 'Journal'),
    ('Journal of Financial Economics - May 2025', '2025-05-01', 'Available', '2025-05-10', 'Academic Journals - Section J4', 'Journal'),
    ('Psychological Review - March 2025', '2025-03-01', 'Available', '2025-03-10', 'Academic Journals - Section J5', 'Journal'),
    ('Cell - April 2025', '2025-04-05', 'Available', '2025-04-15', 'Academic Journals - Section J1', 'Journal'),
    ('The Astrophysical Journal - May 2025', '2025-05-15', 'Available', '2025-05-25', 'Academic Journals - Section J6', 'Journal'),
    ('American Economic Review - June 2025', '2025-06-01', 'Available', '2025-06-10', 'Academic Journals - Section J4', 'Journal'),
    ('Journal of Personality and Social Psychology - July 2025', '2025-07-01', 'Available', '2025-07-10', 'Academic Journals - Section J5', 'Journal');

INSERT INTO Journal (ItemID, Volume, Issue, Publisher, Field, PeerReviewed) VALUES
    (31, 'Vol. 613', 'Issue 7945', 'Springer Nature', 'Multidisciplinary Science', 1),
    (32, 'Vol. 401', 'Issue 10375', 'Elsevier', 'Medicine', 1),
    (33, 'Vol. 329', 'Issue 9', 'American Medical Association', 'Medicine', 1),
    (34, 'Vol. 45', 'Issue 4', 'IEEE', 'Computer Science', 1),
    (35, 'Vol. 148', 'Issue 2', 'Elsevier', 'Economics & Finance', 1),
    (36, 'Vol. 130', 'Issue 2', 'American Psychological Association', 'Psychology', 1),
    (37, 'Vol. 186', 'Issue 7', 'Cell Press', 'Biology', 1),
    (38, 'Vol. 947', 'Issue 1', 'American Astronomical Society', 'Astronomy & Astrophysics', 1),
    (39, 'Vol. 113', 'Issue 6', 'American Economic Association', 'Economics', 1),
    (40, 'Vol. 124', 'Issue 7', 'American Psychological Association', 'Psychology', 1);

-- Media items
INSERT INTO LibraryItem (Title, PublicationDate, Status, AcquisitionDate, Location, ItemType) VALUES
    ('The Beatles - Abbey Road', '1969-09-26', 'Available', '2020-11-15', 'Music Collection - Section M1', 'Media'),
    ('Star Wars: Episode IV - A New Hope', '1977-05-25', 'Available', '2020-12-10', 'Film Collection - Section F2', 'Media'),
    ('The Queen''s Gambit', '2020-10-23', 'Available', '2021-02-10', 'TV Series Collection - Section T3', 'Media'),
    ('Pink Floyd - The Dark Side of the Moon', '1973-03-01', 'Available', '2021-03-05', 'Music Collection - Section M1', 'Media'),
    ('Inception', '2010-07-16', 'Available', '2021-04-20', 'Film Collection - Section F3', 'Media'),
    ('Breaking Bad - Complete Series', '2008-01-20', 'Available', '2021-05-15', 'TV Series Collection - Section T1', 'Media'),
    ('Miles Davis - Kind of Blue', '1959-08-17', 'Available', '2021-06-25', 'Music Collection - Section M2', 'Media'),
    ('The Lord of the Rings Trilogy', '2001-12-19', 'Available', '2021-07-30', 'Film Collection - Section F1', 'Media'),
    ('Game of Thrones - Season 1', '2011-04-17', 'Available', '2021-08-20', 'TV Series Collection - Section T2', 'Media'),
    ('Fleetwood Mac - Rumours', '1977-02-04', 'Available', '2021-09-10', 'Music Collection - Section M1', 'Media');

INSERT INTO Media (ItemID, MediaType, Artist, Runtime, Format) VALUES
    (41, 'Record', 'The Beatles', '47 minutes', 'Vinyl LP'),
    (42, 'DVD', 'George Lucas', '121 minutes', 'DVD'),
    (43, 'DVD', 'Scott Frank', '395 minutes', 'DVD Box Set'),
    (44, 'CD', 'Pink Floyd', '43 minutes', 'Audio CD'),
    (45, 'DVD', 'Christopher Nolan', '148 minutes', 'DVD'),
    (46, 'DVD', 'Vince Gilligan', '3120 minutes', 'DVD Box Set'),
    (47, 'Record', 'Miles Davis', '45 minutes', 'Vinyl LP'),
    (48, 'DVD', 'Peter Jackson', '558 minutes', 'DVD Box Set'),
    (49, 'DVD', 'David Benioff, D.B. Weiss', '600 minutes', 'DVD Box Set'),
    (50, 'CD', 'Fleetwood Mac', '40 minutes', 'Audio CD');

-- Events
INSERT INTO Event (Title, Description, EventDate, StartTime, EndTime, MaxAttendees, EventType, TargetAudience, StaffID, RoomID) VALUES
    ('Summer Reading Kickoff', 'Join us for the kickoff of our summer reading program with activities and refreshments.', '2025-06-15', '14:00', '16:00', 50, 'Workshop', 'All Ages', 5, 4),
    ('Book Club: "The Midnight Library"', 'Monthly book club discussing Matt Haig''s "The Midnight Library".', '2025-05-20', '18:30', '20:00', 15, 'BookClub', 'Adults', 2, 2),
    ('Film Screening: Citizen Kane', 'Classic film screening with brief discussion afterward.', '2025-05-25', '19:00', '21:30', 30, 'Screening', 'Adults', 7, 8),
    ('Storytime for Toddlers', 'Weekly storytime session for children ages 2-5.', '2025-05-18', '10:00', '11:00', 20, 'Workshop', 'Children', 5, 5),
    ('Introduction to 3D Printing', 'Learn the basics of 3D printing and design your first model.', '2025-06-01', '15:00', '17:00', 15, 'Workshop', 'Teens & Adults', 4, 9),
    ('Local Author Showcase', 'Meet local authors and hear readings from their work.', '2025-06-10', '14:00', '16:00', 40, 'Other', 'All Ages', 7, 4),
    ('Poetry Reading Night', 'Open mic poetry reading for local poets.', '2025-05-28', '18:00', '20:00', 30, 'Other', 'Adults', 8, 7),
    ('Digital Resources Workshop', 'Learn how to use the library''s digital resources and e-book services.', '2025-06-05', '10:00', '12:00', 20, 'Workshop', 'Adults & Seniors', 9, 6),
    ('Art Exhibition Opening: Local Landscapes', 'Opening reception for new art exhibition featuring local landscape paintings.', '2025-06-20', '17:00', '19:00', 50, 'ArtShow', 'All Ages', 7, 4),
    ('Science Club for Kids', 'Fun science experiments and learning for children ages 8-12.', '2025-05-27', '13:00', '14:30', 25, 'Workshop', 'Children', 5, 5);

-- Borrowing records
INSERT INTO Borrowing (MemberID, ItemID, BorrowDate, DueDate, ReturnDate, StaffID) VALUES
    (1, 1, '2025-04-10', '2025-04-24', '2025-04-22', 6),
    (2, 5, '2025-04-15', '2025-04-29', '2025-04-28', 6),
    (3, 9, '2025-04-18', '2025-05-02', '2025-05-01', 6),
    (4, 12, '2025-04-20', '2025-05-04', NULL, 6),
    (5, 42, '2025-04-25', '2025-05-09', '2025-05-08', 6),
    (6, 3, '2025-04-28', '2025-05-12', NULL, 6),
    (7, 50, '2025-05-01', '2025-05-15', NULL, 6),
    (8, 22, '2025-05-05', '2025-05-19', '2025-05-10', 6),
    (9, 45, '2025-05-08', '2025-05-22', NULL, 6),
    (10, 35, '2025-05-10', '2025-05-24', NULL, 6),
    (1, 7, '2025-05-12', '2025-05-26', NULL, 6),
    (2, 15, '2025-05-15', '2025-05-29', NULL, 6);

-- Manual creation of a fine (for a returned item)
INSERT INTO Fine (BorrowID, Amount, Status, IssuedDate, PaidDate) VALUES
    (3, 2.50, 'Unpaid', '2025-05-01', NULL);

-- EventAttendance records
INSERT INTO EventAttendance (EventID, MemberID, RegistrationDate, AttendanceStatus) VALUES
    (1, 1, '2025-05-20', 'Registered'),
    (1, 4, '2025-05-21', 'Registered'),
    (1, 6, '2025-05-22', 'Registered'),
    (2, 2, '2025-05-10', 'Registered'),
    (2, 8, '2025-05-12', 'Registered'),
    (3, 3, '2025-05-15', 'Registered'),
    (3, 9, '2025-05-16', 'Registered'),
    (3, 11, '2025-05-17', 'Registered'),
    (4, 5, '2025-05-10', 'Registered'),
    (5, 7, '2025-05-20', 'Registered'),
    (6, 10, '2025-05-25', 'Registered'),
    (7, 2, '2025-05-20', 'Registered');

-- AcquisitionRequest records
INSERT INTO AcquisitionRequest (Title, AuthorCreator, PublicationType, RequestDate, Status, MemberID, StaffID, Notes) VALUES
    ('Cloud Atlas', 'David Mitchell', 'Book', '2025-05-10', 'Pending', 3, NULL, 'Multiple member requests for this title'),
    ('Educated: A Memoir', 'Tara Westover', 'Book', '2025-05-12', 'Approved', 5, 2, 'Approved for next acquisition batch'),
    ('National Geographic - Special Edition on Climate Change', 'National Geographic', 'Magazine', '2025-05-15', 'Pending', 8, NULL, 'Special issue requested for reference collection'),
    ('The Queen''s Gambit - 4K Edition', 'Scott Frank', 'Media', '2025-05-18', 'Rejected', 4, 7, 'Already have standard edition; limited budget for duplicates'),
    ('Journal of Artificial Intelligence Research - 2025 Issues', 'AI Research Association', 'Journal', '2025-05-20', 'Approved', 9, 2, 'Will add to digital subscription'),
    ('The Lincoln Highway', 'Amor Towles', 'Book', '2025-05-22', 'Pending', 6, NULL, 'Recent bestseller'),
    ('Bluey - Season 1', 'Joe Brumm', 'Media', '2025-05-23', 'Approved', 5, 7, 'Popular children''s content'),
    ('Scientific Python: A Complete Guide', 'John Smith', 'Book', '2025-05-25', 'Pending', 7, NULL, 'Requested for technical collection'),
    ('The Paris Review - Complete Archive', 'Various', 'Journal', '2025-05-26', 'Rejected', 2, 2, 'Beyond current budget constraints'),
    ('Local History Oral Recordings', 'Community History Project', 'Media', '2025-05-28', 'Approved', 10, 1, 'Important local history preservation');

-- Volunteer records
INSERT INTO Volunteer (MemberID, SkillsInterests, AvailabilityHours, StartDate, Status) VALUES
    (3, 'Reading to children, Event organization', 'Weekends, 10AM-2PM', '2025-03-15', 'Active'),
    (5, 'Computer skills, Cataloging', 'Monday/Wednesday, 1PM-5PM', '2025-04-10', 'Active'),
    (8, 'ESL tutoring, Translation (Spanish)', 'Tuesday/Thursday, 6PM-8PM', '2025-02-20', 'Active'),
    (11, 'Book repair, Collection maintenance', 'Friday, 9AM-12PM', '2025-01-05', 'Active'),
    (7, 'Event setup, General assistance', 'Weekends, 12PM-4PM', '2025-05-01', 'Active'),
    (1, 'Digital literacy teaching, Senior assistance', 'Monday/Friday, 2PM-4PM', '2025-03-10', 'Inactive'),
    (12, 'Art workshop instruction, Display creation', 'Wednesday, 3PM-6PM', '2025-04-20', 'Active'),
    (6, 'Book sorting, Shelving', 'Tuesday/Thursday, 10AM-1PM', '2025-02-15', 'Active'),
    (9, 'Technical support, Equipment training', 'Friday, 1PM-5PM', '2025-05-15', 'Active'),
    (4, 'Reading group facilitation, Book discussion', 'Monday, 6PM-8PM', '2025-01-20', 'Inactive');

-- HelpRequest records
INSERT INTO HelpRequest (MemberID, StaffID, RequestDate, Description, Status, Resolution, ClosedDate) VALUES
    (2, 8, '2025-05-10', 'Need help finding resources on renewable energy for research paper', 'Resolved', 'Provided list of books and journals, plus access to specialized database', '2025-05-10'),
    (4, 5, '2025-05-12', 'Looking for recommendations for 8-year-old reluctant reader', 'Resolved', 'Recommended graphic novels and adventure series with demonstration of digital options', '2025-05-12'),
    (7, 4, '2025-05-15', 'Having trouble accessing e-books on tablet', 'Resolved', 'Helped install and configure app, demonstrated usage', '2025-05-15'),
    (9, 2, '2025-05-18', 'Need research assistance for historical project on local area', 'InProgress', NULL, NULL),
    (1, 6, '2025-05-20', 'Question about borrowing limits and extension policies', 'Resolved', 'Explained policies and demonstrated online renewal process', '2025-05-20'),
    (10, 9, '2025-05-22', 'Need help with database searches for academic journal articles', 'Resolved', 'Provided tutorial on advanced search techniques', '2025-05-22'),
    (6, 8, '2025-05-23', 'Looking for poetry collections for middle school students', 'Resolved', 'Created curated list of age-appropriate collections', '2025-05-23'),
    (3, 5, '2025-05-25', 'Need recommendations for book club selection', 'Open', NULL, NULL),
    (5, 7, '2025-05-26', 'Requesting information about upcoming events for seniors', 'Resolved', 'Provided calendar and added to email notification list', '2025-05-26'),
    (8, 3, '2025-05-28', 'Need assistance with citation formatting for research paper', 'InProgress', NULL, NULL);
"""

def main():
    """Main function"""
    extract_schema_sql()
    extract_sample_data_sql()
    initialize_database()

if __name__ == "__main__":
    main()