#!/usr/bin/env python3
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from dataclasses import dataclass, field
from typing import List
from enum import Enum, auto
import re
from sortedcontainers import SortedSet

def get_all_filenames() -> List[Path]:
    files = list(Path(__file__).parent.glob('**/*'))
    return files

@contextmanager
def get_cursor():
    try:
        con = sqlite3.connect("preduzetnik.sqlite3")
        cur = con.cursor()
        yield cur
    finally:
        cur.close()

def get_hashes(column_name: str, table_name: str):
    with get_cursor() as cursor:
        result = cursor.execute(f"SELECT {column_name} FROM {table_name};")
        return [value[0] for value in result.fetchall()]


@dataclass
class ValidatableTarget:
    column_name: str
    table_name: str


class TestState(Enum):
    failed = auto()
    passed = auto()


@dataclass
class TestResult:
    params: ValidatableTarget
    hash: str
    state: TestState
    warnings: List[str] = field(default=list)


def print_results(header: str, results: List[TestResult]):
    if not results:
        return

    print(("=" * 44) + header + ("=" * 44))
    for result in results:
        print(result)


def main():
    files = get_all_filenames()

    targets_to_validate = [
        ValidatableTarget("document_hash", "client_contract"),

        ValidatableTarget("invoice_hash", "client_payment"),
        ValidatableTarget("acceptance_hash", "client_payment"),
        ValidatableTarget("payment_hash", "client_payment"),

        ValidatableTarget("invoice_hash", "service_payment"),
        ValidatableTarget("document_hash", "service_contract"),
        ValidatableTarget("payment_hash", "service_payment"),

        ValidatableTarget("document_hash", "personal_service_contract"),
        ValidatableTarget("payment_hash", "personal_service_payment"),

        ValidatableTarget("invoice_hash", "tax_payment"),
        ValidatableTarget("payment_hash", "tax_payment"),

        ValidatableTarget("document_hash", "tax_type"),
    ]

    test_results: list[TestResult] = []

    all_hashes = SortedSet()

    for params in targets_to_validate:
        for hash in get_hashes(params.column_name, params.table_name):
            all_hashes.add(hash)
            state = TestState.passed
            warnings = []

            if hash is None:
                warnings.append("Hash is None")

            if "NO_NEED" in hash:
                continue
 
            if hash is not None and len([True for file in files if hash in str(file.name)]) != 1:
                state = TestState.failed

            test_results.append(
                TestResult(
                    params=params,
                    hash=hash,
                    state=state,
                    warnings=warnings,
                )
            )

    passed_tests = list([result for result in test_results if result.state == TestState.passed and not result.warnings])
    warning_tests = list([result for result in test_results if result.warnings])
    failed_tests = list([result for result in test_results if result.state != TestState.passed])
    todos = [f"WARNING TODO: {file.name} is discovered at path {str(file)}!" for file in files if "TODO" in file.name]

    zombie_hashes = []
    for file in files:
        if match := re.search(r"(?P<hash>[a-z,0-9]{16})(\.pdf)",file.name):
            if match.groupdict().get("hash") not in all_hashes:
                zombie_hashes.append(f"WARNING ZOMBIE HASH: {match} for file {file}")

    print_results("PASSED_TESTS", passed_tests)
    print_results("WARNING_PASSED_TESTS", warning_tests)
    print_results("WARNING_TODOS", todos)
    print_results("WARNING_ZOMBIE_HASHES", zombie_hashes)
    print_results("FAILED_TESTS", failed_tests)

    print(f"passed_tests amount: {len(passed_tests)}")
    print(f"warning_passed_tests amount: {len(warning_tests)}")
    print(f"warning todos discovered: {len(todos)}")
    print(f"WARNING_ZOMBIE_HASHES discovered: {len(zombie_hashes)}")
    print(f"failed_tests amount: {len(failed_tests)}")



    if len(failed_tests) > 0:
        raise Exception("Some tests failed")

if __name__=="__main__":
    main()
