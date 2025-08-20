from random import randint
random_id = list(set([10000000000000+randint(0, 100000000) for i in range(100000)]))
with open("random_id.txt", "w") as random_idd:
    random_idd.write("\n".join(map(str, random_id)))