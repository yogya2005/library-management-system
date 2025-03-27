# Library Management System

A comprehensive SQLite-based library management system built with Python. This database system handles all aspects of a modern library, including collection management, member accounts, borrowing/returning, events, staff management, and more.

## Features

- **Collection Management**
  - Multiple item types (Books, E-books, Magazines, Journals, Media)
  - Search by title, author, type
  - Donation processing
  - Acquisition requests

- **Member Services**
  - Borrowing and returning items
  - Event registration
  - Fine management
  - Help request system
  - Volunteer registration

- **Staff Management**
  - Process returns
  - Manage help requests
  - Create and manage events
  - Process acquisition requests
  - Manage volunteers
  - Handle fines

## Database Structure

The system uses a relational database with the following main entities:
- Member
- Staff
- LibraryItem (with subtypes for different media)
- Event
- Room
- Borrowing
- Fine
- AcquisitionRequest
- EventAttendance
- Volunteer
- HelpRequest

## Requirements

- Python 3.6+
- SQLite 3
- tabulate package (`pip install tabulate`)

## Setup Instructions

1. Clone the repository or extract all files to a directory.

2. Install required Python packages:
   ```
   pip install tabulate
   ```

3. Run the initialization script to create the database and load sample data:
   ```
   python initialize-db.py
   ```
   This will create two SQL files (`schema.sql` and `sample_data.sql`) and initialize the database with sample data.

4. Run the main application:
   ```
   python library-app.py
   ```

## Sample Login Credentials

### Member Accounts
- Email: yogya1
  Password: password

- Email: yogya2
  Password: password

### Staff Accounts
- Email: admin
  (For demo purposes, staff logins only require the email)

- Email: bob.martinez@library.org
  (For demo purposes, staff logins only require the email)

## Database Design Considerations

The database was designed with the following principles in mind:

1. **Normalization**: The database design follows BCNF (Boyce-Codd Normal Form) principles to avoid anomalies.

2. **Inheritance**: Library items use a superclass-subclass model with a general `LibraryItem` table and specific subtypes.

3. **Constraints**: Key constraints, foreign key constraints, and check constraints ensure data integrity.

4. **Triggers**: Automated actions maintain database consistency (e.g., updating item status when borrowed).

5. **Indices**: Strategic indices improve query performance on frequently accessed fields.

## Usage Notes

- The system uses console-based user interface with menu navigation.
- Members can borrow items for 14 days; late returns automatically incur fines.
- Staff can manage all aspects of the library operation.
- The database comes pre-populated with sample data for testing.
