import os
import argparse
import subprocess
from dataclasses import dataclass

class ProteusProcessor: #The processor will take in the file of known subdomains, split it, rank it.
    def __init__(self, filepath):
        self.filepath = filepath
    
class ProteusArgManager:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Proteus is a subdomain permutator and resolver. Developed by Far Horizon (farhorizon.dev)",
                                              epilog="\n!!!!!\nI recommend calculating the total generated permutations in advance, as a large number of permutations can take hours or even days to resolve. The default baselist has 150 entries.\n\nThe amount of permutations can be calculated with (baselist length + harvested words)* known domains\n!!!!!")
        self._configure_arguments()
    
    def _configure_arguments(self):
        # Input files
        self.parser.add_argument(
            "-f", "--file",
            required=True,
            type=str,
            help="set the file containing target subdomains. Currently only accepts .txt files [REQUIRED]"
        )
        self.parser.add_argument(
            "-b", "--baselist",
            type=str,
            default="default",
            help="set a preset list of words to include for permutation. if none is set, the default list will be used"
        )

        # Function toggles
        self.parser.add_argument(
            "--no-baselist",
            dest="useBaselist",
            action='store_false',
            help="instruct the permutator to not use a baselist [DEFAULT: enabled]"
        )
        self.parser.add_argument(
            "--no-resolve",
            dest="resolve",
            action='store_false',
            help="disable DNS resolution. Only permutation is performed [DEFAULT: enabled]"
        )
        self.parser.add_argument(
            "--no-harvest",
            dest="harvest",
            action='store_false',
            help="disable harvesting of domain parts. The permutator will only use the words from the baselist [DEFAULT: enabled"
        )

        # Rate-limiting
        self.parser.add_argument(
            "-tr", "--threads-resolver",
            type=int,
            default=100,
            help="set the amount of threads used by the resolver (dnsx) [DEFAULT: 100]"
        )
        self.parser.add_argument(
            "-rr", "--rate-resolver",
            type=int,
            default=-1,
            help="set a rate limit for the resolver (dnsx) [DEFAULT: -1 (none)]"
        )

        # Behavior
        self.parser.add_argument(
            "-mhw","--max-harvested-words",
            type=int,
            default=200,
            help="Set the maximum amount of words harvested and used for permutation [DEFAULT: 200]"
        )
        self.parser.add_argument(
            "-v", "--verbose",
            action='store_true',
            help="enable verbose mode [DEFAULT: False]"
        )
        self.parser.add_argument(
            "-s", "--silent",
            action='store_true',
            help="enable silent mode [DEFAULT: False]"
        )

        # Dangerous arguments
        self.parser.add_argument(
            "--overwrite-files",
            action='store_true',
            help="Proteus might write certain outputs to files. If this option is enabled, and the output file already exists, these files might be overwritten [DEFAULT: False]"
        )

    def parse(self):
        args = self.parser.parse_args()
        config = ProteusConfig(
            file=args.file,
            baselist=args.baselist,
            threadsResolver=args.threads_resolver,
            rateResolver=args.rate_resolver,
            resolve=args.resolve,
            useBaselist=args.useBaselist,
            harvest=args.harvest,
            maxHarvestedWords=args.max_harvested_words,
            verbose=args.verbose,
            silent=args.silent,
            overwriteFiles=args.overwrite_files
        )

        # normalize input file path
        config.file = os.path.abspath(os.path.expanduser(config.file))

        # Target file checks
        if not os.path.exists(config.file):
            self.parser.error(ErrorMessages.TARGET_FILE_DOES_NOT_EXIST.format(config.file))
        if not os.path.isfile(config.file) or not (config.file.lower().endswith(".txt")):
            self.parser.error(ErrorMessages.TARGET_FILE_INVALID.format(config.file))
        if os.path.getsize(config.file) == 0:
            self.parser.error(ErrorMessages.TARGET_FILE_EMPTY.format(config.file))
        
        # set the path to the default baselist if default is chosen
        if config.useBaselist and config.baselist == "default":
            script_dir = os.path.dirname(os.path.abspath(__file__))
            config.baselist = os.path.join(script_dir, "baselists", "default_baselist.txt")

        # normalize baselist path
        if config.useBaselist and config.baselist != "default":
            config.baselist = os.path.abspath(os.path.expanduser(config.baselist))
        
        # Baselist file checks
        if config.useBaselist:
            if not os.path.exists(config.baselist):
                self.parser.error(ErrorMessages.BASELINE_FILE_DOES_NOT_EXIST.format(config.baselist))
            if not os.path.isfile(config.baselist) or not (config.baselist.lower().endswith(".txt")):
                self.parser.error(ErrorMessages.BASELINE_FILE_INVALID.format(config.baselist))
            if os.path.getsize(config.baselist) == 0:
                self.parser.error(ErrorMessages.BASELINE_FILE_EMPTY.format(config.baselist))
        
        # Raise an error if there is conflict in verbosity settings
        if config.verbose and config.silent:
            self.parser.error(ErrorMessages.VERBOSITY_CONFLICT)
        
        # Raise an error if harvesting and baselist are both disabled
        if not config.harvest and not config.useBaselist:
            self.parser.error(ErrorMessages.NO_PERMUTATION_OPTIONS_SET)
        
        # for any resolver rate at or below 0 assume intention is unlimited
        if config.rateResolver <= 0 and config.resolve:
            config.rateResolver = -1
        
        # Raise an error if there are no threads available to the resolver
        if config.threadsResolver < 1 and config.resolve:
            self.parser.error(ErrorMessages.NO_RESOLVER_THREADS.format(config.threadsResolver))
        
        if config.maxHarvestedWords < 1 and config.harvest:
            self.parser.error(ErrorMessages.MAX_HARVEST_TOO_LOW.format(config.maxHarvestedWords))
        
        return config



