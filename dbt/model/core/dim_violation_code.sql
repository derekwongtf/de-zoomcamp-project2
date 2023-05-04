{{ config(materialized='view') }}


select 
    VIOLATION_CODE, 
    VIOLATION_DESCRIPTION
from {{ ref('violation_code_lookup') }}