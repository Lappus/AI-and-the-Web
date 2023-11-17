1. Update (16.11):
   - hab den display der URLS auf dem "search"-view gefixed, hyperlinks lassen sich jetzt ohne error aufrufen
   - habe den code bisschen sortiert und eine main.py erstellt, die sich auf die crawler-funktionen bezieht
   - die "Home page" wird in unseren results zweimal angezeigt, einmal als https://vm009.rz.uos.de/crawl/ und einmal als https://vm009.rz.uos.de/crawl/index.html, das muss noch korrigiert werden  (I think the issue is that there are two URLs to the same Home page and therefore our if not(visited_links) doesnt pick up on it)
   - jedes mal wenn unsere spider() funktion aufgerufen wird, wird ein neuer Index aufgebaut. Ist whoosh nicht eigentlich dafür da, dass sich sowas gemerkt wird und das nicht passiert? sollte man sich vielleicht nochmal anschauen
   - Habe versucht den search engine mit nem spell checker robuster zu machen - funktioniert noch nicht ganz, momentan funktionieren nur falschgeschriebene Wörter
   - habe das interface vom search view bisschen verschönert (aber lange nicht so schön wie Julians home view, bin nicht so im HTML game)
