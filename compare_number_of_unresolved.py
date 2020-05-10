from names_and_constants import *

def compare_meta_data(file1, file2):
    f1 = open(file1)
    f2 = open(file2)
    total1 = 0
    total2 = 0
    file1_winner = 0
    file2_winner = 0
    tie = 0
    
    for line1, line2 in zip(f1.readlines(), f2.readlines()):
        res1 = int(line1.split("\t")[0])
        res2 = int(line2.split("\t")[0])
        
        total1 = total1 + int(res1)
        total2 = total2 + int(res2)
    
        if res1 < res2:
            file1_winner = file1_winner + 1
        elif res2 < res1:
            file2_winner = file2_winner + 1
        else:
            tie = tie + 1
                
    print(file1)
    print("Unresolved:", total1)
    print("Winner:", file1_winner)
    
    print()
    print(file2)
    print("Unresolved:", total2)
    print("Winner:", file2_winner)
    print()
    print("Tie:", tie)

if __name__ == "__main__":
    pass
    # TODO: Add code
