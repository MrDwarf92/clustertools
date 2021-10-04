def file_preparation(file):
    f = open(file,'r+')
    lines = f.readlines()
    f.close()

    if (lines[10])[:7] != 'Cluster':
        lines[10] = 'Cluster' + lines[10]
        f = open(file,'r+')
        for i in range(len(lines)):
            f.write(lines[i])
        f.close()


    f.close()
