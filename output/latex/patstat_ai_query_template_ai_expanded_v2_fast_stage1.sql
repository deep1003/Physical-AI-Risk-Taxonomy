SELECT DISTINCT
 a.appln_id app_id,
 a.appln_auth patent_office,
 a.appln_nr app_num,
 a.earliest_filing_year priority_year,
 t.appln_title title,
 b0.appln_abstract abstract,
 a.docdb_family_size family_size,
 a.granted granted,
 CAST(NULL AS INTEGER) ipc_count,
 CAST(NULL AS INTEGER) cpc_count,
 CAST(NULL AS VARCHAR(4000)) applicant_info,
 CAST(NULL AS VARCHAR(4000)) applicant_std_name_ids,
 CAST(NULL AS VARCHAR(4000)) applicant_sectors,
 CAST(NULL AS VARCHAR(4000)) applicant_ctry_codes,
 CAST(NULL AS VARCHAR(4000)) inventor_info,
 CAST(NULL AS VARCHAR(4000)) inventor_sectors,
 CAST(NULL AS VARCHAR(4000)) inventor_ctry_codes,
 CAST(NULL AS VARCHAR(4000)) all_ipc_codes,
 CASE WHEN (
   EXISTS(SELECT 1 FROM tls209_appln_ipc i WHERE i.appln_id=a.appln_id AND(
     i.ipc_class_symbol LIKE 'G06N%'OR i.ipc_class_symbol LIKE 'G06V%'OR i.ipc_class_symbol LIKE 'G06F  18/%'
     OR i.ipc_class_symbol LIKE 'G06F  40/%'OR i.ipc_class_symbol LIKE 'G10L  13/%'OR i.ipc_class_symbol LIKE 'G10L  15/%'
     OR i.ipc_class_symbol LIKE 'G10L  17/%'OR i.ipc_class_symbol LIKE 'G10L  25/%'))
   OR EXISTS(SELECT 1 FROM tls224_appln_cpc c WHERE c.appln_id=a.appln_id AND(
     c.cpc_class_symbol LIKE 'G06N%'OR c.cpc_class_symbol LIKE 'G06V%'OR c.cpc_class_symbol LIKE 'G06F  18/%'
     OR c.cpc_class_symbol LIKE 'G06F  40/%'OR c.cpc_class_symbol LIKE 'G10L  13/%'OR c.cpc_class_symbol LIKE 'G10L  15/%'
     OR c.cpc_class_symbol LIKE 'G10L  17/%'OR c.cpc_class_symbol LIKE 'G10L  25/%'OR c.cpc_class_symbol LIKE 'Y10S706%'))
 ) THEN 1 ELSE 0 END has_ai_core_code
FROM tls201_appln a
 LEFT JOIN tls202_appln_title t ON a.appln_id=t.appln_id
 LEFT JOIN tls203_appln_abstr b0 ON a.appln_id=b0.appln_id
