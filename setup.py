
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in flashchat_integration/__init__.py
from flashchat_integration import __version__ as version

setup(
	name="flashchat_integration",
	version=version,
	description="Complete SMS, WhatsApp, and OTP integration for ERPNext using FlashChat.xyz API",
	author="Erpflow-dev",
	author_email="mushleh.uddin.acca@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
