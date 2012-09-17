
from django.test import TestCase

from common.fn import load_fn
from common.email import sendmail, renderAndSendMail
from common.rally import import_result

from mock import patch

import smtplib
import os

import datetime



class TestFn(TestCase):

    def test_load_fn(self):
        self.assertEquals(load_fn("common.fn.load_fn"),load_fn)

    def test_load_fn_bad(self):
        self.assertRaises(AttributeError,load_fn,"not.a.module")


class TestEmail(TestCase):

    def setUp(self):
        self.settings = __import__(os.environ['DJANGO_SETTINGS_MODULE'])
        self.settings.SMTPSERVER = 'testserver'

    @patch('smtplib.SMTP')
    def test_sendmail(self,mock):
        sendmail('noone',['nobody'],'hello')
        self.assert_(mock.called)
        self.assertEquals(mock.call_count,1)
        args, kwargs = mock.call_args
        self.assertEquals(args,(self.settings.SMTPSERVER,))
        self.assertEquals(kwargs,{})

    @patch('smtplib.SMTP')
    def test_renderAndSendMail(self,mock):
        renderAndSendMail('common/test.html',{},'none','nobody','nobody')
        self.assert_(mock.called)
        self.assertEquals(mock.call_count,1)
        args, kwargs = mock.call_args
        self.assertEquals(args,(self.settings.SMTPSERVER,))
        self.assertEquals(kwargs,{})




