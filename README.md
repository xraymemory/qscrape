# qscrape
Python scraper for gathering Q intel and generating your own drops
 
# Usage
You can run the scraper via command line ```python3 qscrape.py``` or import and invoke like so
```Python
from qscrape import Q

q = Q()
# Get Q drops 1 through 420
q.scrape(start=1, end=420)
# Output to file './q.json'
q.save()
# Markov generation
print(q.drop())
'To suggest this is the first domino.'
```

The data is represented internally as an `OrderedDict` with the following shape 

```Python
{ "number": int,
  "date": str,
  "text": str
}
```

The `save` function outputs JSON 

# Why?
While the author of this tool personally believes QAnon is one part shitpost two parts psyop, one cannot deny the importance of Q's posts as bizarre socio-political artifacts. `qscrape` is developed and maintained for use in digital archaeology and media studies
