import os
import sys

def check_file_path(file_):
    assert file_ is not None
    if os.path.exists(file_):
        return file_
    else:
        print('Invalid file path')
        return None

def check_arg():
    try:
        file_ = sys.argv[2]
        return file_
    except Exception as e:
        print("Syntax: *.py <[add]|[remove]> <file>")
        sys.exit()

def strip_two_char(file_):
    assert file_ is not None
    strip_command = "sed '$s/..$//'" + " " + file_
    os.system(strip_command)
    confirm_ = input("Are you satisfied with the preview? (y/n): ").strip()
    if confirm_ == "y":
        strip_command = "sed -i '$s/..$//'" + " " + file_
        os.system(strip_command)
        print("Final Result: ")
        cat_command = "cat " + file_
        os.system(cat_command)
    else:
        print("You cancelled. No changes were made.")

def add_two_char(file_):
    assert file_ is not None
    with open(file_, 'r') as open_file:
        data = open_file.readlines()
        data = data[0].rstrip('\n')
        print(data)
    add_ = input("What do you want to add?: ").strip()
    new_data = data + add_
    print(new_data)
    confirm_ = input("Are you satisfied with the preview? (y/n): ").strip()
    if confirm_ == "y":
        add_command = "echo -n " + new_data + " > " + file_
        os.system(add_command)

def get_action():
    try:
        action_ = sys.argv[1]
        return action_
    except Exception as e:
        print("Syntax: *.py <[add]|[remove]> <file>")
        sys.exit()

if __name__ == "__main__":
    action_ = get_action()
    file_ = check_arg()
    file_ = check_file_path(file_)
    if action_ == "remove":
        strip_two_char(file_)
    elif action_ == "add":
        add_two_char(file_)


