from base64 import b64encode 
from collections import defaultdict
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

def process(img, type = "png"):
    filex = BytesIO()
    if type == "png":
        img.save(filex, "PNG")
        into = "png"
    else:
        img[0].save(fp=filex, format='GIF', append_images=img[1:], save_all=True, duration=type, loop=0)
        into = "gif"
    # display trick derived from https://stackoverflow.com/questions/26649716/how-to-show-pil-image-in-ipython-notebook/32108899#32108899
    return f"data:image/{into};base64,{b64encode(filex.getvalue()).decode('utf-8')}"

def super_simple_example(school_capacities, students, schools):
    img = Image.new("RGBA", (450, max(40 * students, 80 * schools)), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("OpenSansEmoji.ttf", 10)
    for student in range(students):
        draw.ellipse((0, 40 * student, 30, 30 + 40 * student), fill = (18, 137, 222, 255))
        draw.text((13, 40 * student + 10), str(student + 1), font = font)

    for school in range(schools):
        draw.rectangle((250, 12 + 80 * school, 435, 48 + 80 * school), fill = (136, 255, 136, 255))
        draw.text((253, 80 * school + 12), "Program " + str(school + 1), font = font, fill = (0, 0, 0, 255))
        for cap in range(school_capacities[school]):
            draw.rectangle((320 + 40 * cap, 14 + 80 * school, 352 + 40 * cap, 46 + 80 * school), outline = (0, 0, 0, 255))

    return img.resize((int(img.width * 1.5), int(img.height * 1.5)))
    
def priority_group_example(all_ordered_groups, priority_group_dict, program_data):
    imgs = []
    font = ImageFont.truetype("OpenSansEmoji.ttf", 15)
    font2 = ImageFont.truetype("OpenSansEmoji.ttf", 20)
    for program in program_data:
        img = Image.new("RGBA", (780, 370), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        ordered_groups = all_ordered_groups[program]
        priority_groups = priority_group_dict[program]
        for i in range(len(ordered_groups)):
            if i % 2 == 0: height = 10
            else: height = 200
            k = 110
            draw.rectangle((k * i, height, 208 + k * i, height + 140), fill = (252, 199, 179, 255))
            draw.text((k * i + 5, height), ordered_groups[i] + f" ({i + 1})", font = font, fill = (0, 0, 0, 255))
            if ordered_groups[i] in priority_groups:
                j = 0
                base = 1
                for student in priority_groups[ordered_groups[i]]:
                    draw.ellipse((k * i + base, height + 25, k * i + base + 50, height + 75), fill = (18, 137, 222, 255))
                    draw.text((k*i + base + 20, height + 40), student.split( )[1], font = font2)
                    base += 53
                    if j == 2:
                        height += 60
                        base = 1
                    j += 1

        draw.text((300, 166), program + " Preferences", font = font, fill = (0, 0, 0, 255))
        imgs.append(img.resize((int(img.width * 0.75), int(img.height * 0.75))))
        
    return imgs

def localized_render_stage(state = None, form = None, program_data = None, pref = None):
    program_preferences = pref
    if state == [1, 1]:
        schools = defaultdict(list)
        working_copy_of_students = {name: {"form": form[name]["form"].copy(), "accepted": False} for name in form}
        upbases = {name: 0 for name in working_copy_of_students}
        leftbases = {name: 0 for name in working_copy_of_students}
        is_matched = defaultdict(lambda: "")
    
    else:
        _, _, _, working_copy_of_students, schools, upbases, leftbases, is_matched = state
        schools = defaultdict(list, schools)
        is_matched = defaultdict(list, is_matched)
    
    student_names = list(working_copy_of_students.keys())
    font = ImageFont.truetype("OpenSansEmoji.ttf", 10)
    font2 = ImageFont.truetype("OpenSansEmoji.ttf", 10)
    font3 = ImageFont.truetype("OpenSansEmoji.ttf", 16)
    match = {}
    for student in working_copy_of_students:
        if len(working_copy_of_students[student]["form"]):
            match[student] = working_copy_of_students[student]["form"][0]

    o_ellipsecol = [18, 137, 222, 255]
    o_prefcol = [136, 255, 136, 255]
    o_textcol = [0, 0, 0, 255]
    o_ellipsecolx = [255, 255, 255, 255]
    speed = 3
    flag = 0
    imgs = []
    imgs2 = []
    text = []

    ellipsecol = o_ellipsecol.copy()
    ellipsecolx = o_ellipsecolx.copy()
    prefcol = o_prefcol.copy()
    textcol = o_textcol.copy()
    ellipsecol2 = o_prefcol.copy() 
    textcol2 = o_textcol.copy()
    counter = 0
    while len(working_copy_of_students[student_names[counter]]["form"]) == 0 or working_copy_of_students[student_names[counter]]["accepted"] == True:
        counter += 1
        if counter == len(student_names):
            img = Image.new("RGBA", (450, max(40 * len(student_names), 80 * len(schools))), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            school_names = list(program_data.keys())
            for school_name in program_data:
                school = school_names.index(school_name)
                draw.rectangle((250, 12 + 80 * school, 435, 48 + 80 * school), fill = tuple(o_prefcol))
                draw.text((253, 80 * school + 12), school_name, font = font, fill = tuple(o_textcol))
                for cap in range(program_data[school_name]["capacity"]):
                    draw.rectangle((320 + 40 * cap, 14 + 80 * school, 352 + 40 * cap, 46 + 80 * school), outline = tuple(o_textcol))

            for student in range(len(student_names)):
                name = student_names[student]
                draw.ellipse((leftbases[name], upbases[name] + 40 * student, leftbases[name] + 30, upbases[name] + 30 + 40 * student), fill = tuple(o_ellipsecol))
                draw.text((13 + leftbases[name], upbases[name] + 40 * student + 11), str(student + 1), font = font, fill = tuple(o_ellipsecolx))

            return None, [process(img.resize((int(img.width * 1.5), int(img.height * 1.5))))], ["Algorithm Complete."], working_copy_of_students, dict(schools), upbases, leftbases, dict(is_matched)
    
    select = student_names[counter]
    select2 = ""
    pselect = working_copy_of_students[select]["form"][0]

    fade = 255
    k = 0
    save = ""
    ranges = []

    while True:
        img = Image.new("RGBA", (450, max(40 * len(student_names), 80 * len(schools))), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)

        school_names = list(program_data.keys())
        for school_name in program_data:
            school = school_names.index(school_name)
            draw.rectangle((250, 12 + 80 * school, 435, 48 + 80 * school), fill = [tuple(ellipsecol2), tuple(o_prefcol)][school_name == pselect])
            draw.text((253, 80 * school + 12), school_name, font = font, fill = [tuple(textcol2), tuple(o_textcol)][school_name == pselect])
            for cap in range(program_data[school_name]["capacity"]):
                draw.rectangle((320 + 40 * cap, 14 + 80 * school, 352 + 40 * cap, 46 + 80 * school), outline = [tuple(textcol2), tuple(o_textcol)][school_name == pselect])

        for student in range(len(student_names)):
            name = student_names[student]
            if flag == 3 and name == select:
                leftbases[name] += 10
                if leftbases[name] == 320 + 40 * len(schools[pselect]): leftbases[name] += 1
            elif flag == 6 and name == select2:
                leftbases[name] -= 10
                if leftbases[name] == 1: leftbases[name] = 0
            if (flag != 3 or (flag == 3 and (name == select or pselect == is_matched[name]))) or (flag == 6 and name == select2):
                if flag == 3 and name == select:
                    b = 15 + 80 * school_names.index(match[name])
                    a = 40 * student
                    upbases[name] = (b-a) * (min(leftbases[name], 320 + 40 * len(schools[pselect]))/10) // ((320 + 40 * len(schools[pselect]))//10)
                    if b < a and abs(upbases[name] - 16 + 80 * school_names.index(match[name])) <= 2:
                        upbases[name] = 16 + 80 * school_names.index(match[name])
                elif flag == 6 and name == select2:
                    b = 15 + 80 * school_names.index(match[name])
                    a = 40 * student
                    upbases[name] = (b-a) * (min(leftbases[name], 320 + 40 * len(schools[pselect]))/10) // ((320 + 40 * len(schools[pselect]))//10)
                    if b < a and abs(upbases[name] - 40 * student) <= 2:
                        upbases[name] = 40 * student
                draw.ellipse((leftbases[name], upbases[name] + 40 * student, leftbases[name] + 30, upbases[name] + 30 + 40 * student), 
                             fill = [tuple(ellipsecol), tuple(o_ellipsecol)][name == select or name == select2 or (working_copy_of_students[name]["accepted"] and (flag < 2 or pselect == is_matched[name]))])
                draw.text((13 + leftbases[name], upbases[name] + 40 * student + 11), str(student + 1), font = font, fill = [tuple(ellipsecolx), tuple(o_ellipsecolx)][name == select or name == select2 or (working_copy_of_students[name]["accepted"] and (flag < 2 or pselect == is_matched[name]))])

            if flag != 3 and not working_copy_of_students[name]["accepted"]:
                base = 0
                programs = working_copy_of_students[student_names[student]]["form"]
                for program in range(len(programs)):
                    draw.rectangle((40, base + 2 * program + 40 * student, 90, base + 8 + 2 * program + 40 * student), fill = [tuple(prefcol), tuple(o_prefcol)][student_names[student] == select and program == 0])
                    draw.text((41, base + 2 * program - 1 + 40 * student), programs[program], fill = [tuple(textcol), tuple(o_textcol)][student_names[student] == select and program == 0], font = font2)
                    base += 10

        if flag == 4:
            if fade == 1: fade = 0
            thenames = [[a.split(" ")[1], "-"][a not in schools[pselect] + [select]] for a in program_preferences[pselect]]
            save = " > ".join(thenames)
            fade = max(0, fade//2)
        elif flag == 5:
            actual_pref = [[a.split(" ")[1], f"({a.split(' ')[1]})"][a == select] for a in program_preferences[pselect] if a in schools[pselect] + [select]]
            save = " > ".join(actual_pref)

        ellipsecol = [min(255, i + speed) for i in ellipsecol[:3]] + [max(0, ellipsecol[3] - speed)]
        prefcol = [min(255, i + speed) for i in prefcol[:3]] + [max(0, prefcol[3] - speed)]
        textcol = [min(255, i + speed) for i in textcol[:3]] + [max(0, textcol[3] - speed)]
        ellipsecolx[3] = max(0, ellipsecolx[3] - speed)
        speed += min(15, speed)

        if flag == 6:
            if leftbases[select2] == 0:
                schools[pselect].remove(select2)
                del working_copy_of_students[select2]["form"][0]
                working_copy_of_students[select2]["accepted"] = False
                is_matched[select2] = ""
                if len(working_copy_of_students[select2]["form"]) == 0:
                    working_copy_of_students[select2]["accepted"] = True
                else:
                    match[select2] = working_copy_of_students[select2]["form"][0]
                text.append("Step 5: Reject least-preferred student.")
                imgs.append(img)
                imgs2.append(img)
                ranges.append(len(imgs))
                for i in range(15):
                    imgs2.append(imgs2[-1])
                flag = 3
            else:
                imgs.append(img)
                imgs2.append(img)

        elif flag == 5:
            student_list = [a for a in program_preferences[pselect] if a in schools[pselect] + [select]]
            if student_list[-1] == select:
                text.append(f"Capping Step: No, reject/ignore them. Preferences: {save}")
                del working_copy_of_students[select]["form"][0]
                if len(working_copy_of_students[select]["form"]) == 0:
                    working_copy_of_students[select]["accepted"] = True
                    is_matched[select] = ""
                imgs.append(img)
                imgs2.append(img)
                ranges.append(len(imgs))
                for i in range(15):
                    imgs2.append(imgs2[-1])
                if counter != len(student_names) - 1:
                    flag = 0
                    counter += 1
                    while len(working_copy_of_students[student_names[counter]]["form"]) == 0 or working_copy_of_students[student_names[counter]]["accepted"] == True:
                        counter += 1
                        if counter == len(student_names):
                            break
                    if counter == len(student_names):
                        break
                    speed = 3
                    k = 0
                    ellipsecol = o_ellipsecol.copy()
                    ellipsecolx = o_ellipsecolx.copy()
                    prefcol = o_prefcol.copy()
                    textcol = o_textcol.copy()
                    ellipsecol2 = o_prefcol.copy() 
                    textcol2 = o_textcol.copy()
                    select = student_names[counter]
                    pselect = working_copy_of_students[select]["form"][0]
                    match[select] = pselect
                else:
                    break
            else:
                text.append(f"Step 4: Yes. Preferences: {save}")
                imgs.append(img)
                imgs2.append(img)
                ranges.append(len(imgs))
                for i in range(15):
                    imgs2.append(imgs2[-1])
                flag = 6
                select2 = [a for a in program_preferences[pselect] if a in schools[pselect] + [select]][-1]

        elif flag == 4:
            if fade == 0:
                fade = 255
                text.append(f"Step 3: Are they better than anyone? Preferences: {save}")
                imgs.append(img)
                imgs2.append(img)
                ranges.append(len(imgs))
                for i in range(15):
                    imgs2.append(imgs2[-1])
                flag = 5
            else:
                imgs.append(img)

        elif flag == 3:
            if leftbases[select] == 321 + 40 * len(schools[pselect]):
                text.append("Capping Step: Mark student as assigned.")
                imgs.append(img)
                imgs2.append(img)
                ranges.append(len(imgs))
                for i in range(15):
                    imgs2.append(imgs2[-1])

                schools[pselect].append(select)
                working_copy_of_students[select]["accepted"] = True
                is_matched[select] = pselect
                if counter != len(student_names) - 1:
                    flag = 0
                    counter += 1
                    while len(working_copy_of_students[student_names[counter]]["form"]) == 0 or working_copy_of_students[student_names[counter]]["accepted"] == True:
                        counter += 1
                        if counter == len(student_names):
                            break
                    if counter == len(student_names):
                        break
                    speed = 3
                    k = 0
                    ellipsecol = o_ellipsecol.copy()
                    ellipsecolx = o_ellipsecolx.copy()
                    prefcol = o_prefcol.copy()
                    textcol = o_textcol.copy()
                    ellipsecol2 = o_prefcol.copy() 
                    textcol2 = o_textcol.copy()
                    select = student_names[counter]
                    pselect = working_copy_of_students[select]["form"][0]
                else:
                    break

            else:
                imgs.append(img)
                imgs2.append(img)

        elif flag == 2:
            if ellipsecol2 == [255, 255, 255, 0] and textcol2 == [255, 255, 255, 0]:
                if len(schools[pselect]) < program_data[pselect]["capacity"]:
                    text.append("Step 2: Program has space; add student.")
                    flag = 3
                else:
                    text.append("Step 2: Program full; find preferences")
                    flag = 4
                imgs.append(img)
                imgs2.append(img)
                ranges.append(len(imgs))
                for i in range(15):
                    imgs2.append(imgs2[-1])
            else:
                imgs.append(img)
                imgs2.append(img)
                ellipsecol2 = [min(255, i + speed) for i in ellipsecol2[:3]] + [max(0, ellipsecol2[3] - speed)]
                textcol2 = [min(255, i + speed) for i in textcol2[:3]] + [max(0, textcol2[3] - speed)]
                speed += min(15, speed - 1)


        elif flag == 1: 
            text.append("Step 1: Select next student's first choice.")
            imgs.append(img)
            imgs2.append(img)
            ranges.append(len(imgs))
            for i in range(15):
                imgs2.append(imgs2[-1])
            speed = 5
            flag = 2

        elif ellipsecol == [255, 255, 255, 0] and textcol == [255, 255, 255, 0] and prefcol == [255, 255, 255, 0] and flag == 0: 
            flag = 1
            imgs.append(img)
            imgs2.append(img)

        else:
            imgs.append(img)
            imgs2.append(img)
            if k == 0:
                k = 1
                for i in range(15):
                    imgs2.append(img)

    def gen_frame(im):
        im = im.resize((int(img.width * 1.5), int(img.height * 1.5)))
        # https://stackoverflow.com/questions/46850318/transparent-background-in-gif-using-python-imageio
        alpha = im.getchannel('A')
        im = im.convert('RGB').convert('P', palette=Image.ADAPTIVE, colors=255)
        mask = Image.eval(alpha, lambda a: 255 if a <=128 else 0)
        im.paste(255, mask)
        im.info['transparency'] = 255
        return im

    gifs = []
    upgraded_ranges = [0] + [i-1 for i in ranges] + [len(imgs) - 1]
    for counter in range(1, len(upgraded_ranges)):
        gif = []
        for i in range(upgraded_ranges[counter - 1], upgraded_ranges[counter] + 1):
            gif.append(gen_frame(imgs[i]))
        filex = BytesIO()
        gif[0].save(fp = filex, format='GIF', append_images=gif[1:], save_all=True, disposal = 2, optimize=False, duration=100)
        filex.seek(0)
        gifs.append(f"data:image/gif;base64,{b64encode(filex.getvalue()).decode('utf-8')}")

    return gifs, None, text, working_copy_of_students, dict(schools), upbases, leftbases, dict(is_matched)
