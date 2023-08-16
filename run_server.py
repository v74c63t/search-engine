from flask import Flask, render_template, request
import webbrowser
import search

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# we load in both the index position file and the document url file beforehand so it can be used during retrieval
index_pos, documents = search.load_index()

#the web gui only has one page, and it automatically creates a numbered list upon the urllist var being filled.
@app.route("/", methods=['POST', 'GET'])
def index():
	if request.method == "POST":
		nquery = request.form["input"]
		# if a user inputs some query (as long as it is not "") search would be run for that query
		if nquery :
			urllist, time = search.search(documents, index_pos, 5, nquery)
			# the top 5 results and the query response time will be rendered into the page once everything is complete 
			# by passing its values into variables that will be bound to the html page and displayed  
			return render_template('base.html', queries = f"Displaying Top {len(urllist)} Results for: \"" + nquery+ "\"", urllist = urllist, time = time)
		else:
			# if no query is entered, the default page will be rendered becauses there is nothing assigned to the variables
			return render_template('base.html')
	else:
		return render_template('base.html')
	
@app.route("/about")
def about():
	return render_template('about.html')

if __name__ == "__main__":
	# app.run(debug=True)
	url = 'http://127.0.0.1:5000'
	webbrowser.open_new(url)
	app.run()