import os
import subprocess
import math

from ProteusConfig import ProteusConfig, ErrorMessages


class ProteusResolver:
    def __init__(self, config: ProteusConfig):
        self.config = config
        self.lowram_entry_limit = 1000000   # 1 million
    
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
    
    # Low-ram version of the resolve method
    def lr_resolve(self):
        if not os.path.exists(self.config.permutatorOutput) or os.path.getsize(self.config.permutatorOutput) == 0:
            raise ValueError(ErrorMessages.RESOLVER_NO_TARGETS)

        if not self.config.silent:
            print(f"splitting the file of generated domains into files of {self.lowram_entry_limit} lines")

        with open(self.config.permutatorOutput, "r") as f:
            file_count = 0
            buffer = []

            for line in f:
                buffer.append(line)

                if len(buffer) >= self.lowram_entry_limit:
                    file_count += 1
                    with open(f"lowram_resolver_split_{file_count}.txt", "w") as out:
                        out.writelines(buffer)
                    
                    buffer.clear()
            
            if buffer:
                file_count += 1
                with open(f"lowram_resolver_split_{file_count}.txt", "w") as out:
                        out.writelines(buffer)

        if not self.config.silent:
            print(f"splitting succeeded, generated {file_count} file(s)")

        for i in range(file_count):
            if not self.config.silent:
                print(f"starting resolver cycle {i + 1} of {file_count}")

            subprocess.run(
                ["dnsx",
                "-l", f"lowram_resolver_split_{i + 1}.txt",
                "-a", "-stats",
                "-o", f"lowram_resolver_output_{i + 1}.txt",
                "-t", f"{self.config.threadsResolver}",
                "-rl", f"{self.config.rateResolver}"],
                check=True)
        
        if not self.config.silent:
            print("completed all resolver cycles, merging the files")

        output = set()
        for j in range(file_count):
            with open(f"lowram_resolver_output_{j + 1}.txt", "r") as f:
                for line in f:
                    output.add(line)
        
        with open(f"{self.config.resolverOutput}", "w") as f:
            f.writelines(output)
        
        if not self.config.silent:
            print("finsihed merging the files, cleaning up extra files")
        
        for x in range(file_count):
            os.remove(f"lowram_resolver_split_{x + 1}.txt")
            os.remove(f"lowram_resolver_output_{x + 1}.txt")

        if not self.config.silent:
            print("cleanup completed")


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
