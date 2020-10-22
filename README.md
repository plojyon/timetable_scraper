# timetable_scraper
A timetable scraper API that combines timetables from FMF and FRI

API available at [https://fmf-fri-timetable-scraper.herokuapp.com/](https://fmf-fri-timetable-scraper.herokuapp.com/)  
Front-end hosted with Github pages at [https://jakic12.github.io/fri-fmf-timetable](https://jakic12.github.io/fri-fmf-timetable)  
[Front-end source code](https://github.com/jakic12/fri-fmf-timetable)  

Endpoints:
* /getUrnik - returns the entire timetable
* /getFmfUrnik - returns only the FMF part of the timetable
* /getFriUrnik - returns only the FRI part of the timetable

Parameters:
* letnik_fri (def. 43889) - letnik code for urnik.fri (defaults to ISRM)
* letnik_fmf (def. 42) - letnik code for urnik.fmf (defaults to ISRM)
* subject_fri (def. 0) - if set, it will ignore letnik_fri and search with subject id

Return value format:
```
[
  {
    "dan": 0, // 0-4 Monday to Friday
    "predmet": {
        "abbr": "LINALG",
        "location": "FMF",
        "name": "Linearna algebra"
    },
    "profesor": "Jakob Cimpri\u010d",
    "tip": "P", // "P" -predavanja, "LV" -lab. vaje
    "trajanje": 2, // in hours
    "ucilnica": "3.04",
    "ura": 8 // starting time (8:15)
  },
  {
    "dan": 0,
    ...
  },
  ...
]
```

Example request:  
```GET https://fmf-fri-timetable-scraper.herokuapp.com/getUrnik?letnik_fmf=43930&letnik_fri=45```  
```GET https://fmf-fri-timetable-scraper.herokuapp.com/getFriUrnik?letnik_fri=43930```  

Environment variables:
* PORT (def. 5000) port on which to listen
* DEBUG (def. 1) is app in debug mode? Set to 0 for production