WHERE a.earliest_filing_year BETWEEN 1990 AND 1990 AND a.granted='Y' AND(
 EXISTS(SELECT 1 FROM tls209_appln_ipc i WHERE i.appln_id=a.appln_id AND(
   i.ipc_class_symbol LIKE 'G06N%'OR i.ipc_class_symbol LIKE 'G06V%'OR i.ipc_class_symbol LIKE 'G06F  18/%'
   OR i.ipc_class_symbol LIKE 'G06F  40/%'OR i.ipc_class_symbol LIKE 'G10L  13/%'OR i.ipc_class_symbol LIKE 'G10L  15/%'
   OR i.ipc_class_symbol LIKE 'G10L  17/%'OR i.ipc_class_symbol LIKE 'G10L  25/%'))
 OR EXISTS(SELECT 1 FROM tls224_appln_cpc c WHERE c.appln_id=a.appln_id AND(
   c.cpc_class_symbol LIKE 'G06N%'OR c.cpc_class_symbol LIKE 'G06V%'OR c.cpc_class_symbol LIKE 'G06F  18/%'
   OR c.cpc_class_symbol LIKE 'G06F  40/%'OR c.cpc_class_symbol LIKE 'G10L  13/%'OR c.cpc_class_symbol LIKE 'G10L  15/%'
   OR c.cpc_class_symbol LIKE 'G10L  17/%'OR c.cpc_class_symbol LIKE 'G10L  25/%'OR c.cpc_class_symbol LIKE 'Y10S706%'))
 OR EXISTS(SELECT 1 FROM tls209_appln_ipc i WHERE i.appln_id=a.appln_id AND(
   i.ipc_class_symbol LIKE 'A61B   5/00%'OR i.ipc_class_symbol LIKE 'A61B  34/00%'OR i.ipc_class_symbol LIKE 'A63F  13/67%'
   OR i.ipc_class_symbol LIKE 'B23K  31/00%'OR i.ipc_class_symbol LIKE 'B25J%'OR i.ipc_class_symbol LIKE 'B29C  65/00%'
   OR i.ipc_class_symbol LIKE 'B60W  30/%'OR i.ipc_class_symbol LIKE 'B60W  40/%'OR i.ipc_class_symbol LIKE 'B60W  50/%'OR i.ipc_class_symbol LIKE 'B60W  60/%'
   OR i.ipc_class_symbol LIKE 'B62D  15/02%'OR i.ipc_class_symbol LIKE 'B62D  57/032%'OR i.ipc_class_symbol LIKE 'B64C%'OR i.ipc_class_symbol LIKE 'B64G   1/24%'
   OR i.ipc_class_symbol LIKE 'E21B  41/00%'OR i.ipc_class_symbol LIKE 'F02D  41/14%'OR i.ipc_class_symbol LIKE 'F03D   7/04%'OR i.ipc_class_symbol LIKE 'F16H  61/00%'
   OR i.ipc_class_symbol LIKE 'G01C  21/%'OR i.ipc_class_symbol LIKE 'G01N  29/44%'OR i.ipc_class_symbol LIKE 'G01N  33/00%'OR i.ipc_class_symbol LIKE 'G01R  31/2%'
   OR i.ipc_class_symbol LIKE 'G01R  31/3%'OR i.ipc_class_symbol LIKE 'G01S   7/41%'OR i.ipc_class_symbol LIKE 'G01S  13/%'OR i.ipc_class_symbol LIKE 'G01S  17/%'
   OR i.ipc_class_symbol LIKE 'G02B  27/01%'OR i.ipc_class_symbol LIKE 'G05B  13/02%'OR i.ipc_class_symbol LIKE 'G05D   1/%'OR i.ipc_class_symbol LIKE 'G06E%'
   OR i.ipc_class_symbol LIKE 'G06F   9/44%'OR i.ipc_class_symbol LIKE 'G06F  11/%'OR i.ipc_class_symbol LIKE 'G06F  15/%'OR i.ipc_class_symbol LIKE 'G06F  16/%'
   OR i.ipc_class_symbol LIKE 'G06F  17/%'OR i.ipc_class_symbol LIKE 'G06F  19/%'OR i.ipc_class_symbol LIKE 'G06F  21/%'OR i.ipc_class_symbol LIKE 'G06G   7/00%'
   OR i.ipc_class_symbol LIKE 'G06J   1/00%'OR i.ipc_class_symbol LIKE 'G06K   7/14%'OR i.ipc_class_symbol LIKE 'G06K   9/%'OR i.ipc_class_symbol LIKE 'G06Q%'
   OR i.ipc_class_symbol LIKE 'G06T%'OR i.ipc_class_symbol LIKE 'G08B  29/18%'OR i.ipc_class_symbol LIKE 'G08G%'OR i.ipc_class_symbol LIKE 'G09B%'
   OR i.ipc_class_symbol LIKE 'G10L%'OR i.ipc_class_symbol LIKE 'G11B  20/10%'OR i.ipc_class_symbol LIKE 'G16H%'OR i.ipc_class_symbol LIKE 'H01M   8/04992%'
   OR i.ipc_class_symbol LIKE 'H02H   1/00%'OR i.ipc_class_symbol LIKE 'H02P  21/00%'OR i.ipc_class_symbol LIKE 'H02P  23/00%'OR i.ipc_class_symbol LIKE 'H03H  17/02%'
   OR i.ipc_class_symbol LIKE 'H04L  12/%'OR i.ipc_class_symbol LIKE 'H04L  25/0%'OR i.ipc_class_symbol LIKE 'H04L  41/%'OR i.ipc_class_symbol LIKE 'H04L  51/%'
   OR i.ipc_class_symbol LIKE 'H04N  21/466%'OR i.ipc_class_symbol LIKE 'H04R  25/00%'))
 OR EXISTS(SELECT 1 FROM tls224_appln_cpc c WHERE c.appln_id=a.appln_id AND(
   c.cpc_class_symbol LIKE 'B25J%'OR c.cpc_class_symbol LIKE 'B60W  60/%'OR c.cpc_class_symbol LIKE 'B62D  57/032%'OR c.cpc_class_symbol LIKE 'G01C  21/%'
   OR c.cpc_class_symbol LIKE 'G02B  27/01%'OR c.cpc_class_symbol LIKE 'G05B  13/02%'OR c.cpc_class_symbol LIKE 'G05B2219/40%'OR c.cpc_class_symbol LIKE 'G05D   1/%'
   OR c.cpc_class_symbol LIKE 'G06F  15/18%'OR c.cpc_class_symbol LIKE 'G06F  16/%'OR c.cpc_class_symbol LIKE 'G06F  17/16%'OR c.cpc_class_symbol LIKE 'G06F  17/2%'
   OR c.cpc_class_symbol LIKE 'G06F  17/30%'OR c.cpc_class_symbol LIKE 'G06K   9/%'OR c.cpc_class_symbol LIKE 'G06T   1/20%'OR c.cpc_class_symbol LIKE 'G06T   7/00%'
   OR c.cpc_class_symbol LIKE 'G06T2207/20%'OR c.cpc_class_symbol LIKE 'G08G   1/16%'OR c.cpc_class_symbol LIKE 'H04L  51/02%'OR c.cpc_class_symbol LIKE 'G16H%'
   OR c.cpc_class_symbol LIKE 'Y10S901%'))
);