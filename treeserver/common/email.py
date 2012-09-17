
from django.template import  Context, loader
import smtplib
import logging
import os

def renderAndSendMail(template,contextDict,sender,to,cc):
    t = loader.get_template(template)
    c = Context(contextDict)
    body = t.render(c)
    logging.debug("Rendered body:\n%s" % body)
    logging.debug("Sending baselinetriagereportdone email to %s cc %s" % (to,cc))
    sendmail(sender,[to+cc],body)
    logging.debug("Sent report email to %s cc %s" % (to,cc))

def sendmail(*args, **kwargs):
    settings = __import__(os.environ['DJANGO_SETTINGS_MODULE'])
    if hasattr(settings, 'SMTPSERVER') and settings.SMTPSERVER:
        server = smtplib.SMTP(settings.SMTPSERVER)
        server.sendmail(*args, **kwargs)
        server.quit()
