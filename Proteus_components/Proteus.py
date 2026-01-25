#!/usr/bin/env python3

from ProteusArgManager import ProteusArgManager
from ProteusHarvester import ProteusHarvester
from ProteusPermutator import ProteusPermutator
from ProteusResolver import ProteusResolver


def main():
    arg_manager = ProteusArgManager()
    config = arg_manager.parse()

    if not config.silent:
        print("starting proteus")

    if config.harvest:
        if not config.silent:
            print("harvesting words")
        harvester = ProteusHarvester(config)
        harvester.harvest()
        harvester.write_harvest_ranking()
    
    if not config.silent:
        print("permutating domains")
    permutator = ProteusPermutator(config)
    if config.harvest:
        permutator.build_permutator_list(harvester.get_harvested_words())
    else:
        permutator.build_permutator_list()
    permutator.read_input_domains()
    permutator.permutate()
    permutator.write_generated_domains()

    if config.resolve:
        if not config.silent:
            print("resolving generated domains")
        resolver = ProteusResolver(config)
        resolver.print_resolve_time()
        resolver.resolve()
    
    if not config.silent:
        print("proteus completed")
    
if __name__ == "__main__":
    main()