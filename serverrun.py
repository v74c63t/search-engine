from flask import Flask, render_template, request
import webbrowser
import search

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

index_pos, N, documents = search.load_index()

#the web gui only has one page, and it automatically creates a numbered list upon the urllist var being filled.
@app.route("/", methods=['POST', 'GET'])
def index():
	if request.method == "POST":
		#functions inside search.py need to be changed to support a single call
		nquery = request.form["input"]
		if nquery :
			urllist, time = search.search(documents, index_pos, 5, nquery)
			return render_template('base.html', queries = f"Displaying top {len(urllist)} results for: " + nquery, urllist = urllist, time = time)
		else:
			return render_template('base.html')
	else:
		return render_template('base.html')

if __name__ == "__main__":
	app.run(debug=True)