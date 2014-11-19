
__author__ = 'phillip'

from StringIO import StringIO
import os
import subprocess
import moodlegradetool.testing as testing


testing.TesterMeta.disable = False

default_file = """#RegexTester
NAME: Test
STDIN: testfile

Regex: test
Regex: test2
"""

def test_handlesconfig():
    fd = StringIO("#RegexTester")
    assert testing.RegexTester.handlesconfig(fd)

def test_parseconfig(monkeypatch):
    fd = StringIO(default_file)
    monkeypatch.setattr(testing.TesterMeta, 'disable', True)
    res = testing.RegexTester.parse_config(fd)
    assert 'name' in res
    assert res['name'] == "Test"
    assert 'input_file' in res
    assert res['input_file'] == os.path.abspath("testfile")
    assert 'regexes' in res
    regs = res['regexes']
    assert regs[0].pattern == 'test', regs[1].pattern == 'test2'

def test_start(monkeypatch, tmpdir):
    def mock_checkout(cmd, *args, **kwargs):

        return "test\ntest2"

    tests = {}
    monkeypatch.setattr(testing, 'tests', tests)
    monkeypatch.setattr(subprocess, 'check_output', mock_checkout)
    testing.RegexTester.parse_config(StringIO(default_file))

    t = tests.values()[0]('Mock', "Mock1")
    t.cwd = str(tmpdir)
    t.input_file = StringIO()

    t.start()

    assert t.score == 2
    assert t.possible == 2

