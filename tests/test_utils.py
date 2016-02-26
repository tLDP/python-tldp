
from __future__ import absolute_import, division, print_function

import os
import stat
import uuid
import unittest
from tempfile import NamedTemporaryFile as ntf

from tldptesttools import TestToolsFilesystem

# -- SUT
from tldp.utils import makefh, which, execute
from tldp.utils import statfiles, stem_and_ext
from tldp.utils import arg_isexecutable, isexecutable
from tldp.utils import arg_isreadablefile, isreadablefile
from tldp.utils import arg_isdirectory
from tldp.utils import arg_isloglevel


class Test_isexecutable_and_friends(unittest.TestCase):

    def test_isexecutable(self):
        f = ntf(prefix='executable-file')
        self.assertFalse(isexecutable(f.name))
        mode = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR
        os.chmod(f.name, mode)
        self.assertTrue(isexecutable(f.name))

    def test_arg_isexecutable(self):
        f = ntf(prefix='executable-file')
        self.assertIsNone(arg_isexecutable(f.name))
        mode = stat.S_IXUSR | stat.S_IRUSR | stat.S_IWUSR
        os.chmod(f.name, mode)
        self.assertEqual(f.name, arg_isexecutable(f.name))


class Test_isreadablefile_and_friends(unittest.TestCase):

    def test_isreadablefile(self):
        f = ntf(prefix='readable-file')
        self.assertTrue(isreadablefile(f.name))
        os.chmod(f.name, 0)
        self.assertFalse(isreadablefile(f.name))

    def test_arg_isreadablefile(self):
        f = ntf(prefix='readable-file')
        self.assertEquals(f.name, arg_isreadablefile(f.name))
        os.chmod(f.name, 0)
        self.assertIsNone(arg_isreadablefile(f.name))


class Test_arg_isloglevel(unittest.TestCase):

    def test_arg_isloglevel_integer(self):
        self.assertEquals(7, arg_isloglevel(7))
        self.assertEquals(40, arg_isloglevel('frobnitz'))
        self.assertEquals(20, arg_isloglevel('INFO'))
        self.assertEquals(10, arg_isloglevel('DEBUG'))


class Test_execute(TestToolsFilesystem):

    def test_execute_returns_zero(self):
        exe = which('true')
        result = execute([exe], logdir=self.tempdir)
        self.assertEqual(0, result)

    def test_execute_returns_nonzero(self):
        exe = which('false')
        result = execute([exe], logdir=self.tempdir)
        self.assertEqual(1, result)

    def test_execute_exception_when_logdir_none(self):
        exe = which('true')
        with self.assertRaises(ValueError) as ecm:
            execute([exe], logdir=None)
        e = ecm.exception
        self.assertTrue('logdir must be a directory' in e.message)

    def test_execute_exception_when_logdir_enoent(self):
        exe = which('true')
        logdir = os.path.join(self.tempdir, 'nonexistent-directory')
        with self.assertRaises(IOError) as ecm:
            execute([exe], logdir=logdir)
        e = ecm.exception
        self.assertTrue('nonexistent' in e.filename)


class Test_which(unittest.TestCase):

    def test_good_which_python(self):
        python = which('python')
        self.assertIsInstance(python, str)
        self.assertTrue(os.path.isfile(python))
        qualified_python = which(python)
        self.assertEqual(python, qualified_python)

    def test_bad_silly_name(self):
        silly = which('silliest-executable-name-which-may-yet-be-possible')
        self.assertIsNone(silly)

    def test_fq_executable(self):
        f = ntf(prefix='tldp-which-test', delete=False)
        f.close()
        notfound = which(f.name)
        self.assertIsNone(notfound)
        os.chmod(f.name, 0755)
        found = which(f.name)
        self.assertEqual(f.name, found)
        os.unlink(f.name)


class Test_statfiles(unittest.TestCase):

    def test_statfiles_dir_in_result(self):
        '''Assumes that directory ./sample-documents/ exists here'''
        here = os.path.dirname(os.path.abspath(__file__))
        statinfo = statfiles(here, relative=here)
        self.assertIsInstance(statinfo, dict)
        self.assertTrue(os.path.basename('sample-documents') in statinfo)

    def test_statfiles_dir_rel(self):
        here = os.path.dirname(os.path.abspath(__file__))
        statinfo = statfiles(here, relative=here)
        self.assertIsInstance(statinfo, dict)
        self.assertTrue(os.path.basename(__file__) in statinfo)

    def test_statfiles_dir_abs(self):
        here = os.path.dirname(os.path.abspath(__file__))
        statinfo = statfiles(here)
        self.assertIsInstance(statinfo, dict)
        self.assertTrue(__file__ in statinfo)

    def test_statfiles_file_rel(self):
        here = os.path.dirname(os.path.abspath(__file__))
        statinfo = statfiles(__file__, relative=here)
        self.assertIsInstance(statinfo, dict)
        self.assertTrue(os.path.basename(__file__) in statinfo)

    def test_statfiles_file_abs(self):
        statinfo = statfiles(__file__)
        self.assertIsInstance(statinfo, dict)
        self.assertTrue(__file__ in statinfo)

    def test_statfiles_nonexistent_file(self):
        here = os.path.dirname(os.path.abspath(__file__))
        this = os.path.join(here, str(uuid.uuid4()))
        statinfo = statfiles(this)
        self.assertIsInstance(statinfo, dict)
        self.assertEquals(0, len(statinfo))


class Test_stem_and_ext(unittest.TestCase):

    def test_stem_and_ext_final_slash(self):
        r0 = stem_and_ext('/h/q/t/z/Frobnitz-HOWTO')
        r1 = stem_and_ext('/h/q/t/z/Frobnitz-HOWTO/')
        self.assertEqual(r0, r1)

    def test_stem_and_ext_rel_abs(self):
        r0 = stem_and_ext('/h/q/t/z/Frobnitz-HOWTO')
        r1 = stem_and_ext('Frobnitz-HOWTO/')
        self.assertEqual(r0, r1)


class Test_att_statinfo(unittest.TestCase):

    def test_max_mtime(self):
        pass


class Test_makefh(unittest.TestCase):

    def test_makefh(self):
        f = ntf(prefix='tldp-makefh-openfile-test-', delete=False)
        # fprime = makefh(f.file)
        # self.assertIs(f, fprime)
        # del fprime
        f.close()
        fprime = makefh(f.name)
        self.assertIs(f.name, fprime.name)
        os.unlink(f.name)

#
# -- end of file
