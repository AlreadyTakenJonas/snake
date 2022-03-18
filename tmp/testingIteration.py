class A:
    def __getitem__(self, index):
        if index > 5:
            raise IndexError
        return "x"

a = A()
for i in a:
    print(i)
    
#print(a[40])