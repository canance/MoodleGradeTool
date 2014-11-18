from StringIO import StringIO

__author__ = 'phillip'



from moodlegradetool import filemanager
filemanager.disable_testermeta = True

import moodlegradetool.testing as testing

def test_handlesconfig():
    fd = StringIO("#RegexTester")
    fd.write()
    fd.seek(0)
    assert testing.RegexTester.handlesconfig(fd)

def test_parseconfig():
    file = """#RegexTester
    NAME: Test
    INFILE: testfile

    Regex: test
    Regex: test2
    """

    fd = StringIO(file)
    res = testing.RegexTester.parse_config(res)

    assert 'name' in res
    assert res['name'] == "Test"
    assert 'input_file' in res
    assert res['input_file'] == testfile
    assert 'regex' in res
    regs = res['regex']
    assert regs[0] == 'test', regs[1] == 'test2'