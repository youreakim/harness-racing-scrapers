# Harness racing scrapers

## Description

This project uses Scrapys web scraping framework to collect information from harness
racing sites, such as entries, results and pedigree information.
Countries and sites these spiders use to collect data. Any country with one or more sites
specified are working.
* Australia
    * One site with two different databases it seems.
    * [Australian Harness racing](https://www.harness.org.au/)
        * Entries
        * Results
    * [HRA](https://www.harness.org.au/ausbreed/reports/search)
        * Horses (Collecting a sires offspring is not done yet, a login is required)
        * Results
* Belgium 
    * [Belgische Federatie voor Paardenwedrennen](https://www.trotting.be/)
        * Entries
        * Results
* Canada
    * [Standardbred Canada](http://standardbredcanada.ca/)
        * Entries
        * Results
* Denmark
    * [Dansk Travsports Centralforbund (DTC)](https://travinfo.dk/)
        * Horses
        * Entries
        * Results
* Finland
    * [Suomen Hippos ry](http://www.hippos.fi/)
        * Horses
        * Entries
        * Results
* France
    * [Trotteur Francais](https://www.letrot.com/)
        * Horses
        * Entries
        * Results
    * [IFCE](https://infochevaux.ifce.fr/fr/info-chevaux)
        * Horses
    * [Pedigrees et Qualifications](http://trot-pedigree.net/)
        * Horses
* Germany
    * [Hauptverband für Traberzucht](https://www.hvtonline.de/)
        * Horses
        * Entries
        * Results
* Holland
    * [Stichting Nederlandse Draf- en Rensport](https://ndr.nl/)
        * Horses
        * Entries
        * Results
* Italy
    * These scrapers are in a somewhat working state, they will be improved at a later point.
    * [Unire](https://www.unire.gov.it/)
        * Links to horses from entries and results are unreliable, some have no links, on other occasions multiple horses have had the same link.
        * Horses
        * Entries
        * Results
    * [Associazione Nazionale Allevatori Cavallo Trottatore](https://www.anact.it/)
        * Foreign horses are given a link with no horse id in entries or results, but they are present in the database, just do a name search for the horse.
        * Horses
        * Entries
        * Results
    * [Trottoweb](https://trottoweb.it/)
        * Results
        * Entries
    * [Snai](https://ippica.snai.it/)
        * Results (basically just collecting odds)
* New Zealand
    * [Harness Racing New Zealand](https://www.hrnz.co.nz/)
        * Horses
        * Entries
        * Results
* Norway
* Spain
* Sweden
* USA

*Please contact the owners of the data if you plan to publish any data collected with these spiders.*

This is a long overdue updated version of my old [project](https://github.com/youreakim/Horses).

### Background

Due to the redesign of a lot of the sites I use as datasources the previous version of this
project used I was forced to rewrite a lot of the spiders, but I still felt 
that it had some issues to be resolved. So this rewrite I hope will remedy that.

* There is only one spider for each task, not one for each task and country as it was previously
* To accomplish this I created a handler class
* When a spider is started, the handler is created along with some initial requests 
* The response of the request is then passed to handler that delegates it to the right parsing function
* The first stage handler takes care of searching for available entries, results or horses
* If it finds any a second stage handler is created, with the initial requests needed to retrieve the item
* When all initial requests are finished, control is passed to the second stage
* This behaves as the first stage, but there might be additional requests added to the handler depending on the data processed
* When the second is finished with all its requests it will call a method to return the item scraped
* If data has been collected from multiple sites it will be merged if possible
* All items are now subclassed from one single base class
* Instead of a few large items as previously, they have been split into nested items to better accommodate the database backend that will be used
* All parsing functions are divided first by spider, then by which site is scraped, so there can be a bit of duplicated code to be delt with later


### Requirements

- [scrapy](https://docs.scrapy.org/en/latest/)
- [scrapy playwright](https://github.com/scrapy-plugins/scrapy-playwright) Do not forget to install the browsers 
- [arrow](https://arrow.readthedocs.io/)

### Usage

Navigate horses directory containing the `scrapy.cfg` file.

To search for a horse by name
```
scrapy crawl horse -a country=australia -a horse_name='just believe'
```

To get all available entries
```
scrapy crawl entries -a country=australia
```

To get all available results
```
scrapy crawl results -a country=australia [-a start_date=YYYY-MM-DD] [-a end_date=YYYY-MM-DD] 
```
start_date and end_date defaults to the day before the current date
