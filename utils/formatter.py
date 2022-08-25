import json
from msvcrt import putch
from pathlib import Path
from turtle import title

#from utils.paths import OUTPUT_DIR
from paths import OUTPUT_DIR

# BASE_DIR = Path(__file__).parent.parent
# OUTPUT_DIR = Path(BASE_DIR / "output")
# if not OUTPUT_DIR.exists():
#     OUTPUT_DIR.mkdir()

class Formatter:

    lang: str
    lang_dir: Path

    def __call__(self, lang="en", f_type="npc", **kwargs):
        self.lang = lang
        self.lang_dir = OUTPUT_DIR / lang
        if not self.lang_dir.exists():
            self.lang_dir.mkdir()

        if f_type == "npc":
            self.__format_npc_names()
        if f_type == "object":
            self.__format_object_names()
        elif f_type == "quest":
            self.__format_quests()
        elif f_type == "gem":
            self.__format_gems()
        elif f_type == "cons":
            self.__format_cons()
        elif f_type == "cons2":
            self.__format_cons2()            

    def __format_npc_names(self):
        with Path(self.lang_dir / "npc_data.json").open("r", encoding="utf-8") as f:
            npc_input = json.load(f)
            npc_input.sort(key=lambda k: int(k["id"]))
        with Path(self.lang_dir / "lookupNpcs.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name()
            g.write(table_name)

            for item in npc_input:
                name = item["name"]
                name = name.replace("'", "\\'")
                name = name.replace("\"", "\\\"")
                g.write("[{}] = \"{}\",\n".format(item["id"], name))

            g.write("}\n")

    def __format_object_names(self):
        with Path(self.lang_dir / "object_data.json").open("r", encoding="utf-8") as f:
            npc_input = json.load(f)
            npc_input.sort(key=lambda k: int(k["id"]))
        with Path(self.lang_dir / "lookupObjects.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("object")
            g.write(table_name)

            for item in npc_input:
                name = item["name"]
                if name.startswith("["):
                    continue
                name = name.replace("'", "\\'")
                name = name.replace("\"", "\\\"")
                g.write("[\"{}\"] = {},\n".format(name, item["id"]))

            g.write("}\n")

    def __format_quests(self):
        with Path(self.lang_dir / "quest_data.json").open("r", encoding="utf-8") as f:
            quest_input = json.load(f)
            quest_input.sort(key=lambda k: k["id"])
        with Path(self.lang_dir / "lookupQuests.lua").open("w", encoding="utf-8") as g:
            table_name = self.__get_table_name("quest")
            g.write(table_name)

            for item in quest_input:
                title = self.__filter_text(item["title"])
                objective = self.__filter_text(item["objective"])
                description = self.__filter_text(item["description"])

                g.write("[{id}] = {{{title}, {desc}, {obj}}},\n".format(id=item["id"], title=title,
                                                                        desc=description, obj=objective))

            g.write("}\n")

    def __format_gems(self):
        with Path(self.lang_dir / "gem_data.json").open("r", encoding="utf-8") as f:
            gems_input = json.load(f)
            gems_input.sort(key=lambda k: k["id"])
        with Path(self.lang_dir / "output_gems.csv").open("w", encoding="utf-8") as g:
            g.write("id;name;farbe;quality;\n")

            for gem in gems_input:
                g.write("{id};{title};{color};{quality}\n".format(id=gem["id"], title=gem["title"], color=gem["color"], quality=gem["quality"]))

            g.write("\n")
    
    def __format_cons(self):

        # read cons_data.json and load the json. create a export csv file for each type of consumes (0-8). changing the hard coded file name has to be done
        # manually. this is just for test purposes and not intended to work in production
        # Steps are
        # 1.) generate a list of consumes ids (like in \ids\cons_ids.py) from the item.csv (wow.tools) filtered for SubClassID and put them into the cons ids file
        # e.g. '117' : { 'classId' : 0, 'subClassId' : 5, 'material' : 0, },
        # 2.) call 'python runner.py -l de -t cons' to execute ConsumesSpider and generate the json file (comment out the call to formatter in the spider_closed function)
        # 3.) toggle comments line 6-12 in this file and call it manually to get the output csv file
        # 4.) change 
        # - the filename for the out file in __format_cons to output_cons_X_DESC.csv (X = SubClassID, DESC = short description)
        # - the input file in __format_cons2 (same)
        # - f("de", "cons") to f("de", "cons2"), 
        # then call this file again to get the final output file

        with Path(self.lang_dir / "cons_data.json").open("r", encoding='utf-8') as f:
            cons_input = json.load(f)
        with Path(self.lang_dir / "output_cons_5_food+drinks.csv").open("w", encoding='utf-8') as g:
            g.write("id;name;json_text;\n")

            for cons in cons_input:
                g.write("{id};{title};{text};\n".format(id=cons["id"], title=cons['title'], text=cons['text']))

            g.write("\n")

    def __format_cons2(self):

        # since the json is different for each consume the following only applies to SubClassID = 5
        with Path(self.lang_dir / "output_cons_5_food+drinks.csv").open("r", encoding='utf-8') as f:
            fileName = self.lang_dir / "output_cons_5_food+drinks2.csv"
            if fileName.exists():
                fileName.unlink()            
            
            f.readline()
            lines = f.readlines()

        # empty list of possible attributes consumes can have
        keys = []
        # some items don't have a 'name_dede' attribute in their json representation. to fix this add this prop manually
        keys.append("name_enus")
        # dict for the json_objects
        json_objects = {}
        for line in lines:              
            if line != "\n":
                # split the line by semicolon: '{id};{title};{text};\n',
                itemid = line.split(";")[0]
                line = line.split(";")[-2]
                # this part is the most tedious, since json requires string literals to have double quotes instead of single and the
                # export only has single quoted strings, those have to be replaced. but unluckily some items contain single quotes in their
                # name which would interfer with ending a string with double quotes. so after replacing ' with " the following part takes
                # care of reversing this change for all the special cases like Tel"Abim -> Tel'Abim to maintain string delimination
                line = line.replace("'", '"')
                line = line.replace("Tel\"Abim", "Tel'Abim")
                line = line.replace("\"Grimmigen Säufer\"", "'Grimmigen Säufer'")
                line = line.replace("Un\"Goro", "Un'Goro")
                line = line.replace("Mag\"har", "Mag'har")               
                line = line.replace("Mok\"Nathal", "Mok'Nathal")
                line = line.replace("Ogri\"la", "Ogri'la")
                line = line.replace("\"Tiefenladung\"", "'Tiefenladung'")    
                line = line.replace("Glyphe \"Pinguin\"", "Glyphe 'Pinguin'")   
                line = line.replace("Glyphe \"Naturkraft\" [PH]", "Glyphe 'Naturkraft' [PH]") 
                line = line.replace("Star\"s Lament", "Star's Lament")                              

                # each line has a json associated, convert this into json object and store it in the json_objects dict with item id as key
                # then loop over it and store the prop name in the list of keys (if not already existing)
                # every json has a prop called 'jsonequip which is a js object itself -> sub values have to be added too
                cons_input = json.loads(line)
                json_objects[itemid] = cons_input
                for k,v in cons_input.items():
                    if k not in keys:
                        keys.append(k)
                    if k == "jsonequip":
                        for k2,v2 in v.items():
                            if k2 not in keys:
                                keys.append(k2)       

        # all the lines are now stored as js objects in json_objects
        # every possible prop is now listed in keys[]
        # next step is to create the output csv file that consists of item id, name and a colum for each prop + associated value:
        # 0.) write head line with semicolon separated values (all the possible keys) and setting it to empty-string
        # 1.) loop over every entry in json_objects
        # 2.) create temp dict and insert all keys[] 
        # 3.) loop over the current entry's attributes and insert the value to the matching item in the output js object
        # 3.1) if the current entry's attribute is jsonequip then just add the while stringifyed content and iterate over the subelements
        # 4.) generate a output string starting with itemid and append delimiter ';' and the values from jo_out
        with Path(fileName).open("w", encoding='utf-8') as g:  
            output = "id;"
            for key in keys:
                output = output + key + ";"
                
            g.write(output + "\n")

            for jo in json_objects.items():
                itemid = jo[0]             
                jo_out = {}
                for key in keys:
                    jo_out[key] = ""

                for k,v in jo[1].items():
                    jo_out[k] = v
                    if k == "jsonequip":
                        for k2, v2 in v.items():
                            jo_out[k2] = v2
             
                output = itemid + ";"
                for k,v in jo_out.items():
                    output = output + str(v) + ";"

                g.write(output + "\n")                

            g.write("\n")        

    def __get_table_name(self, target="npc"):
        lang = self.lang
        if target == "npc":
            table_name = "LangNameLookup['{}'] = {{\n"
        elif target == "object":
            table_name = "\nLangObjectLookup['{}'] = {{\n"
        elif target == "quest":
            table_name = "\nLangQuestLookup['{}'] = {{\n"

        if lang == "en":
            return table_name.format("enUS")
        elif lang == "de":
            return table_name.format("deDE")
        elif lang == "fr":
            return table_name.format("frFR")
        elif lang == "es":
            return table_name.format("esES")
        elif lang == "ru":
            return table_name.format("ruRU")
        elif lang == "cn":
            return table_name.format("zhCN")
        elif lang == "pt":
            return table_name.format("ptBR")
        else:
            raise ValueError("Language '{}' not supported for formatting!".format(lang))

    @staticmethod
    def __filter_text(text):
        text = text.replace("\\", "")
        text = text.replace("'", "\\'")
        text = text.replace("\"", "\\\"")
        if text:
            text = "'" + text + "'"
        else:
            text = "nil"
        return text


if __name__ == '__main__':
    f = Formatter()
    #f("de", "cons")
    # f("pt", "quest")
    f("de", "cons")

