r = 0.1

i0 = 100.0
n0 = 2
i1 = 100.0
n1 = 1

i01 = i0 * (1 + r)
i0f = i0 * (1 + r)**n0

i1f = i1 * (1 + r)**n1

print(i0f/i0 - 1)
print(i0*r/i0)
print(((i01-i0))/i0)
print(((i0f-i01))/i01)
print(((i0f-i01))/i01 + ((i01-i0))/i0)

print((i0f+i1f)/(i0+i1) - 1)

