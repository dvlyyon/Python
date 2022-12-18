#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pexpect
import sys


child = pexpect.spawn(sys.argv[1])
while True:
    which = child.expect(["Sign the certificate?",
        "certified, commit?",
        "Enter Export Password",
        "\$ $"])
    if which == 0:
        child.sendline('y')
    if which == 1:
        child.sendline('y')
    if which == 2:
        child.sendline('e2e!Net4u#')
    if which == 3:
        sys.exit()


