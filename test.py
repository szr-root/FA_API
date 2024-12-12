dat = ['1', '2', '3', '0.1', '0.2', '0.3']
for item in dat:
    if item.startswith('0'):
        dat.remove(item)
print(dat)
