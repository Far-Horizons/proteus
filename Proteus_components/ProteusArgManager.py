import argparse
import os

from ProteusConfig import ProteusConfig, ErrorMessages


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
            help="disable harvesting of domain parts. The permutator will only use the words from the baselist [DEFAULT: enabled]"
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
            default=200,
            help="set a rate limit for the resolver (dnsx). Any negative value will be interpreted as unlimited. Note that rates over 300 may lead to rate-limiting [DEFAULT: 200]"
        )

        # Behavior
        self.parser.add_argument(
            "-mhw","--max-harvested-words",
            type=int,
            default=200,
            help="Set the maximum amount of harvested words used for permutation. All words are harvested and ranked, this just changes how many are actually used [DEFAULT: 200]"
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
        self.parser.add_argument(
            "--low-ram-mode",
            action='store_true',
            help="large lists of generated domains can cause issues when loaded into dnsx on small machines (like a 1vcpu/1gb ram VPS). This mode splits the list into parts and runs multiple, smaller dnsx cycles to solve this issue. This mode is slightly slower than the standard mode, but will allow for larger sets of data (currently not implemented) [DEFAULT: False]"
        )

        # permutation strategies (not implemented yet)
        self.parser.add_argument(
            "-ps", "--permutation-strategy",
            type=str,
            nargs="+",
            default=["simple"],
            choices=["simple", "hyphenate", "insert", "append-hyphenate", "all"],
            help="Set the permutation strategy to use. options:\nsimple (prepend the permutator to the domain, seperated by a .)\nhyphenate (prepend the permutator to the domain, separated by a -)\ninsert (insert the permutator between parts of known domains)\nall (a mix of the afformentioned strategies. Be warned: even a small list with this strategy will lead to large amount of generated domains) [DEFAULT: simple]" 
        )

        # Outputs
        self.parser.add_argument(
            "-ro", "--resolver-output",
            type=str,
            default="resolved_domains.txt",
            help="set the output file for the resolver [DEFAULT resolver_output.txt]"
        )
        self.parser.add_argument(
            "-ho", "--harvester-output",
            type=str,
            default="harvester_output.txt",
            help="set the output file for the harvester [DEFAULT harvester_output.txt]"
        )
        self.parser.add_argument(
            "-go", "--permutator-output",
            type=str,
            default="generated_domains.txt",
            help="set the output for the permutator. This file contains all of the domains generated by the permutator, including those that don't resolve [DEFAULT: generated_domains.txt]"
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
            overwriteFiles=args.overwrite_files,
            harvesterOutput=args.harvester_output,
            resolverOutput=args.resolver_output,
            permutatorOutput=args.permutator_output,
            permutationStrategy=args.permutation_strategy,
            lowRamMode=args.low_ram_mode
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
                self.parser.error(ErrorMessages.BASELIST_FILE_DOES_NOT_EXIST.format(config.baselist))
            if not os.path.isfile(config.baselist) or not (config.baselist.lower().endswith(".txt")):
                self.parser.error(ErrorMessages.BASELIST_FILE_INVALID.format(config.baselist))
            if os.path.getsize(config.baselist) == 0:
                self.parser.error(ErrorMessages.BASELIST_FILE_EMPTY.format(config.baselist))
        
        # Normalize output paths
        config.harvesterOutput = os.path.abspath(os.path.expanduser(config.harvesterOutput))
        config.resolverOutput = os.path.abspath(os.path.expanduser(config.resolverOutput))
        config.permutatorOutput = os.path.abspath(os.path.expanduser(config.permutatorOutput))
        
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
        
        # Normalize strategy selection
        config.permutationStrategy = [ps.lower() for ps in config.permutationStrategy]
        if "all" in config.permutationStrategy:
            config.permutationStrategy = ["simple", "hyphenate", "insert", "append-hyphenate"]
        elif len(config.permutationStrategy) != len(set(config.permutationStrategy)):
            config.permutationStrategy = list(set(config.permutationStrategy)) # convert to set then back to list to remove duplicates
        
        # [TODO] Still have to implement checks for if output files already exist, and if output files should be overwritten

        return config