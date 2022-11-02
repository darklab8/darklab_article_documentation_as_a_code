#!/usr/bin/env python3
import subprocess
import inspect
subprocess.run(inspect.cleandoc("""
git remote remove origin || true
    && git remote add origin git@github.com-dd84ai:dd84ai/darklab_secrets.git
    && git remote set-url --add --push origin git@github.com-dd84ai:dd84ai/darklab_secrets.git
    && git remote set-url --add --push origin git@gitlab.com-dd84ai:dd84ai/darklab_secrets.git
""").replace("\n",""), shell=True, check=True)