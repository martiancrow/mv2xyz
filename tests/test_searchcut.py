import re

text = "Elementum molestie vestibulum aliquam."

res = re.search(r".{0,%d}(%s).{0,%d}" % (18, "Aliquam", 18), text, flags=re.I)
#res = re.search(r"(%s)" % "Aliquam", text, flags=re.I)

print(len(text))
print(text[37])
print(res)

resspan = res.span()

print(resspan)

print(res.group())

lst = [idx for idx in range(0, 10) if idx % 2 == 0]

print(lst)

