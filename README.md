1. Update (16.11):
   - hab den display der URLS auf dem "search"-view gefixed, hyperlinks lassen sich jetzt ohne error aufrufen
   - habe den code bisschen sortiert und eine main.py erstellt, die sich auf die crawler-funktionen bezieht
   - die "Home page" wird in unseren results zweimal angezeigt, einmal als https://vm009.rz.uos.de/crawl/ und einmal als https://vm009.rz.uos.de/crawl/index.html, das muss noch korrigiert werden  (I think the issue is that there are two URLs to the same Home page and therefore our if not(visited_links) doesnt pick up on it)
   - jedes mal wenn unsere spider() funktion aufgerufen wird, wird ein neuer Index aufgebaut. Ist whoosh nicht eigentlich dafür da, dass sich sowas gemerkt wird und das nicht passiert? sollte man sich vielleicht nochmal anschauen
   - Habe versucht den search engine mit nem spell checker robuster zu machen - funktioniert noch nicht ganz, momentan funktionieren nur falschgeschriebene Wörter
   - habe das interface vom search view bisschen verschönert (aber lange nicht so schön wie Julians home view, bin nicht so im HTML game)

2. Update (17.11):
   - die Search Ausgabeseite habe ich an das Main Layout angeglichen.
   - es gibt noch probleme des Layouts bei unterschiedlicher Fenstergröße (öffne ich die website auf meinem Laptopbildschirm verschiebt sich einiges)

3. Update (23.11)
   - we need to change something so it accepts lower and upper case letters
   - how can we get rid of the brackets in the output around the words(only relevant when spell-checker corrects words)? 
   - search history output needs to be adapted!! I am so over css, is there a way to write a main css from which the other ones inheret? the current code is so redundant
   - search history css needs to be adapted so it looks pretty, but I am tired now und hab kein Bock mehr:) 
   - how can we put the .css files into the css folder within static in a way that it still finds them?