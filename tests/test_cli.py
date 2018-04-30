from subprocess import run, PIPE
from collections import namedtuple

import pytest

CLI_BASIC_FILE = 'tests/cli_test_data/cli_data_basic.txt'
CLI_ATTR_FILE = 'tests/cli_test_data/cli_data_attributes.txt'


CliTestRecord = namedtuple("CliTestRecord", ["input", "output"])


def generate_cases(source_file):
    input = ""
    output = ""
    cases = []
    with open(source_file, 'r') as fd:
        for line in fd:
            if line.startswith("$ "):
                if input:
                    cases.append(CliTestRecord(input, output))
                    input = output = ""
                input = line[2:].strip()
            else:
                output += line

    if input:
        cases.append(CliTestRecord(input, output))
    return cases


basic_cases = generate_cases(CLI_BASIC_FILE)
attribute_cases = generate_cases(CLI_ATTR_FILE)


def run_bash(input):
    if input.startswith("duden "):
        input = "python -m duden.main " + input[6:]

    run(["bash"], input="pwd", universal_newlines=True)
    run(["bash"], input="ls", universal_newlines=True)
    run(["bash"], input="whoami", universal_newlines=True)
    run(["env"], input="whoami", universal_newlines=True)
    return run(["bash"], stdout=PIPE, stderr=PIPE, input=input,
               universal_newlines=True)


def run_duden(argstring):
    return run_bash("python ./duden/main.py " + argstring)


@pytest.mark.parametrize("input,output", basic_cases)
def test_cli_basic(input, output):
    p = run_bash(input)
    assert p.stderr == '', "stderr is not empty!"
    assert p.stdout == output


@pytest.mark.skip
@pytest.mark.parametrize("input,output", attribute_cases)
def test_cli_attributes(input, output):
    p = run_bash(input)
    assert p.stderr == '', "stderr is not empty!"
    assert p.stdout == output, "stdout does not match"
