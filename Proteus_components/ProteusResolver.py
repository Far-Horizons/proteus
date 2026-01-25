import os
import subprocess
import math

from ProteusConfig import ProteusConfig, ErrorMessages


class ProteusResolver:
    def __init__(self, config: ProteusConfig):
        self.config = config
    
    def resolve(self):
        if not os.path.exists(self.config.permutatorOutput) or os.path.getsize(self.config.permutatorOutput) == 0:
            raise ValueError(ErrorMessages.RESOLVER_NO_TARGETS)

        subprocess.run(
            ["dnsx",
             "-l", f"{self.config.permutatorOutput}",
             "-a", "-stats",
             "-o", f"{self.config.resolverOutput}",
             "-t", f"{self.config.threadsResolver}",
             "-rl", f"{self.config.rateResolver}"],
             check=True
        )
    
    def print_resolve_time(self):
        if not os.path.exists(self.config.permutatorOutput):
            raise FileNotFoundError(ErrorMessages.GENERATED_FILE_DOES_NOT_EXIST.format(self.config.permutatorOutput))
        
        if self.config.rateResolver < 1:
            print("unable to do a time estimate, as the rate is unlimited")
            return
        
        with open(self.config.permutatorOutput, "r") as f:
            lines = sum(1 for _ in f)
        
        resolve_time_minimum =  math.ceil(lines / self.config.rateResolver)
        
        resolve_hours = resolve_time_minimum // 3600
        resolve_remaining = resolve_time_minimum % 3600
        resolve_minutes = resolve_remaining // 60
        resolve_seconds = resolve_remaining % 60

        resolve_estimate = ""
        if resolve_hours > 0:
            resolve_estimate += f"hours: {resolve_hours}"
        if resolve_minutes > 0:
            if resolve_estimate != "":
                resolve_estimate += ", "
            resolve_estimate += f"minutes: {resolve_minutes}"
        if resolve_seconds > 0:
            if resolve_estimate != "":
                resolve_estimate += ", "
            resolve_estimate += f"seconds: {resolve_seconds}"

        print(f"Estimated time to attempt resolving all generated domains ({lines}) is: {resolve_estimate}. This estimate is assuming that the resolver runs at the maximum set rate of {self.config.rateResolver} the whole time, which may not be true if dnsx is bottlenecked by assigned threads, bandwith, or rate-limiting")
