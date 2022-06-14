class Reference:
    def __init__(self, section, subsection, line):
        self.section = section
        self.subsection = subsection
        self.line = line

    def nice_print(self):
        return f"{self.subsection} ({self.section}.{self.line})"

    def __str__(self):
        return self.nice_print()
