####################################################################
#                                                                  #
# Script which merges two text files with each containing a        #
# column of texts. It merges the files row by row and adds a       #
# a the ; separator                                                #
#                                                                  #
####################################################################


# input files
input_1, input_2 = "spanish.txt", "german.txt"
# output file
file_to_write = "merged.txt"


if __name__ == "__main__":

    vocab = ""

    with open(input_1, encoding="utf8") as f:
        content_1 = [v.replace("\n", "") for v in f.readlines()]
    
    with open(input_2, encoding="utf8") as f:
        content_2 = [v.replace("\n", "") for v in f.readlines()]

    if(len(content_1) != len(content_2)):
        raise Exception(f"The number of vocabulary does not match in the file: {len(content_1)} != {len(content_2)}")

    vocab = [f"{v1};{v2}" for v1, v2 in zip(content_1, content_2)]

    with open(file_to_write, encoding="utf8", mode="w+") as f:
        f.write("\n".join(vocab))