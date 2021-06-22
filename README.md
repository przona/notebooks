# Notebooks used in the project Przona

Contact person: Erik Tjong Kim Sang e.tjongkimsang@esciencecenter.nl

Notebooks for scraping websites with medical guidelines and performing text analysis

## Website richtlijnendatabase.nl

1. Run `scrape_website.ipynb` to retrieve the html files. They will be stored in the directory `../data/richtlijnendatabase.nl`
2. Run `get_paragraphs.ipynb` to extract the paragraphs with text from the downloaded files. They will be stored in the file `csv/paragraphs_20210621.csv`
3. Run steps 1 and 4 of `text_ranking.ipynb` to find the paragraphs with relevant medical terms regarding **ehealth**. This information will be stored in the files `paragraphs.json` and `index.html`
4. Run `json_diff.ipynb` to compare the json file of step 3 with a previous version and classify the html pages according to treatment steps. The results will be stored in the file `index.html`
