-- NOTE: you should .gitignore this file as it contains credentials
USE ROLE useradmin;
CREATE USER IF NOT EXISTS reporter
    PASSWORD = 'Indiramahadiva0' -- create and fill in password
    LOGIN_NAME = 'reporter'
    DEFAULT_WAREHOUSE = dev_wh
    DEFAULT_NAMESPACE = 'job_ads.marts'
    COMMENT = 'reporter user for making analysis and BI'
    DEFAULT_ROLE = 'job_ads_reporter_role';

USE ROLE useradmin;
ALTER USER reporter SET PASSWORD = 'Indiramahadiva0';