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
	nquery = request.form["input"]
	if request.method == "POST" and nquery:
		#functions inside search.py need to be changed to support a single call
		urllist = search.search(documents, index_pos, N, 5, nquery)
		return render_template('base.html', queries = "Displaying results for: " + nquery, urllist = urllist)
	else:
		return render_template('base.html')

if __name__ == "__main__":
	app.run(debug=True)
