class Validator:
    ILLEGAL_STRINGS = {'ῤ': None, '᾿Α': 'Ἀ', '῾Ε': 'Ἐ', '῾Η': 'Ἡ', '῾Ι': 'Ἰ', '῾Ρ': 'Ῥ'}
    def validate(self, word):
        for illegal in self.ILLEGAL_STRINGS.keys():
            if illegal in word:
                if self.ILLEGAL_STRINGS[illegal]:
                    return f"{illegal} that should be replaced by {self.ILLEGAL_STRINGS[illegal]}"
                else:
                    return f"{illegal}"
        return True
