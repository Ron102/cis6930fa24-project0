import argparse
import re
import tempfile
#import project0
import urllib.request
import sqlite3
import os
import tempfile
import configparser
from importlib import resources
import pypdf
from pypdf import PdfReader


def main(url):
    incident_data = fetchincidents(url)
    incidents = extractincidents(incident_data)

    db = createdb()

    populatedb(db, incidents)

    status(db)



def fetchincidents(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}
        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request) as response:
            pdf_data = response.read()

        with open("downloaded_file.pdf", "wb") as f:
            f.write(pdf_data)

    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}. The requested URL was: {url}")
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}. The requested URL was: {url}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")




def extractincidents(pdf_path):
    reader = PdfReader("downloaded_file.pdf")
    lines = []
    final_lines = []

    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text(extraction_mode="layout", layout_mode_space_vertically=False)
        lines.append(text)


    for i in lines:
        final_lines.append(i.split("\n"))
        

    flat_list = [item for sublist in final_lines for item in sublist]
    flat_list = [s for s in flat_list if s.strip() != "NORMAN POLICE DEPARTMENT"]
    flat_list = [s for s in flat_list if s.strip() != "Daily Incident Summary (Public)"]
    flat_list = [s for s in flat_list if "Date / Time" not in s]

    
    flat_list.pop()

    return flat_list



def createdb():
    resources_dir = 'resources'
    os.makedirs(resources_dir, exist_ok=True)
    db_file_path = os.path.join(resources_dir, 'normanpd.db')
    con = sqlite3.connect(db_file_path)
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS incidents")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS incidents (
    incident_time TEXT,
    incident_number TEXT,
    incident_location TEXT,
    nature TEXT,
    incident_ori TEXT
);
    """)

    con.commit()
    return db_file_path



def populatedb(db_path, incidents):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for line in incidents:
        fields = re.split(r'\s{2,}', line)
        if len(fields) != 5:
            print(f"Data format incorrect for: {line}")
            continue

        date_time, incident_number, location, nature, incident_ori = fields

        values = (date_time.strip(), incident_number.strip(), location.strip(), nature.strip(), incident_ori.strip())

        try:
            cursor.execute(''' 
            INSERT INTO incidents ("incident_time", "incident_number", "incident_location", "nature", "incident_ori")
            VALUES (?, ?, ?, ?, ?)
            ''', values)
        except sqlite3.Error as e:
            print(f"Error inserting row: {e}")

    conn.commit()
    conn.close()


def status(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = '''
    SELECT nature, COUNT(*) as count 
    FROM incidents 
    GROUP BY nature
    ORDER BY nature ASC
    '''
    
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            nature, count = row
            print(f"{nature}|{count}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        conn.close()




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                         help="Incident summary url.")
     
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)
