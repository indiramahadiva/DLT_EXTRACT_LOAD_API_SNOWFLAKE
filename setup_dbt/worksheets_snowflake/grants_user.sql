USE ROLE USERADMIN;

CREATE ROLE job_ads_dbt_role;

GRANT ROLE job_ads_dbt_role TO USER transformer;
GRANT ROLE job_ads_dbt_role TO USER indiramahadiva; -- Add your own user name here