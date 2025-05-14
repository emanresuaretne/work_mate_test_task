import argparse
import json
import sys
from typing import *


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("files", nargs="*", help="list of files")
    parser.add_argument("--report", "-r", default="payout", help="type of report")
    parser.add_argument("--output", "-o", help="json file to output")

    return parser.parse_args()

def main():
    args: argparse.Namespace = parse_args()

    Employee = Dict[str, Union[int, str]]
    employees: List[Employee] = []

    for file_name in args.files:
        if file_name.endswith(".csv"):
            try:
                with open(file_name, "r", encoding="utf-8") as csv_file:
                    lines: List[str] = csv_file.readlines()
                    headers: List[str] = lines[0].rstrip("\n").split(',')

                    columns: List[str] = ["id", "name", "email", "department", "hours_worked"]
                    indices: set[int] = set(range(len(columns) + 1))

                    columns_indices: Dict[str, int] = {}
                    for column in columns:
                        index: int = headers.index(column)
                        columns_indices[column] = index
                        indices.remove(index)

                    columns_indices["salary"] = list(indices)[0]

                    for line in lines[1:]:
                        to_report: Employee = {}
                        prep: List[str] = line.rstrip("\n").split(",")
                        for k, v in columns_indices.items():
                            match k:
                                case "id" | "hours_worked" | "salary":
                                    to_report[k] = int(prep[v])
                                case _:
                                    to_report[k] = prep[v]
                        employees.append(to_report)
            except FileNotFoundError:
                sys.exit(f"there is no such a file: {file_name}")
        else:
            sys.exit("all input files should have .csv extension")

    if args.output is not None:
        if args.output.endswith(".json"):
            with open(args.output, 'w') as json_file:
                json.dump(employees, json_file)
        else:
            sys.exit("output file should have .json extension")

    if args.files:
        ReportRow = List[Union[str, int, float]]
        report: List[ReportRow] = []
        match args.report:
            case "payout":
                report.append(["", "name", "hours", "rate", "payout"])

                employees: List[Employee] = sorted(employees, key=lambda e: e["department"])
                prev: str = employees[0]["department"]
                report.append([prev, "", "", "", ""])
                department_hours: int = 0
                department_payout: int = 0

                for e in employees:
                    curr: str = e["department"]
                    if curr != prev:
                        report.append(["", "", department_hours, "", f"${department_payout}"])
                        report.append([curr, "", "", "", ""])
                        department_hours = 0
                        department_payout = 0

                    prev = curr

                    employee_hours: int = e["hours_worked"]
                    employee_salary: int = e["salary"]
                    employee_payout: int = employee_hours * employee_salary
                    report.append(["--------------", e["name"], employee_hours, employee_salary, f"${employee_payout}"])

                    department_hours += employee_hours
                    department_payout += employee_payout

                report.append(["", "", department_hours, "", f"${department_payout}"])

            case "mean":
                report.append(["", "mean"])

                employees: List[Employee] = sorted(employees, key=lambda r: r["department"])
                prev: str = employees[0]["department"]
                department_rate: List[int] = []

                for e in employees:
                    curr: str = e["department"]
                    if curr != prev:
                        department_mean: float = round(sum(department_rate) / len(department_rate), 1)
                        report.append([prev, department_mean])
                        department_rate = []

                    prev = curr

                    department_rate.append(e["salary"])

                department_mean = round(sum(department_rate) / len(department_rate), 1)
                report.append([prev, department_mean])

            case _:
                sys.exit("there is no such a report type")

        widths: List[int] = [0 for _ in report[0]]
        for row in report:
            for i, value in enumerate(row):
                widths[i] = max(widths[i], len(str(value)))

        for row in report:
            print(
                "\t".join(
                    f"{str(item):<{widths[i]}}"
                    for i, item in enumerate(row)
                )
            )
    else:
        sys.exit("please enter at least one input file")

if __name__ == "__main__":
    main()