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
        with Path(self.lang_dir / "cons_data.json").open("r", encoding='utf-8') as f:
            cons_input = json.load(f)
        with Path(self.lang_dir / "output_cons_5_food+drinks.csv").open("w", encoding='utf-8') as g:
            g.write("id;name;json_text;\n")

            for cons in cons_input:
                g.write("{id};{title};{text};\n".format(id=cons["id"], title=cons['title'], text=cons['text']))

            g.write("\n")

    def __format_cons2(self):
        with Path(self.lang_dir / "output_cons_5_food+drinks.csv").open("r", encoding='utf-8') as f:
            fileName = self.lang_dir / "output_cons_5_food+drinks2.csv"
            if fileName.exists():
                fileName.unlink()            
            
            f.readline()
            lines = f.readlines()

        keys = []
        keys.append("name_enus")
        json_objects = {}
        for line in lines:              
            if line != "\n":
                itemid = line.split(";")[0]
                line = line.split(";")[-2]
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

                cons_input = json.loads(line)
                json_objects[itemid] = cons_input
                for k,v in cons_input.items():
                    if k not in keys:
                        keys.append(k)
                    if k == "jsonequip":
                        for k2,v2 in v.items():
                            if k2 not in keys:
                                keys.append(k2)       


        with Path(fileName).open("w", encoding='utf-8') as g:  
            output = "id;"
            for key in keys:
                output = output + key + ";"
                
            g.write(output + "\n")

            for jo in json_objects.items():
                itemid = jo[0]
                if itemid == '1401':
                    itemid = itemid                   
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

