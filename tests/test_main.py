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
        "8/2/2024 0:10 2024-00055701 2954 OAK TREE AVE Traffic Stop OK0140200\n"
        "8/2/2024 0:12 2024-00011459 700 N BERRY RD Medical Call Pd Requested 14005\n"
        "8/2/2024 0:12 2024-00015446 700 N BERRY RD Medical Call Pd Requested EMSSTAT\n"
        "8/2/2024 0:13 2024-00055703 148 REED AVE Disturbance/Domestic OK0140200\n"
        "8/2/2024 0:14 2024-00055702 2560 E LINDSEY ST Traffic Stop OK0140200\n"
        "8/2/2024 0:22 2024-00055705 W LINDSEY ST / ELM AVE Foot Patrol OK0140200\n"
    )

    mock_pdf_reader.return_value.pages = [mock_page]

    result = extractincidents('downloaded_file.pdf')

    expected_result = ["8/2/2024 0:12 2024-00011459 700 N BERRY RD Medical Call Pd Requested 14005", "8/2/2024 0:13 2024-00055703 148 REED AVE Disturbance/Domestic OK0140200", "8/2/2024 0:22 2024-00055705 W LINDSEY ST / ELM AVE Foot Patrol OK0140200"]

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
        "09/15/2024 10:30 2024-00011501 201 REED AVE Traffic Accident OK0140200",  
        "09/16/2024 08:15 2024-00011502 123 MAIN ST Theft OK0140200",              
        "Wrong data format",                                                      
    ]

    populatedb(db_path, incidents)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM incidents")
    rows = cursor.fetchall()

    assert len(rows) == 2, "Not all valid rows inserted."

    expected_data = [
        ("09/15/2024 10:30", "2024-00011501", "201 REED AVE", "Traffic Accident", "OK0140200"),
        ("09/16/2024 08:15", "2024-00011502", "123 MAIN ST", "Theft", "OK0140200")
    ]

    for row, expected in zip(rows, expected_data):
        assert row == expected, f"Expected {expected} but got {row}"

    conn.close()



def test_status():
    db_path = createdb()

    incidents = [
        "09/15/2024 10:30 2024-00011501 201 REED AVE Traffic Accident OK0140200",  
        "09/16/2024 08:15 2024-00011502 123 MAIN ST Theft OK0140200",
        "09/17/2024 14:45 2024-00011503 456 OAK ST Traffic Accident OK0140200",  
    ]

    populatedb(db_path, incidents)

    output = StringIO()
    sys.stdout = output

    status(db_path)

    sys.stdout = sys.__stdout__

    expected_output = "Theft|1\nTraffic Accident|2\n"
    assert output.getvalue() == expected_output, "The output is incorrect."

