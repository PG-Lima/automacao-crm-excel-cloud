"""Shared test environment for the demo applications.

These values are deliberately fictional and are set before application modules
are imported, because the application settings are loaded at import time.
"""
import os


os.environ["APP_ENV"] = "test"
os.environ["APP_DEBUG"] = "false"
os.environ["CRM_DEMO_USERNAME"] = "test-crm-user"
os.environ["CRM_DEMO_PASSWORD"] = "test-crm-password"
os.environ["CRM_SESSION_SECRET"] = "crm-test-secret-that-is-at-least-32-characters"
os.environ["CLOUD_DEMO_USERNAME"] = "test-cloud-user"
os.environ["CLOUD_DEMO_PASSWORD"] = "test-cloud-password"
os.environ["CLOUD_SESSION_SECRET"] = "cloud-test-secret-that-is-at-least-32-characters"
