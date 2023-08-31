def filter_states_by_sector(
        states_file_path,
        sector
):
    ret_states = []
    with open(states_file_path, "r") as read_file:
        curr_line = ' '
        while curr_line != '':
            curr_line = read_file.readline()
            if "State:" in curr_line:
                curr_line_split = curr_line.split(": ")
                curr_line_state = curr_line_split[1].replace('\n', '')

                for i in range(3):
                    curr_line = read_file.readline()

                if sector in curr_line:
                    ret_states.append(curr_line_state)
    return ret_states


def list_states_from_vps(file_path):
    states_list = []
    with open(file_path, "r") as read_file:
        curr_line = ' '
        while curr_line != '':
            curr_line = read_file.readline()
            curr_line_split = curr_line.split(", ")
            state_1 = curr_line_split[0][1:]
            state_2 = curr_line_split[1][:-1]

            states_list.append(state_1)
            states_list.append(state_2)

    return states_list


def identify_incomplete_sectors():
    sectors = []

    with open(r"2Ms1_up_vectors.txt", "r") as up_vectors_file:
        up_vector = ' '

        while up_vector != '':
            up_vector = up_vectors_file.readline()
            with open(r".\2Ms1.states\2Ms1.EL0.ER0.states.all", "r") as states_list:
                compare_line = ' '
                match_found = False

                while compare_line != '' and not match_found:
                    compare_line = states_list.readline()
                    match_found = compare_line.find(up_vector) > -1

                if match_found:
                    for i in range(3):
                        compare_line = states_list.readline()
                    if compare_line not in sectors:
                        sectors.append(compare_line)

    with open("standard_up-vector_sectors.txt", "a") as output:
        output.writelines(sectors)


def compare_up_states():
    standard_statesxsectors = {}
    standard_file_line = ' '

    with open(r".\2Ms1.states\2Ms1.EL0.ER0.states.all", "r") as standard_states_file:
        while standard_file_line != '':
            standard_file_line = standard_states_file.readline()
            if "State:" in standard_file_line:
                file_line_split = standard_file_line.split(' ')
                state_name = file_line_split[1].replace('\n', '')

                standard_file_line = standard_states_file.readline()
                standard_state = standard_file_line.replace('\n', '')
                for i in range(2):
                    standard_file_line = standard_states_file.readline()
                standard_sector = standard_file_line.replace('\n', '')

                standard_statesxsectors[state_name] = (
                    standard_state,
                    standard_sector
                )

    aminus_statesxsectors = {}
    aminus_file_line = ' '

    with open(r".\Aminus-all-modes\2Ms1.EL0.ER0.states.all", "r") as aminus_states_file:
        while aminus_file_line != '':
            aminus_file_line = aminus_states_file.readline()
            if "State:" in aminus_file_line:
                file_line_split = aminus_file_line.split(' ')
                state_name = file_line_split[1].replace('\n', '')

                aminus_file_line = aminus_states_file.readline()
                aminus_state = aminus_file_line.replace('\n', '')
                for i in range(2):
                    aminus_file_line = aminus_states_file.readline()
                aminus_sector = aminus_file_line.replace('\n', '')

                aminus_statesxsectors[state_name] = (
                    aminus_state,
                    aminus_sector
                )

    matches = []

    with open(r"2Ms1_up_vectors.txt", "r") as standard_upv_file:
        standard_upv = ' '
        while standard_upv != '':
            standard_upv = standard_upv_file.readline().strip()

            with open(r"2Ms1-Aminus_up_vectors.txt", "r") as aminus_upv_file:
                aminus_upv = ' '
                while aminus_upv != '':
                    aminus_upv = aminus_upv_file.readline().strip()

                    try:
                        if standard_statesxsectors[standard_upv][0] == \
                                aminus_statesxsectors[aminus_upv][0]:
                            matches.append(
                                ((standard_upv, standard_statesxsectors[standard_upv]),
                                 (aminus_upv, aminus_statesxsectors[aminus_upv]))
                            )
                            break
                    except KeyError:
                        continue

    up_sectors = []
    for match in matches:
        print("state:", match[0][0])
        print('\tstate:\t', match[0][1][0])
        print('\tsector:\t', match[0][1][1])
        print("state:", match[1][0])
        print('\tstate:\t', match[1][1][0])
        print('\tsector:\t', match[1][1][1], '\n')

        if match[1][1][1] not in up_sectors:
            up_sectors.append(match[1][1][1])

    print("number of matches:", len(matches))
    print("\nunpaired sectors:")
    for sector in up_sectors:
        print(sector)


def statexsector_from_name(path, name):
    current_line = ' '
    state = None
    sector = None
    with open(path, "r") as read_file:
        while current_line != '' and (state, sector) == (None, None):
            current_line = read_file.readline()

            if current_line.find(name) > -1:
                current_line = read_file.readline()
                state = current_line.strip()

                for i in range(2):
                    current_line = read_file.readline()
                sector = current_line.strip()

    return state, sector
