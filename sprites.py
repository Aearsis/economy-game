from PIL import Image

from core.models import Entity


def path(name):
    return "icons/%s.png" % name


def image(entity):
    try:
        return Image.open(path(entity.name))
    except:
        print("Chybi %s!" % entity)
        return Image.open(path("Neznámé"))


images = [(e.id, image(e)) for e in Entity.objects.all()]

w = sum([i.size[0] for _, i in images])
mh = max([i.size[1] for _, i in images])

result = Image.new("RGBA", (w, mh))
css = []

x = 0
for id, img in images:
    result.paste(img, (x, 0))
    css.append(".eicon-%i { background-position: -%ipx 0; }\n" % (id, x))
    x += img.size[0]

result.save("static/img/icons-sprite.png")

f = open("static/css/sprites.css", mode="w")
f.write("".join(css))
f.close()
