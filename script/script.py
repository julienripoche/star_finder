#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Spam spam spam !!!
"""

import smtplib
#from email.mime.text import MIMEText
s2 = smtplib.SMTP('smtp.live.com')
s2.starttls()
s2.ehlo()
s2.login('julian.ripoche@hotmail.fr', 'Simracomir41')
s2.sendmail('julian.ripoche@hotmail.fr', 'adrien.blanchet@u-psud.fr', "spam %d" % (0))
