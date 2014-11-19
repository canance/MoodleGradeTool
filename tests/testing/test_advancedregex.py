from StringIO import StringIO
from collections import namedtuple
import pexpect
import pytest
from moodlegradetool import testing

from lxml.builder import ElementMaker

E = ElementMaker(namespace="http://moodlegradetool.com/advanced_regex")

__author__ = 'phillip'

default_file = """<?xml version="1.0" encoding="UTF-8"?>
<!--AdvancedRegexTester-->
<AdvRegexTester xmlns="http://moodlegradetool.com/advanced_regex">
    <name>Test1</name>
    <main>Hello</main>
    <Definitions>
        <file id="file1">dummy1.txt:dummy.txt</file>
        <Regex id="reg1">test</Regex>
        <Regex id="reg2">Hello, (.*)</Regex>
        <Regex id="reg3">(\d+?) \+ (\d+?) = (\d+?)</Regex>
        <input id="name" type="str">Phillip</input>
        <input id="num1" type="int">5</input>
        <input id="num2" type="int">10</input>
    </Definitions>
    <Test>
        <Expect prompt="Enter the file name:">
            <input>file1</input>
        </Expect>
        <Expect prompt="Enter your name:">
            <match>reg1</match>
            <input>name</input>
        </Expect>
        <Expect prompt="Enter two numbers">
            <match id="nametest">reg2</match>
            <input>num1</input>
            <input>num2</input>
        </Expect>
        <Expect>
            <match id="equ">reg3</match>
        </Expect>
        <assertion match="nametest">
                <group id="1">
                    name
                </group>
        </assertion>
        <assertion match="equ">
            <group id="1">
                num1
            </group>
            <group id="2">
                num2
            </group>
            <group id="3" eval="true">
                num1+num2
            </group>
        </assertion>
    </Test>
</AdvRegexTester>
"""

class_file = """<?xml version="1.0" encoding="UTF-8"?>
<!--AdvancedRegexTester-->
<AdvRegexTester xmlns="http://moodlegradetool.com/advanced_regex">
    <name>Test1</name>
    <main>Hello</main>
    <Definitions>
        <file id="file1">dummy1.txt:dummy.txt</file>
        <Regex id="reg1">test</Regex>
        <Regex id="reg2">Hello, (.*)</Regex>
        <Regex id="reg3">(\d+?) \+ (\d+?) = (\d+?)</Regex>
        <input id="name" type="str">Phillip</input>
        <input id="num1" type="int">5</input>
        <input id="num2" type="int">10</input>
    </Definitions>
    <Test>
        <expect></expect>
    </Test>
</AdvRegexTester>
"""

@pytest.fixture(scope='module')
def advancedclass():
    maintests = testing.tests
    testing.tests = {}
    testing.AdvancedRegexTester.parse_config(StringIO(class_file))
    res = testing.tests.values()[0]
    testing.tests = maintests
    return res

Prompt = namedtuple("Prompt", ("prompt", "before", 'inputs'))
class ExpectMock(object):

    def __init__(self, prgm="", args=(), prompts=(Prompt("mock", 'mock', ('mock',)), )):
        self.prompts = prompts
        self._nxtp = iter(prompts)
        self.before = ""
        self.prgm = prgm
        self.args = args
        self.inputs = iter([])

    def spawn(self, prgm, args, *arg, **kwargs):
        if self.prgm != prgm:  # Check to make sure its the proper program
            pytest.fail("Unexpected program name {}, should be {}".format(prgm, self.prgm))
            return
        if len(args) != len(self.args):  # Check to make sure the argument lengths match up
            pytest.fail("Given argument list ({}) doesn't match expected list({})".format(args, self.args))
            return
        for xarg, garg in zip(self.args, args):  # Make sure the given arguments match the expected ones
            if xarg != garg:
                pytest.fail("Given argument ({}) doesn't match expected argument ({})".format(xarg, garg))

        return self

    def expect(self, prompt):
        try:
            try:
                next(self.inputs)  # Make sure all expected inputs were encountered
                pytest.fail("Not all expected inputs were consumed")
            except StopIteration:
                pass

            p, b, i = next(self._nxtp)
            if p == prompt:
                self.before = b
                self.inputs = iter(i)
            else:
                pytest.fail("Prompt expected ({}) doesn't match what was given ({})".format(p, prompt))

        except StopIteration:
            pytest.fail("More prompts than expected")

    def send(self, item):
        try:
            exp = next(self.inputs)
            if exp.strip() != item.strip():
                pytest.fail("Given input was not expected: Given {}, Expected {}".format(item, exp))
        except StopIteration:
            pytest.fail("Too many inputs given")

@pytest.fixture(scope='module')
def parse_config():
    fd = StringIO(default_file)
    testing.TesterMeta.disable = True
    res = testing.AdvancedRegexTester.parse_config(fd)
    testing.TesterMeta.disable = False
    return res

def test_handlesconfig():
    fd = StringIO(default_file)
    assert testing.AdvancedRegexTester.handlesconfig(fd)

def test_parsename(parse_config):
    assert 'name' in parse_config
    assert parse_config['name'] == "Test1"

def test_parsemain(parse_config):
    assert 'main' in parse_config
    assert parse_config['main'] == "Hello"

def test_parseregexs(parse_config):
    assert 'regexes' in parse_config
    assert len(parse_config['regexes']) == 3
    assert parse_config['regexes']['reg1'].pattern == 'test'

def test_start(advancedclass, monkeypatch):
    mock = ExpectMock(prgm="java", args=("Hello",))
    test = advancedclass("MStudent1", "Mock1")
    monkeypatch.setattr(pexpect, "spawn", mock.spawn)
    test.start()

def test_match(advancedclass, monkeypatch):
    pass

def test_filename(advancedclass, monkeypatch):
    mock = ExpectMock(prompts=(Prompt("File name:", "", "dummy.txt")))
    node = E.Test(
        E.expect(
            E.input("file1"),
            prompt="File name:"
        )
    )
    test = advancedclass('MStudent1', 'mock')
    test.do_test(mock, node)

