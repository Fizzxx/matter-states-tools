
DIRECTORY = r"..\latest output 5-2023"


def identify_vector_pairs(directory: str):
    states_rm_dict = {}
    states_na_dict = {}

    # Collects all states and respective RM U(1) charges into states_rm_dict
    #   keys are the state names/numbers ; values are lists of charges as integers
    with open(directory + r"\2Ms1.EL0.ER0.rm.u1.all", "r") as rmu1_readfile:
        curr_file_lines = rmu1_readfile.readlines()

        for line in curr_file_lines:
            line_split = line.split("\t\t ")

            curr_state_name = line_split[0]
            curr_state_rm = line_split[1].strip()

            curr_state_rm_split = curr_state_rm.split("\t ")
            curr_state_rm_charges = tuple([int(x) for x in curr_state_rm_split])

            states_rm_dict[curr_state_name] = curr_state_rm_charges

    # Collects all the states and respective NA reps in states_na_dict
    #   keys are state names/numbers ; values are strings of the reps
    with open(directory + r"\2Ms1.EL0.ER0.rm.na.all", "r") as rmna_readfile:
        curr_file_lines = rmna_readfile.readlines()

        for line in curr_file_lines:
            line_split = line.split("\t\t")

            curr_state_name = line_split[0]
            curr_state_na = []
            valid_reps = True
            for x in line_split[1].split(" \t")[:-1]:
                try:
                    x = int(x.strip())
                except ValueError:
                    valid_reps = False
                    break
                if x % 3 == 0 and x < 0:
                    curr_state_na.append(-1 * x)
                else:
                    curr_state_na.append(x)
            if valid_reps:
                states_na_dict[curr_state_name] = curr_state_na

    # initialize variables and objects related to paired and unpaired states
    vp_dict = {}
    total_pairs = 0
    num_paired_states = 0
    inverse_dict = {}
    up_vectors = []

    # inverts the states_rm_dict dictionary, and consolidates  states' names
    #   keys are the RM U(1) charges ; values are lists of all state names matching those charges
    for key, value in states_rm_dict.items():
        inverse_dict.setdefault(value, []).append(key)

    # identifies all state pairs that have rm u(1) charges that are additive inverses
    #   and that have matching NA reps.
    # also identifies states that have no pairs.
    for key_1, value_1 in states_rm_dict.items():
        inverse_value = tuple([-1 * i for i in value_1])
        matching_keys = inverse_dict.get(inverse_value, [])

        match_found = False
        for key_2 in matching_keys:
            if states_na_dict[key_1] == states_na_dict[key_2]:
                match_found = True
                total_pairs += 1
                vp_dict.setdefault(key_1, []).append(key_2)

        if not match_found:
            up_vectors.append(key_1)
        else:
            num_paired_states += 1

    # writes the vector pairs to their respective output file
    with open(r"2Ms1.EL0.ER0-vector_pairs.txt", "w") as write_file:
        for key, values in vp_dict.items():
            write_file.write(f"{key}:")
            for value in values:
                write_file.write(f"{value} ")
            write_file.write('\n')
        write_file.write(f"\nTotal number of pairs: {total_pairs}")
        write_file.write(f"\nNumber of paired states: {num_paired_states}")

    # writes the unpaired vectors to their respective output file
    with open(r"2Ms1.EL0.ER0-up_vectors.txt", "w") as write_file:
        for vec in up_vectors:
            write_file.write(f"{vec}\n")
        write_file.write(f"\nTotal number of unpaired states: {len(up_vectors)}")


if __name__ == "__main__":
    identify_vector_pairs(DIRECTORY)