@dataclass
class ProteusConfig:
    file: str                       # [REQUIRED] set a target file containing the subdomains to use for permutation
    baselist: str = "default"       # use a custom preset list of words for permutation. If no custom list is set proteus uses the default list.
    threadsResolver: int = 100      # dnsx threads  (default 100)
    rateResolver: int = -1          # dnsx rate limit   (default -1)
    resolve: bool = True            # use dnsx resolution   (default True)
    useBaselist: bool = True        # use a base list for permutations  (default True)
    harvest: bool = True            # Harvest words to use in permutating   (default True)
    maxHarvestedWords: int = 200    # Limit to the amount of harvested words used for permutating (default 200)
    verbose: bool = False           # Enable verbose mode (default False)
    silent: bool = False            # Enable silent mode (default False)
    overwriteFiles: bool = False    # Overwrite files if they already exist (default False)

@dataclass
class ErrorMessages:
    TARGET_FILE_DOES_NOT_EXIST = "!!!\nThe target file does not exist: {}\n!!!"
    TARGET_FILE_INVALID = "!!!\nThe target file is not a .txt file: {}\n!!!"
    TARGET_FILE_EMPTY = "!!!\nThe target file is empty: {}\n!!!"
    BASELINE_FILE_DOES_NOT_EXIST = "!!!\nThe selected baseline file does not exist: {}\n!!!"
    BASELINE_FILE_INVALID = "!!!\nThe baseline file is not a .txt file: {}\n!!!"
    BASELINE_FILE_EMPTY = "!!!\nThe baseline file is empty: {}\n!!!"
    NO_PERMUTATION_OPTIONS_SET = "!!!\nYou have disabled both the harvesting and baselist. This will leave the list of words for permutation empty, resulting in no permutation being performed. Enable harvesting, baselist, or both to continue\n!!!"
    NO_ACTIONS_SET = "!!!\nYou disabled all of the functionalities of proteus. You instructed the tool to do nothing\n!!!"
    VERBOSITY_CONFLICT = "!!!\nYou enabled both verbose and silent mode. Since these conflict, only one can be enabled at a time\n!!!"
    NO_RESOLVER_THREADS = "!!!\nYou set the resolver to use {} threads, but it requires at least 1 thread\n!!!"
    MAX_HARVEST_TOO_LOW = "!!!\nYou set the maximum harvested words to {}. This means no words will be harvested, but harvesting is not disabled. If you don't want any words to be harvested, instead turn off harvesting with --no-harvest\n!!!"
    PLACEHOLDER_ERROR = "!!!\nPLACEHOLDER ERROR MESSAGE\n!!!"