import os
import re
import subprocess
from typing import Optional

from ProteusConfig import ProteusConfig, ErrorMessages


class ProteusPermutator:
    def __init__(self, config: ProteusConfig):
        self.config = config
        self.permutators: set[str] = set()
        self.input_domains: set[str] = set()
        self.generated_domains: set[str] = set()
        self.low_ram_buffer_file: str = "proteus_permutator_lowram_buffer.txt"

    
    def build_permutator_set(self, harvested_words: Optional[list[str]] = None):
        if harvested_words is None:
            harvested_words = []

        if self.config.useBaselist:
            with open(self.config.baselist, "r") as bl:
                for word in bl:
                    word = word.strip().lower()
                    if word:
                        self.permutators.add(word)

        if self.config.harvest:
            i = 0
            for word in harvested_words:
                if i >= self.config.maxHarvestedWords:
                    break
                if word not in self.permutators:
                    self.permutators.add(word)
                    i += 1

    
    def read_input_domains(self):
        with open(self.config.file, "r") as f:
            for line in f:
                line = line.strip().lower()
                if not re.fullmatch(r'[a-z0-9\-.]+', line): # Filters empty lines, comments, and invalid (anything not a-z 0-9 - . (allowed character of a domain))
                    continue
                self.input_domains.add(line)

    
    def permutate_simple_actions(self):
        if not self.permutators:
            self.build_permutator_set()

        seps = []
        if "simple" in self.config.permutationStrategy:
            seps.append(".")
        if "hyphenate" in self.config.permutationStrategy:
            seps.append("-")
        
        if not seps:
            return
        
        for sep in seps:
            for domain in self.input_domains:
                for perm in self.permutators:
                    gen = f"{perm}{sep}{domain}".strip().lower()
                    if gen not in self.input_domains:
                        if sep == "." or (sep == "-" and len(domain.strip().split(".")) >= 3):
                            self.generated_domains.add(gen)
    
    def permutate_insertion(self):
        if not self.permutators:
            self.build_permutator_set()
        
        if "insert" not in self.config.permutationStrategy:
            return

        for domain in self.input_domains:
            for perm in self.permutators:
                parts = domain.split(".")
                if len(parts) <= 2:
                    continue
                insertions = len(parts) - 2 # insertions are done after every part except for domain and TLD
                insertions_done = 0
                while insertions_done < insertions:
                    position = insertions_done + 1
                    gen = parts.copy()
                    gen.insert(position, perm)
                    res = ".".join(gen)
                    
                    if res not in self.input_domains:
                        self.generated_domains.add(res)
                    insertions_done += 1

    def permutate_append_hyphenate(self):
        if not self.permutators:
            self.build_permutator_set()
        
        if "append-hyphenate" not in self.config.permutationStrategy:
            return

        for domain in self.input_domains:
            for perm in self.permutators:
                parts = domain.split(".")
                if len(parts) <= 2:
                    continue
                appends = len(parts) - 2
                appends_done = 0
                while appends_done < appends:
                    gen = parts.copy()
                    gen[appends_done] += f"-{perm}"
                    res = ".".join(gen)
                    
                    if res not in self.input_domains:
                        self.generated_domains.add(res)
                    appends_done += 1
    
    # The following few methods are the low-ram alternatives to the earlier methods. They function similarly, but are separate methods for clarity. Low-ram methods start with the "lr_" prefix
    def lr_permutate_simple_actions(self):
        if not self.permutators:
            self.build_permutator_set()

        seps = []
        if "simple" in self.config.permutationStrategy:
            seps.append(".")
        if "hyphenate" in self.config.permutationStrategy:
            seps.append("-")
        
        if not seps:
            return
        
        with open(self.low_ram_buffer_file, "a") as buf:
            for sep in seps:
                for domain in self.input_domains:
                    for perm in self.permutators:
                        gen = f"{perm}{sep}{domain}".strip().lower()
                        if gen not in self.input_domains:
                            if sep == "." or (sep == "-" and len(domain.strip().split(".")) >= 3):
                                buf.write(gen + "\n")
    
    def lr_permutate_insertion(self):
        if not self.permutators:
            self.build_permutator_set()
        
        if "insert" not in self.config.permutationStrategy:
            return
        
        with open(self.low_ram_buffer_file, "a") as buf:
            for domain in self.input_domains:
                for perm in self.permutators:
                    parts = domain.split(".")
                    if len(parts) <= 2:
                        continue
                    insertions = len(parts) - 2 # insertions are done after every part except for domain and TLD
                    insertions_done = 0
                    while insertions_done < insertions:
                        position = insertions_done + 1
                        gen = parts.copy()
                        gen.insert(position, perm)
                        res = ".".join(gen)
                        
                        if res not in self.input_domains:
                            buf.write(res + "\n")
                        insertions_done += 1
                    
    def lr_permutate_append_hyphenate(self):
        if not self.permutators:
            self.build_permutator_set()
        
        if "append-hyphenate" not in self.config.permutationStrategy:
            return

        with open(self.low_ram_buffer_file, "a") as buf:
            for domain in self.input_domains:
                for perm in self.permutators:
                    parts = domain.split(".")
                    if len(parts) <= 2:
                        continue
                    appends = len(parts) - 2
                    appends_done = 0
                    while appends_done < appends:
                        gen = parts.copy()
                        gen[appends_done] += f"-{perm}"
                        res = ".".join(gen)
                        
                        if res not in self.input_domains:
                            buf.write(res + "\n")
                        appends_done += 1

    # Basically just does "sort -u [buffer file] > [output file]" to the buffer file
    def dedup_lr_buffer(self):
        # check if generated domains output file already exists
        if os.path.exists(self.config.permutatorOutput):
            raise FileExistsError(ErrorMessages.FILE_ALREADY_EXISTS.format(self.config.permutatorOutput))
        
        if not self.config.silent:
            print("deduplicating the low-ram buffer file")

        subprocess.run([
            "sort", "-u",
            f"{self.low_ram_buffer_file}",
            "-o", f"{self.config.permutatorOutput}"
        ],
        check=True)

        if not self.config.silent:
            print("success, removing buffer file")
        
        os.remove(self.low_ram_buffer_file)

    def write_generated_domains(self):
        # check if generated domains output file already exists
        if os.path.exists(self.config.permutatorOutput):
            raise FileExistsError(ErrorMessages.FILE_ALREADY_EXISTS.format(self.config.permutatorOutput))
        
        with open(self.config.permutatorOutput, "w") as f:
            for l in self.generated_domains:
                f.write(l + "\n")