import os
import re


def create_rm_charge_dict(path: str) -> dict:
    '''
    Collects all state names and respective RM U(1) charges into states_rm_dict.
    Keys are the state identifiers. Values are lists of charges as integers.
    '''
    return_dict = {}
    with open(path + r"rm.u1.all", "r") as rmu1_readfile:
        curr_file_lines = rmu1_readfile.readlines()

        for line in curr_file_lines:
            line_split = line.split("\t\t ")

            curr_state_name = line_split[0]
            curr_state_rm = line_split[1].strip()

            curr_state_rm_split = curr_state_rm.split("\t ")
            curr_state_rm_charges = tuple([int(x) for x in curr_state_rm_split])

            return_dict[curr_state_name] = curr_state_rm_charges
    
    return return_dict


def create_na_reps_dict(path: str) -> dict:
    '''
    Collects all the state names and respective NA representations into a dictionary.
    Keys are state identifiers. Values are ints symbolizing the dimensions of the representations.
    '''
    return_dict = {}
    with open(path + r"rm.na.all", "r") as rmna_readfile:
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

                # If a rep dimension is a multiple of 3,
                #   it's barred rep is equivalent.
                if x % 3 == 0 and x < 0:
                    curr_state_na.append(-1 * x)
                else:
                    curr_state_na.append(x)
            if valid_reps:
                return_dict[curr_state_name] = curr_state_na

    return return_dict

def create_reverse_rm_dict(rm_dict: dict) -> dict:
    '''
    Inverts the states_rm_dict dictionary, and consolidates  states' names
    Keys are the RM U(1) charges ; values are lists of all state names matching those charges
    '''
    inverse_dict = {}
    for key, value in rm_dict.items():
        inverse_dict.setdefault(value, []).append(key)
    
    return inverse_dict


def extract_tower_name(item: str, directory: str):
    input_file_pattern = r"2Ms[0-9]+\.EL[0-9]\.ER[0-9]\.[lr]m\.[un][1a]\.all"
    tower_name_pattern = r"2Ms[0-9]+\.EL[0-9]\.ER[0-9]\."

    item_path = os.path.join(directory, item)
    if not os.path.isfile(item_path):
        return None

    if not re.match(input_file_pattern, item):
        return None

    return re.search(tower_name_pattern, item).group()


def identify_vector_pairs(directory: str):
    prev_tower_name = ''

    for item in os.listdir(directory):
        tower_name = extract_tower_name(item)

        # We only want to process each tower once
        if tower_name and tower_name == prev_tower_name:
            continue
        prev_tower_name = tower_name

        rm_charge_dict = create_rm_charge_dict(directory + tower_name)
        na_reps_dict = create_na_reps_dict(directory + tower_name)

        # initialize variables and objects related to paired and unpaired states
        vector_pair_dict = {}
        total_pairs = 0
        num_paired_states = 0
        unpaired_vectors = []

        inverse_rm_dict = create_reverse_rm_dict(rm_charge_dict)

        # Identifies all state pairs that have RM U(1) charges that are additive inverses,
        #   and that have matching NA reps.
        # Also identifies states that have no pairs.
        for state_name, rm_charges in rm_charge_dict.items():
            # Create the target inverse values
            inverse_values = tuple([-1 * c for c in rm_charges])
            # Retrieve all state names that match the inverse values
            matching_states = inverse_rm_dict.get(inverse_values, [])

            match_found = False
            for pair_state_name in matching_states:
                if na_reps_dict[state_name] == na_reps_dict[pair_state_name]:
                    match_found = True
                    total_pairs += 1
                    vector_pair_dict.setdefault(state_name, []).append(pair_state_name)

            if not match_found:
                unpaired_vectors.append(state_name)
            else:
                num_paired_states += 1

        # writes the vector pairs to their respective output file
        with open(directory + tower_name + r"vector_pairs.txt", "w") as write_file:
            for state, pairs in vector_pair_dict.items():
                write_file.write(f"{state}:")
                for pair in pairs:
                    write_file.write(f"{pair} ")
                write_file.write('\n')
            write_file.write(f"\nTotal number of pairs: {total_pairs}")
            write_file.write(f"\nNumber of paired states: {num_paired_states}")

        # writes the unpaired vectors to their respective output file
        with open(directory + tower_name + r"up_vectors.txt", "w") as write_file:
            for state in unpaired_vectors:
                write_file.write(f"{state}\n")
            write_file.write(f"\nTotal number of unpaired states: {len(unpaired_vectors)}")


if __name__ == "__main__":
    directory = r".\\path-to-directory\\"
    identify_vector_pairs(directory)
