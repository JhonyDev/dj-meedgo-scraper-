# str = "ab1cd1cef"
# Index = 3
# print(str.replace(str[-1], "", 1))

import gender_guesser.detector as gender

d = gender.Detector()
print(d.get_gender(u"Shabir"))

print(d.get_gender(u"Maryam"))

print(d.get_gender(u"Anisa"))  # should be androgynous
print(d.get_gender(u"Asim"))  # should be androgynous
