from . import misc_parsing_tools as mpt


def group_vp_by_sector():
    paired_states = []
    unpaired_states = []

    target_sector = "4  4  4  0  0  4  0  0  4  0  0  4  0  0  4  0  0  4  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  " \
                    "0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0  0 "

    s_sector_state_names = mpt.filter_states_by_sector(states_file_path=r".\2Ms1.states\2Ms1.EL0.ER0.states.all", sector=target_sector)

    with open(r"2Ms1.EL0.ER0-up_vectors.txt", "r") as up_vectors_file:
        up_vector_file_lines = up_vectors_file.readlines()
        for state in s_sector_state_names:
            if state in up_vector_file_lines:
                unpaired_states.append(state)
            else:
                paired_states.append(state)

    vp_dict = {}
    with open(r"2Ms1.EL0.ER0-vector_pairs.txt", "r") as vp_file:
        vp_file_lines = vp_file.readlines()
        for line in vp_file_lines:
            try:
                line_split = line.split(':')
                line_state = line_split[0]
                state_pairs = line_split[1].strip().split(' ')

                vp_dict[line_state] = state_pairs
            except IndexError:
                continue

    all_states_dict = {}
    with open(r".\2Ms1.states\2Ms1.EL0.ER0.states.all") as all_states_file:
        curr_line = ' '
        while curr_line != '':
            curr_line = all_states_file.readline()
            if "State:" in curr_line:
                curr_line_split = curr_line.split(': ')
                curr_name = curr_line_split[1].strip()

                curr_line = all_states_file.readline()
                curr_state = curr_line.replace('\n', '')

                all_states_dict[curr_name] = curr_state

    with open(r"2Ms1.EL0.ER0_S-sector_pairs.txt", "w") as output_file:
        for name in s_sector_state_names:
            pairs = [name]
            for pair in vp_dict[name]:
                pairs.append(pair)

            for pair in pairs:
                if pair == name:
                    output_file.write(f"\t{pair}\n")
                    output_file.write(all_states_dict[pair])
                    output_file.write('\n')
                else:
                    output_file.write(pair)
                    output_file.write('\n')
                    output_file.write(all_states_dict[pair])
                    output_file.write('\n')
            output_file.write("\n\n")


if __name__ == "__main__":
    group_vp_by_sector()
