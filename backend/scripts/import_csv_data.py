"""
Import CSV data into Neon PostgreSQL database - FAST VERSION
"""
import os
import sys
import csv
import psycopg
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Update with new DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

def create_sales_table(conn):
    """Create the sales table"""
    create_table_sql = """
    DROP TABLE IF EXISTS ttd_sales_data CASCADE;
    
    CREATE TABLE ttd_sales_data (
        id SERIAL PRIMARY KEY,
        OrderDate VARCHAR(50),
        Store_ID VARCHAR(50),
        Category VARCHAR(100),
        City VARCHAR(100),
        Country VARCHAR(100),
        CustomerName VARCHAR(200),
        Discount DECIMAL(5,2),
        OrderID VARCHAR(100),
        PostalCode VARCHAR(20),
        ProductName TEXT,
        Profit DECIMAL(15,2),
        Quantity INTEGER,
        Region VARCHAR(100),
        Sales DECIMAL(15,2),
        Segment VARCHAR(100),
        ShipDate VARCHAR(50),
        ShipMode VARCHAR(100),
        State VARCHAR(100),
        Sub_Category VARCHAR(100),
        DaystoShipActual INTEGER,
        SalesForecast DECIMAL(15,2),
        ShipStatus VARCHAR(100),
        DaystoShipScheduled INTEGER,
        SalesperCustomer DECIMAL(15,2),
        ProfitRatio DECIMAL(10,2),
        latitude DECIMAL(10,6),
        longitude DECIMAL(10,6)
    );
    """
    
    with conn.cursor() as cur:
        cur.execute(create_table_sql)
        conn.commit()
        print("✓ Table created successfully")

def import_csv_data_fast(conn, csv_file_path):
    """Import data from CSV using COPY (fastest method)"""
    with conn.cursor() as cur:
        # Read CSV and prepare for COPY
        print("  Reading CSV file...")
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            # Skip header
            next(f)
            
            # Use COPY command for ultra-fast import
            with cur.copy("""
                COPY ttd_sales_data (
                    OrderDate, Store_ID, Category, City, Country, CustomerName,
                    Discount, OrderID, PostalCode, ProductName, Profit, Quantity,
                    Region, Sales, Segment, ShipDate, ShipMode, State, Sub_Category,
                    DaystoShipActual, SalesForecast, ShipStatus, DaystoShipScheduled,
                    SalesperCustomer, ProfitRatio, latitude, longitude
                ) FROM STDIN WITH (FORMAT CSV)
            """) as copy:
                for line in f:
                    copy.write(line)
        
        conn.commit()
        
        # Get count
        cur.execute("SELECT COUNT(*) FROM ttd_sales_data")
        count = cur.fetchone()[0]
        print(f"✓ Imported {count} total rows")

def main():
    """Main function"""
    print("=" * 60)
    print("Importing CSV Data into Neon PostgreSQL (FAST)")
    print("=" * 60)
    print()
    
    # Determine CSV file path
    # Check if we are in backend folder or root
    potential_paths = [
        "ttdsalesdata.csv",
        os.path.join("backend", "ttdsalesdata.csv"),
        os.path.join("..", "ttdsalesdata.csv")
    ]
    
    csv_file = None
    for path in potential_paths:
        if os.path.exists(path):
            csv_file = path
            break
            
    if not csv_file:
        print(f"✗ CSV file 'ttdsalesdata.csv' not found in current directory or backend/")
        sys.exit(1)
        
    print(f"Using CSV file: {csv_file}")
    
    if not DATABASE_URL:
        print("✗ DATABASE_URL not found in .env")
        sys.exit(1)
    
    try:
        # Connect to database
        print("1. Connecting to database...")
        conn = psycopg.connect(DATABASE_URL)
        print("✓ Connected to database")
        print()
        
        # Create table
        print("2. Creating table...")
        create_sales_table(conn)
        print()
        
        # Import data
        print("3. Importing CSV data (this should take <10 seconds)...")
        import_csv_data_fast(conn, csv_file)
        print()
        
        # Verify data
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM ttd_sales_data")
            count = cur.fetchone()[0]
            print(f"✓ Verification: {count} rows in database")
            
            # Show sample data
            cur.execute("SELECT * FROM ttd_sales_data LIMIT 3")
            print("\nSample rows:")
            for row in cur.fetchall():
                # Adjust indices based on table structure
                # id=0, OrderDate=1 ... CustomerName=6 ... Sales=14
                print(f"  Order: {row[8]}, Customer: {row[6]}, Sales: ${row[14]}")
        
        conn.close()
        
        print()
        print("=" * 60)
        print("✓ Import Complete!")
        print("=" * 60)
        print()
        print("Table: ttd_sales_data")
        print(f"Rows: {count}")
        print()
        print("Next step: Run 'python backend/scripts/initialize_embeddings.py'")
        print()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
