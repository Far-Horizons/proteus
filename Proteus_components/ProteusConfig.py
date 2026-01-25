from dataclasses import dataclass


@dataclass
class ProteusConfig:
    file: str                                       # [REQUIRED] set a target file containing the subdomains to use for permutation
    baselist: str = "default"                       # use a custom preset list of words for permutation. If no custom list is set proteus uses the default list.
    threadsResolver: int = 100                      # dnsx threads  (default 100)
    rateResolver: int = 200                         # dnsx rate limit   (default 200)
    resolve: bool = True                            # use dnsx resolution   (default True)
    useBaselist: bool = True                        # use a base list for permutations  (default True)
    harvest: bool = True                            # Harvest words to use in permutating   (default True)
    maxHarvestedWords: int = 200                    # Limit to the amount of harvested words used for permutating (default 200)
    verbose: bool = False                           # Enable verbose mode (default False)
    silent: bool = False                            # Enable silent mode (default False)
    overwriteFiles: bool = False                    # Overwrite files if they already exist (default False)
    harvesterOutput: str = "harvester_output.txt"   # harvester output file (default harvester_output.txt)
    resolverOutput: str = "resolved_domains.txt"    # resolver output file (default resolved_domains.txt)
    permutatorOutput: str = "generated_domains.txt" # permutator output file (default generated_domains.txt)
    permutationStrategy: str = "simple"             # permutation strategy to use (default simple)

@dataclass
class ErrorMessages:
    TARGET_FILE_DOES_NOT_EXIST = "!!!\nThe target file does not exist: {}\n!!!"
    TARGET_FILE_INVALID = "!!!\nThe target file is not a .txt file: {}\n!!!"
    TARGET_FILE_EMPTY = "!!!\nThe target file is empty: {}\n!!!"
    BASELIST_FILE_DOES_NOT_EXIST = "!!!\nThe selected baseline file does not exist: {}\n!!!"
    BASELIST_FILE_INVALID = "!!!\nThe baseline file is not a .txt file: {}\n!!!"
    BASELIST_FILE_EMPTY = "!!!\nThe baseline file is empty: {}\n!!!"
    NO_PERMUTATION_OPTIONS_SET = "!!!\nYou have disabled both the harvesting and baselist. This will leave the list of words for permutation empty, resulting in no permutation being performed. Enable harvesting, baselist, or both to continue\n!!!"
    NO_ACTIONS_SET = "!!!\nYou disabled all of the functionalities of proteus. You instructed the tool to do nothing\n!!!"
    VERBOSITY_CONFLICT = "!!!\nYou enabled both verbose and silent mode. Since these conflict, only one can be enabled at a time\n!!!"
    NO_RESOLVER_THREADS = "!!!\nYou set the resolver to use {} threads, but it requires at least 1 thread\n!!!"
    MAX_HARVEST_TOO_LOW = "!!!\nYou set the maximum harvested words to {}. This means no words will be harvested, but harvesting is not disabled. If you don't want any words to be harvested, instead turn off harvesting with --no-harvest\n!!!"
    FILE_ALREADY_EXISTS = "!!!\nThe file {} already exists. Either select a different name for this output file, or enable file overwriting\n!!!"
    RESOLVER_NO_TARGETS = "!!!\nSomething went wrong! The resolver did not receive any targets\n!!!"
    GENERATED_FILE_DOES_NOT_EXIST = "!!!\nThe file containing the generated domains does not exist: {}\n!!!"
    PLACEHOLDER_ERROR = "!!!\nPLACEHOLDER ERROR MESSAGE\n!!!"