import pytest
import os
from io import StringIO
import sqlite3
import sys
from unittest import mock
from project0.main import main, fetchincidents, extractincidents, createdb, populatedb, status
from unittest.mock import patch, mock_open, MagicMock



def test_fetchincidents(mocker):
    test_url = "https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-02_daily_incident_summary.pdf"  
    expected_path = "downloaded_file.pdf"

    mock_response = mock.Mock()
    mock_response.read.return_value = b"%PDF-1.4\n1 0 obj\n<< /Type /Page /MediaBox [0 0 612 792] >>\nendobj\n"
    
    mocker.patch('urllib.request.urlopen', return_value=mock_response)

    fetchincidents(test_url)

    assert os.path.exists(expected_path)



@patch('project0.main.PdfReader')  
def test_extractincidents(mock_pdf_reader):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = (
        "NORMAN POLICE DEPARTMENT\n"
        "Daily Incident Summary (Public)\n"
        "Date / Time             Incident Number   Location   Nature  Incident ORI\n"
        "08/15/2024  15:30      2024-0001      Main Street   Theft    OK0140200\n"
        "08/16/2024  10:45      2024-0002      2nd Avenue    Burglary OK0140200\n"
        "Some other content\n"
    )

    mock_pdf_reader.return_value.pages = [mock_page]  

    result = extractincidents('downloaded_file.pdf')

    expected_result = [
        "08/15/2024  15:30      2024-0001      Main Street   Theft    OK0140200",
        "08/16/2024  10:45      2024-0002      2nd Avenue    Burglary OK0140200",
        "Some other content"
    ]

    assert result == expected_result, "Extracted text does not match expected output."



def test_createdb():
    db_file_path = createdb()

    assert os.path.exists(db_file_path), "Database file not created."

    con = sqlite3.connect(db_file_path)
    cur = con.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='incidents';")
    table_exists = cur.fetchone()

    assert table_exists is not None, "'incidents' table not created."

    con.close()



def test_populatedb():
    db_path = createdb()  

    incidents = [
        "09/15/2024 10:30   2024-00011501   201 REED AVE   Traffic Accident   OK0140200"
    ]

    populatedb(db_path, incidents)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM incidents")
    rows = cursor.fetchall()

    assert len(rows) == 1, f"Expected 1 row but got {len(rows)}. Rows: {rows}"

    expected_data = [
        ("09/15/2024 10:30", "2024-00011501", "201 REED AVE", "Traffic Accident", "OK0140200")
    ]

    for row, expected in zip(rows, expected_data):
        assert row == expected, f"Expected {expected} but got {row}"

    conn.close()




def test_status():
    db_path = createdb()

    incidents = [
        "8/2/2024 12:47   2024-00055815   426 S PONCA AVE   Animal Complaint   OK0140200",
        "8/2/2024 16:44   2024-00055898   1621 W BOYD ST   Animal Complaint   OK0140200"
    ]

    populatedb(db_path, incidents)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM incidents")
    rows = cursor.fetchall()
    output = StringIO()
    sys.stdout = output
    status(db_path)
    sys.stdout = sys.__stdout__
    expected_output = "Animal Complaint|2"
    assert output.getvalue().strip() == expected_output, f"Expected output: {expected_output}, but got: {output.getvalue()}"
