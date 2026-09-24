USE ROLE USERADMIN;

CREATE ROLE job_ads_dbt_role;

GRANT ROLE job_ads_dbt_role TO USER transformer;
GRANT ROLE job_ads_dbt_role TO USER indiramahadiva; -- Add your own user name here

use role accountadmin;   -- or sysadmin, whichever role owns job_ads

grant create schema on database job_ads to role job_ads_dbt_role;