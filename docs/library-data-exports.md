# Library Data

Various places we have data we can upload to the Internet Archive.

## Considerations

- Privacy: nothing with PII or enough data to de-anonymize
- Can any of this be automated or is it all clicking buttons in admin interfaces?

## The List

### Koha

#### MARC records

Admin side > Cataloging > [Export Catalog Data](https://library-staff.cca.edu/cgi-bin/koha/tools/export.pl)

Leave everything as the default for a full data export.

**Privacy**: potential notes in item records? Acquisition notes in MARC? Double check before exporting.

#### Circulation Statistics

Run the ["Anonymized Usage Statistics for Export" report](https://library-staff.cca.edu/cgi-bin/koha/reports/guided_reports.pl?id=471&op=run). This report returns checkout and renewal events alongside patron category and basic bibliographic information. Our smaller patron categories are combined into an "OTHER" field for privacy reasons while the largest circ categories (faculty, grad, and undergrad) are unchanged.

### COUNTER Statistics

Eric's Drive > Computers > Clytemnestra > COUNTER5 > [all_data](https://drive.google.com/drive/folders/1Mfc4kNKsdOaHEugD9WIEJcJR70Ie8vaZ). This is where data compiled by the COUNTER 5 Report Tool is backed up.

Many JSON and TSV files. COUNTER files are abstract enough that they do not present a privacy issue.

### 360 CORE

#### DB Subscriptions

Serials Solution > [Management Reports](https://clientcenter.serialssolutions.com/CC/Reports/QueuedReports.aspx?LibraryCode=CC9) > Database Details Report > Request Report. This is the report of all our subscribed databases, including OA ones.

#### Complete Tracked Resources

In the same place, select the **Tracked Resources** report. This is every title included in our Summon index, which is a very large list of some 650,000 titles (ebooks, journals, and videos). It is too large to import into Google Sheets, though you can use a connected BigQuery project. I created a `tracked-resources-bigquery` project in Google Cloud for this purpose. Appending data into the existing dataset's table in the project looks like this:

```sh
gcloud components install bq # one-time install of bq CLI
# column_name_character_map fixes illegal Database/Provider column name
bq load \
    --source_format=CSV \
    --autodetect \
    --skip_leading_rows=1 \
    --noreplace \
    --column_name_character_map=V2 \
    $DATASET.$TABLE_NAME \
    path/to/Tracked_Resources.csv
```

Another alternative would be to inspect the data using Python's [pandas](https://pandas.pydata.org/).

We should probably just concatenate and zip the two CSVs together for archival purposes.

#### 360 Core Usage Statistics

[Usage statistics](https://intota.hosted.exlibrisgroup.com/Home/Reports)

These are low value as 360 Core was only one aspect of our usage since Summon and we already have COUNTER reports. Eric did a full export of all non-sensitive reports on June 12, 2026 running from 2006 when we acquired Serials Solutions to May, 2026. We probably do not need to revisit this data.

### Statistics Presentations

Download from [Library Data page](https://libraries.cca.edu/about-us/about-us/library-data/) in a couple of formats, e.g. PDF and PPTX.
