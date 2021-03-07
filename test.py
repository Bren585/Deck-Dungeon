foo = (2, 3, 6, 7)
bar = (1, 4, 5, 8)

def addArray(foo, bar):
    if len(foo) != len(bar) : return
    hold = []
    for i in range(0, len(foo)):
        hold.append(foo[i] + bar[i])
    return hold

print(addArray(foo, bar))