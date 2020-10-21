import requests
from bs4 import BeautifulSoup
from pprint import pprint
from flask import Flask, json, request
import re
import os

production = not bool(int(os.environ.get('DEBUG', "1")));
if not production:
	print("Running in debug mode. Do not deploy in this state.");

dayIndex = {
	"MON": 0,
	"TUE": 1,
	"WED": 2,
	"THU": 3,
	"FRI": 4
	# weekends don't exist in urnik.fri
}

api = Flask(__name__);


@api.route('/getFriUrnik', methods=['GET'])
def get_fri():
	letnik = request.args.get('letnik_fri', default=43889, type=int);
	URL = 'https://urnik.fri.uni-lj.si/timetable/fri-2020_2021-zimski-drugi-teden/allocations?group='+str(letnik);
	page = requests.get(URL);
	soup = BeautifulSoup(page.content, 'html.parser');

	results = [];
	entries = soup.find_all(class_="grid-entry");
	for entry in entries:
		termin = re.search(r"grid-row: (\d?\d) / span (\d?\d);", entry['style']);
		if (termin != None):
			ura = 6+int(termin.group(1)) if termin.group(1) != None else -1;
			trajanje = int(termin.group(2)) if termin.group(2) != None else -1;
		else:
			ura = -1;
			trajanje = -1;

		dan = re.search(r"grid-area: day(...)", entry.parent['style']);
		dan = dayIndex[dan.group(1)] if (dan != None) else -1;

		predmet = entry.find(class_='link-subject').text.strip();

		tip = entry.find(class_='entry-type').text[1:].strip();

		profesor = entry.find(class_='link-teacher').text.title();

		ucilnica = entry.find(class_='link-classroom').text;

		results.append({"predmet": predmet, "profesor": profesor, "ucilnica": ucilnica, "tip": tip, "dan": dan, "ura":ura, "trajanje": trajanje});
	return json.dumps(results);

@api.route('/getFmfUrnik', methods=['GET'])
def get_fmf():
	letnik = request.args.get('letnik_fmf', default=42, type=int);
	URL = 'https://urnik.fmf.uni-lj.si/letnik/'+str(letnik);
	page = requests.get(URL);
	soup = BeautifulSoup(page.content, 'html.parser');

	results = [];
	entries = soup.find_all(class_="srecanje-absolute-box");
	for entry in entries:
		dan = re.search(r"left: (\d?\d)\.\d\d%", entry['style']);
		dan = int(dan.group(1))//20 if (dan != None) else -1;

		ura = re.search(r"top: (\d?\d\.\d\d)%", entry['style']);
		ura = 7+round(float(ura.group(1))/7.69) if (ura != None) else -1;

		trajanje = re.search(r"height: (\d?\d\.\d\d)%", entry['style']);
		trajanje = round(float(trajanje.group(1))/7.69) if (trajanje != None) else -1;

		predmet = entry.find(class_='predmet').find('a').text.strip();

		tip = entry.find(class_='predmet').find(class_="tip").text.strip();

		profesor = entry.find(class_='ucitelj').find('a');
		profesor = profesor['title'] if profesor else "";

		ucilnica = entry.find(class_='ucilnica').find('a');
		ucilnica = ucilnica['title'] if ucilnica else "";

		results.append({"predmet": predmet, "profesor": profesor, "ucilnica": ucilnica, "tip": tip, "dan": dan, "ura":ura, "trajanje": trajanje});
	return json.dumps(results);

@api.route('/getUrnik', methods=['GET'])
def get_both():
	return json.dumps(json.loads(get_fmf()) + json.loads(get_fri()));

@api.errorhandler(500)
def err500(e):
	if (not production):
		return json.dumps([{"error": "500", "e": e}]);
	else:
		return json.dumps([{"error": "500"}]);

@api.errorhandler(404)
def err404(e):
	if (not production):
		return json.dumps([{"error": "404", "e": e}]);
	else:
		return json.dumps([{"error": "404"}]);

if __name__ == '__main__':
	api.run();
