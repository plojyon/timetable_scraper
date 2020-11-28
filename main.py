import requests
from bs4 import BeautifulSoup
from pprint import pprint
from flask import Flask, json, request
from flask_cors import CORS
import json
import re
import os

app = Flask(__name__);
CORS(app);

try:
	PORT = int(os.getenv("PORT"));
except:
	PORT = 5000;
if not PORT: PORT = 5000;
print("Using port "+str(PORT));

production = os.getenv("DEBUG") == '0';
if not production:
	print("Running in debug mode. Do not deploy in this state.");

TIMETABLE = "failed to load";
try:
	with open('timetable.json') as json_file:
		TIMETABLE = json.load(json_file);
except:
	print("Failed to load timetable json.");

dayIndex = {
	"MON": 0,
	"TUE": 1,
	"WED": 2,
	"THU": 3,
	"FRI": 4
	# weekends don't exist in urnik.fri
}
'''
for (i in urnik) {
  if (urnik[i].predmet.abbr == "ODV" && urnik[i].tip == "P") urnik[i].link = "https://teams.microsoft.com/l/channel/19%3abfaa863595024fcc91959ddf16e89030%40thread.tacv2/General?groupId=c76ad578-7a69-4b47-bd06-07521f0ab47d&tenantId=a6cc90df-f580-49dc-903f-87af5a75338e"
  if (urnik[i].predmet.abbr == "ODV" && urnik[i].tip == "LV") urnik[i].link = "https://teams.microsoft.com/l/channel/19%3a946e2e041f794f19bfb77efd9d773acd%40thread.tacv2/Laboratorijske%2520vaje?groupId=c76ad578-7a69-4b47-bd06-07521f0ab47d&tenantId=a6cc90df-f580-49dc-903f-87af5a75338e"
  if (urnik[i].predmet.abbr == "P1" && urnik[i].tip == "P") urnik[i].link = "https://uni-lj-si.zoom.us/j/7311330543?pwd=ZnBZZnpyU2pNSUF1dFIwOTlxblg2Zz09"
  if (urnik[i].predmet.abbr == "P1" && urnik[i].tip == "LV") urnik[i].link = "https://teams.microsoft.com/l/channel/19%3a82a5038cac3b4e46a2059c40d2ee8843%40thread.tacv2/General?groupId=d308da2b-c295-4e5d-9ec3-141b7f5516d8&tenantId=a6cc90df-f580-49dc-903f-87af5a75338e"
  if (urnik[i].predmet.abbr == "A1") urnik[i].link = "Ni linka :("
  if (urnik[i].predmet.abbr == "DS1" && urnik[i].tip == "P") urnik[i].link = "https://uni-lj-si.zoom.us/j/93091769572?pwd=RlhwRzNWVDlWT3A0L2d5NXo0MmNFZz09"
  if (urnik[i].predmet.abbr == "DS1" && urnik[i].tip == "V") urnik[i].link = "https://fmf-uni-lj-si.zoom.us/j/91779033051?pwd=dWdRV2JJanNOM0ZWUFBoTVlObDJ6Zz09"
  if (urnik[i].predmet.abbr == "LINALG" && urnik[i].tip == "P") urnik[i].link = "https://fmf-uni-lj-si.zoom.us/j/91456042157?pwd=d1YrK3NWYzIzQ2h3WEpPb2hBZFRudz09"
  if (urnik[i].predmet.abbr == "LINALG" && urnik[i].tip == "V") urnik[i].link = "https://uni-lj-si.zoom.us/j/99794927001?pwd=VGY0dHdlY0xIVWNKYndPemEzR2FWUT09"
}
'''
predmeti = {
	"ODV_LV": {
		"name": "Osnove digitalnih vezij",
		"abbr": "ODV",
		"location": "FRI"
	},
	"ODV_P": {
		"name": "Osnove digitalnih vezij",
		"abbr": "ODV",
		"location": "FRI"
	},
	"P1_LV": {
		"name": "Programiranje 1",
		"abbr": "P1",
		"location": "FRI"
	},
	"P1_P": {
		"name": "Programiranje 1",
		"abbr": "P1",
		"location": "FRI"
	},
	"Analiza 1": {
		"name": "Analiza 1",
		"abbr": "A1",
		"location": "FMF"
	},
	"Diskretne strukture 1": {
		"name": "Diskretne strukture 1",
		"abbr": "DS1",
		"location": "FMF"
	},
	"Linearna algebra": {
		"name": "Linearna algebra",
		"abbr": "LINALG",
		"location": "FMF"
	},
	"Kolokviji 1": {
		"name": "Kolokviji 1",
		"abbr": "K1",
		"location": "FMF"
	}
}

@app.route('/', methods=['GET'])
def get_cache():
	return json.dumps(TIMETABLE);

@app.route('/getFriUrnik', methods=['GET'])
def get_fri():
	letnik = request.args.get('letnik_fri', default=43889, type=int);
	subject = request.args.get('subject_fri', default=0, type=int);
	if subject == 0:
		URL = 'https://urnik.fri.uni-lj.si/timetable/fri-2020_2021-zimski-drugi-teden/allocations?group='+str(letnik);
	else:
		URL = 'https://urnik.fri.uni-lj.si/timetable/fri-2020_2021-zimski-drugi-teden/allocations?subject='+str(subject);
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

		if predmet in predmeti:
			p = predmeti[predmet];
		else:
			p = {"name": predmet, "abbr": predmet, "location": "FRI"};
		results.append({"predmet": p, "profesor": profesor, "ucilnica": ucilnica, "tip": tip, "dan": dan, "ura":ura, "trajanje": trajanje});
	return json.dumps(results);

@app.route('/getFmfUrnik', methods=['GET'])
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

		if predmet in predmeti:
			p = predmeti[predmet];
		else:
			p = {"name": predmet, "abbr": predmet, "location": "FMF"};
		results.append({"predmet": p, "profesor": profesor, "ucilnica": ucilnica, "tip": tip, "dan": dan, "ura":ura, "trajanje": trajanje});
	return json.dumps(results);

@app.route('/getUrnik', methods=['GET'])
def get_both():
	return json.dumps(json.loads(get_fmf()) + json.loads(get_fri()));

@app.errorhandler(500)
def err500(e):
	if (not production):
		return json.dumps([{"error": "500", "e": e}]);
	else:
		return json.dumps([{"error": "500"}]);

@app.errorhandler(404)
def err404(e):
	if (not production):
		return json.dumps([{"error": "404", "e": e}]);
	else:
		return json.dumps([{"error": "404"}]);

if __name__ == '__main__':
	app.run(port=PORT);
