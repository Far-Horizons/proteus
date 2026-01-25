import os
import re
from collections import Counter

from ProteusConfig import ProteusConfig, ErrorMessages


class ProteusHarvester:
    def __init__(self, config: ProteusConfig):
        self.config = config
        self.harvestCounter = Counter() # harvested words, along with how many times they appear. This does not automatically sort by rank (use .most_common())
    
    def harvest(self):
        # open the file
        with open(self.config.file, "r") as f:
            for line in f:
                line = line.strip().lower()
                if not re.fullmatch(r'[a-z0-9\-.]+', line): # Filters empty lines, comments, and invalid (anything not a-z 0-9 - . (allowed character of a domain))
                    continue
                
                # split line into pieces and write to a counter
                parts = line.split(".")
                for p in parts:
                    p = p.strip()
                    if p:
                        self.harvestCounter[p] += 1

    def write_harvest_ranking(self):
        # check if harvester output file already exists
        if os.path.exists(self.config.harvesterOutput):
            raise FileExistsError(ErrorMessages.FILE_ALREADY_EXISTS.format(self.config.harvesterOutput))
        
        with open(self.config.harvesterOutput, "w") as f:
            for word, count in self.harvestCounter.most_common():
                f.write(f"{word} : {count}\n")
        
    def get_harvested_words(self): # limited by maxHarvestedWords
        top_words_with_count = self.harvestCounter.most_common(self.config.maxHarvestedWords)
        top_words = [word for word, _ in top_words_with_count]
        return top_words