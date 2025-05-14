import pytest
from unittest.mock import patch, mock_open, ANY
import sys
from main import main, parse_args


def test_parse_args():
    with patch.object(sys, 'argv', ['main.py', 'data1.csv', '--report', 'payout', '--output', 'output.json']):
        args = parse_args()
        assert args.files == ['data1.csv']
        assert args.report == 'payout'
        assert args.output == 'output.json'


def test_file_not_found():
    with patch.object(sys, 'argv', ['main.py', 'non_existent_file.csv']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert str(exc_info.value) == 'there is no such a file: non_existent_file.csv'


def test_invalid_input_file_extension():
    with patch.object(sys, 'argv', ['main.py', 'data1.txt']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert str(exc_info.value) == 'all input files should have .csv extension'


def test_invalid_output_file_extension():
    with patch.object(sys, 'argv', ['main.py', 'data1.csv', '--output', 'output.csv']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert str(exc_info.value) == 'output file should have .json extension'


def test_output_json():
    mock_csv_data = "id,name,email,department,hours_worked,salary\n1,John,john@example.com,HR,40,50\n2,Alice,alice@example.com,IT,35,70"

    expected_employees = [
        {"id": 1, "name": "John", "email": "john@example.com", "department": "HR", "hours_worked": 40, "salary": 50},
        {"id": 2, "name": "Alice", "email": "alice@example.com", "department": "IT", "hours_worked": 35, "salary": 70},
    ]

    with patch.object(sys, 'argv',
                      ['main.py', 'data1.csv', '--report', 'payout', '--output', 'output.json']):
        with patch("builtins.open", new_callable=mock_open, read_data=mock_csv_data) as mocked_open:
            with patch("json.dump") as mock_json_dump:
                main()

                mock_json_dump.assert_called_once_with(expected_employees, ANY)

                mocked_open.assert_any_call("output.json", "w")


def test_invalid_report_type():
    with patch.object(sys, 'argv', ['main.py', 'data1.csv', '--report', 'payin', '--output', 'output.json']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert str(exc_info.value) == "there is no such a report type"
