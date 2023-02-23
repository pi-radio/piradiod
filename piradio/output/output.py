from prompt_toolkit import print_formatted_text

class PiOutput:
    def __init__(self):
        pass

    def error(self, s):
        print_formatted_text(f"ERROR: {s}")
    
    def warn(self, s):
        print_formatted_text(f"WARNING: {s}")
    
    def info(self, s):
        print_formatted_text(s)
    
    def print(self, s):
        print_formatted_text(s)

    def debug(self, s):
        if False:
            print_formatted_text(s)

output = PiOutput()
