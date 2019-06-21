# Changelog

## Pre release

### Implemented enhancements
- TT-1491 Adding sorting via title and more relevance to query that matches in titles
- TT-1459 Added testapi endpoint to create ISD companies which are used in automated tests
- TT-1558 Add managment command to mask personal company data

### Fixed bugs
- No ticket - Upgraded djangorestframework to resolve security vulnerability
- No ticket - Upgraded directory-client-core to fix inconsistency in cache.
- TT-1438 - Allow searching for companies via case study attributes
- TT-1438 - Add website Testimonial to CaseStudySearch

## [2019.05.23](https://github.com/uktrade/directory-api/releases/tag/2019.05.23)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.05.16...2019.05.23)

### Fixed bugs

- TT-1480 - Fixed pagination
- TT-1463 - Improved ordering of companies that match multiple filters
- TT-1481 - Allow searching via expertise fields in term

## [2019.05.16](https://github.com/uktrade/directory-api/releases/tag/2019.05.16)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.05.09...2019.05.16)

### Implemented enhancements
- TT-1408 - Customize ISD search results order.

### Fixed bugs:
- TT-7 - Fixed Server Error (500) when searching for pre-verified enrolments
- Replaced is_published field in fixtures/development.json from is_published_investment_support_directory & is_published_find_a_supplier
- TT-1438 - Fixed inability to search by case study contents.
- TT-1472 - Fixed unwanted partial matches of expertise filters

## [2019.05.09](https://github.com/uktrade/directory-api/releases/tag/2019.05.09)
[Full Changelog](https://github.com/uktrade/directory-api/compare/2019.04.08...2019.05.09)

### Implemented enhancements
- Upgraded Elasticsearch from 5 to 6
- TT-1317 - Added feature to bulk upload expertise from django admin
- TT-1348 - Added Investment Support Directory search endpoint
- TT-1398 - Populate products and services from keywords
- TT-1428 - fixed 404 ,allow investment support directory companies and FAS to return a profile.
- TT-1446 - Added new testapi endpoint to discover unpublished companies & extra details to testapi responses in order to facilitate automated testing for pre-verified companies.

### Fixed bugs:

- Upgraded urllib3 to fix [vulnerability](https://nvd.nist.gov/vuln/detail/CVE-2019-11324)
