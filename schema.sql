-- Library Database Schema

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
