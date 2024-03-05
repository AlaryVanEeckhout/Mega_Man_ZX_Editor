import os.path
import re

def write_preferences(obj: object):
    with open("preferences.txt", "w") as my_file:
        my_file.write(
f"""[SETTINGS]
theme_switch={obj.theme_switch}""")

def load_preferences(obj: object, sec="ALL_SECTIONS", inc: list[str]=[], exc: list[str]=[], struct="string"):
    info_name = "[INFO] "
    PRINTCOLOR_HEADER = '\033[95m'
    PRINTCOLOR_OKBLUE = '\033[94m'
    PRINTCOLOR_OKCYAN = '\033[96m'
    PRINTCOLOR_OKGREEN = '\033[92m'
    PRINTCOLOR_WARNING = '\033[93m'
    PRINTCOLOR_FAIL = '\033[91m'
    PRINTCOLOR_ENDC = '\033[0m'
    PRINTCOLOR_BOLD = '\033[1m'
    PRINTCOLOR_UNDERLINE = '\033[4m'
    if os.path.exists("preferences.txt"):
        print(info_name + PRINTCOLOR_OKCYAN + "initfile found." + PRINTCOLOR_ENDC)
        print(info_name + "reading values in \"" + struct + "\" mode.")
        init_file = {}
        init_file_section = ""
        with open("preferences.txt", "r") as my_file:
            for line in my_file:
                line = line.removesuffix("\n")
                if line and line[0] == "[":
                    init_file_section = line[1:-1]
                    init_file[init_file_section] = {}
                elif init_file_section == "" or "=" not in line:
                    print(info_name + PRINTCOLOR_FAIL + "file empty or corrupted." + PRINTCOLOR_ENDC)
                    print(info_name + PRINTCOLOR_FAIL + "load aborted." + PRINTCOLOR_ENDC)
                    return
                else:
                    init_file[init_file_section][line[:line.index("=")]] = line[line.index("=")+1:]

        for section_name, section_value in init_file.items():
            if sec == section_name or sec == "ALL_SECTIONS":
                print(info_name + "Section: " + section_name)
            for property_name, property_value in section_value.items():
                if sec == section_name or sec == "ALL_SECTIONS":
                    if (not inc or property_name in inc) and not (property_name in exc):
                        if struct == "string":
                            setattr(obj, property_name, property_value)
                        elif struct == "bool":
                            #print(info_name + str(getattr(obj, property_name)) + "=" + property_value)
                            if property_value == "True":
                                setattr(obj, property_name, True)
                            else:
                                setattr(obj, property_name, False)
                        elif struct == "int":
                            if not (property_value == str(re.findall("([0-9]+)", property_value)[0] + "." + re.findall("([0-9]+)", property_value)[int(len(re.findall("([0-9]+)", property_value)) - 1)]) or str.isnumeric(property_value)):
                                print(info_name + PRINTCOLOR_FAIL + "corruption found in initfile at property: " + property_name + PRINTCOLOR_ENDC)
                                #print(property_value)
                                #print(str(re.findall("([0-9]+)", property_value)))
                                #print(str(re.findall("([0-9]+)", property_value)[0] + "." + re.findall("([0-9]+)", property_value)[1]))
                                print(info_name + PRINTCOLOR_FAIL + "load aborted." + PRINTCOLOR_ENDC)
                                return
                            #print(info_name + str(getattr(obj, property_name)) + "=" + property_value)
                            setattr(obj, property_name, int(float(property_value)))
                        elif struct == "array2d int":
                            if not (property_value == str(re.findall("([0-9]+)", property_value)[0] + "." + re.findall("([0-9]+)", property_value)[int(len(re.findall("([0-9]+)", property_value)) - 1)]) or str.isnumeric(property_value)):
                                print(info_name + PRINTCOLOR_FAIL + "corruption found in initfile at property: " + property_name + PRINTCOLOR_ENDC)
                                print(info_name + PRINTCOLOR_FAIL + "load aborted." + PRINTCOLOR_ENDC)
                                return
                            getattr(obj, property_name[:property_name.index("[")])[int(property_name[property_name.index("[")+1:property_name.index("]")])][int(property_name[property_name.index("[")+4:-1])] = int(float(property_value))
                            #print(info_name + property_name[property_name.index("[")+1:property_name.index("]")])
                            #print(info_name + property_name[property_name.index("[")+4:-1])
                        print(info_name + property_name + "=" + property_value)
        if not sec in init_file:
            print(info_name + PRINTCOLOR_WARNING + "could not find section \"" + sec + "\" in initfile." + PRINTCOLOR_ENDC)
            print(info_name + PRINTCOLOR_OKCYAN + "loading attempt ended." + PRINTCOLOR_ENDC)
            return
        elif not section_value.items():
            print(info_name + PRINTCOLOR_WARNING + "could not find properties in section: " + sec + PRINTCOLOR_ENDC)
            print(info_name + PRINTCOLOR_OKCYAN + "loading attempt ended." + PRINTCOLOR_ENDC)
            return
        print(info_name + PRINTCOLOR_OKGREEN + "finished loading." + PRINTCOLOR_ENDC)
    else:
        print(info_name + PRINTCOLOR_WARNING + "couldn't read initfile as it doesn't exist at the moment." + PRINTCOLOR_ENDC)