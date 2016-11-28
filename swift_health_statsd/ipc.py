# Copyright 2016 SAP SE
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess, threading

class Timeout(Exception):
    def __init__(self, command, timeout):
        self.command = command
        self.timeout = timeout
    def __str__(self):
        return "Command '{}' aborted after {} seconds".format(self.command, self.timeout)

class CheckOutputHelper(object):
    def run(self, command, timeout=None):
        self.process = None
        self.output = ""

        def worker():
            self.process = subprocess.Popen(command,
                stdout=subprocess.PIPE,
                stderr=None,
                shell=True,
                universal_newlines=True,
            )
            self.output, _ = self.process.communicate()

        thread = threading.Thread(target=worker)
        thread.start()

        thread.join(timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()

        ret = self.process.returncode
        if ret == 0:
            return self.output
        elif ret == -15: # SIGTERM
            raise Timeout(command, timeout)
        else:
            raise subprocess.CalledProcessError(ret, command, self.output)

def check_output(command, timeout=None):
    """
        Equivalent to

        >>> subprocess.check_output(command, shell=True, universal_newlines=True)

        But if a timeout (in seconds) is given, SIGTERM is sent to the process
        after the timeout.
    """
    return CheckOutputHelper().run(command, timeout)
