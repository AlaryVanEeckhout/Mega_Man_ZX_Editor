# reader and writer of the preferences.ini file
import os.path
import re

info_name = "[INFO] "
PRINTCOLOR_HEADER = '\033[95m' #purple
PRINTCOLOR_OKBLUE = '\033[94m'
PRINTCOLOR_OKCYAN = '\033[96m'
PRINTCOLOR_OKGREEN = '\033[92m'
PRINTCOLOR_WARNING = '\033[93m' #yellow
PRINTCOLOR_FAIL = '\033[91m' #red
PRINTCOLOR_ENDC = '\033[0m'
PRINTCOLOR_BOLD = '\033[1m'
PRINTCOLOR_UNDERLINE = '\033[4m'

def write(obj: object):
    with open("preferences.ini", "w") as my_file:
        my_file.write(
f"""[SETTINGS]
theme_index={obj.theme_index}
displayBase={obj.displayBase}
displayAlphanumeric={obj.displayAlphanumeric}
[MISC]
firstLaunch={obj.firstLaunch}"""
        )
    print(info_name + PRINTCOLOR_OKCYAN + "wrote to ini file." + PRINTCOLOR_ENDC)

def read(obj: object, sec="ALL_SECTIONS", inc: list[str]=[], exc: list[str]=[], property_type="string"): # load preferences into program
    if os.path.exists("preferences.ini"):
        print(info_name + PRINTCOLOR_OKGREEN + "ini file found." + PRINTCOLOR_ENDC)
        print(info_name + "reading values in \"" + property_type + "\" mode.")
        init_file = {}
        init_file_section = ""
        with open("preferences.ini", "r") as my_file:
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
                    if (not inc or property_name in inc) and not (property_name in exc): # inc/exc logic
                        if property_type == "string":
                            setattr(obj, property_name, property_value)
                        elif property_type == "bool":
                            #print(info_name + str(getattr(obj, property_name)) + "=" + property_value)
                            setattr(obj, property_name, property_value == "True")
                        elif property_type == "int":
                            if not (property_value == str(re.findall("([0-9]+)", property_value)[0] + "." + re.findall("([0-9]+)", property_value)[int(len(re.findall("([0-9]+)", property_value)) - 1)]) or str.isnumeric(property_value)):
                                print(info_name + PRINTCOLOR_FAIL + "corruption found in ini file at property: " + property_name + PRINTCOLOR_ENDC)
                                #print(property_value)
                                #print(str(re.findall("([0-9]+)", property_value)))
                                #print(str(re.findall("([0-9]+)", property_value)[0] + "." + re.findall("([0-9]+)", property_value)[1]))
                                print(info_name + PRINTCOLOR_FAIL + "load aborted." + PRINTCOLOR_ENDC)
                                return
                            #print(info_name + str(getattr(obj, property_name)) + "=" + property_value)
                            setattr(obj, property_name, int(float(property_value)))
                        elif property_type == "array2d int":
                            if not (property_value == str(re.findall("([0-9]+)", property_value)[0] + "." + re.findall("([0-9]+)", property_value)[int(len(re.findall("([0-9]+)", property_value)) - 1)]) or str.isnumeric(property_value)):
                                print(info_name + PRINTCOLOR_FAIL + "corruption found in ini file at property: " + property_name + PRINTCOLOR_ENDC)
                                print(info_name + PRINTCOLOR_FAIL + "load aborted." + PRINTCOLOR_ENDC)
                                return
                            getattr(obj, property_name[:property_name.index("[")])[int(property_name[property_name.index("[")+1:property_name.index("]")])][int(property_name[property_name.index("[")+4:-1])] = int(float(property_value))
                            #print(info_name + property_name[property_name.index("[")+1:property_name.index("]")])
                            #print(info_name + property_name[property_name.index("[")+4:-1])
                        print(info_name + property_name + "=" + property_value)
        if not sec in init_file:
            print(info_name + PRINTCOLOR_WARNING + "could not find section \"" + sec + "\" in ini file." + PRINTCOLOR_ENDC)
            print(info_name + PRINTCOLOR_OKCYAN + "loading attempt ended." + PRINTCOLOR_ENDC)
            return
        elif not section_value.items():
            print(info_name + PRINTCOLOR_WARNING + "could not find properties in section: " + sec + PRINTCOLOR_ENDC)
            print(info_name + PRINTCOLOR_OKCYAN + "loading attempt ended." + PRINTCOLOR_ENDC)
            return
        print(info_name + PRINTCOLOR_OKGREEN + "finished loading." + PRINTCOLOR_ENDC)
    else:
        print(info_name + PRINTCOLOR_WARNING + "couldn't read ini file as it doesn't exist at the moment." + PRINTCOLOR_ENDC)