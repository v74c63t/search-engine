## ABOUT

This is a search engine that uses rank retrieval to retrieve urls that are most relevant to the query based on the index that was built.

## CONFIGURATION

1. Installing libraries
   There are some libraries used that must be installed because they are not a part of the python standard library. Before running anything, they must be installed through the terminal via pip or pip3 so everything can run. Make sure BeautifulSoup, nltk, and flask are installed as well as nltk stopwords being downloaded prior to executing the program.
2. Documents
   Put the documents you plan on building your index from in a folder inside the directory and name it `DEV` and make sure they are .JSON files.

## EXECUTION

1. **Building the Index**
    - To build the index, open up the terminal and insert `python index.py` and as long as the folder with the documents are set up properly, this would create three files in total: index.json, index_pos.json, and doc_url.json. (Note: this process may take a while to run)
2. **Starting the Search Interface**
   - In order to start up the search interface, open up the terminal and type `python run_server.py`. This would start up the server and allow access to the search interface via a web browser. After running run_server.py, it should automatically open a new window with the app ,but if it does not, go to `http://127.0.0.1:5000` on any web browser to access it.
   ![](img/search_engine.png)
3. **Performing a Query**
   - To perform any query, type in the input box that prompts for the query and press either the enter key or the search button. Shortly after, if possible, the top 5 urls will be displayed back in a list format under the input prompt alongside the amount of time it took to retrieve that information for that particular query. Additionally, the urls in the list can be clicked to be redirected to the actual page.
   ![](img/query1.png)
   ![](img/query2.png)
4. **Additional Notes**
    - If an error pops up, such as accessed denied, you may need to wait a bit for everything to successfully render/load and it should work in a few minutes.
    - Make sure the url has `http://` instead of `https://`.