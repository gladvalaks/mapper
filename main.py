import pygame
import sys
import requests
import os
from classes import Background, GUI, LabelMenu, TextBox, ButtonMenu, Checkbox
import math

api_key = "3c4a592e-c4c0-4949-85d1-97291c87825c"
org_search = "https://search-maps.yandex.ru/v1/"
map_image = None
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
toponym_to_find = None
geocoder_params = {"geocode": toponym_to_find, "format": "json"}
pygame.init()
running = True
size = width, height = 1280, 720
screen = pygame.display.set_mode(size)
addy = "Адресс: "


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2.)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)

    return distance


def terminate():
    pygame.quit()
    try:
        os.remove("map.png")
    except:
        pass
    sys.exit()


def change_centr_map(map, num, koef):
    y = map.get_bounds(map.get_toponym())[num]
    if map.clicked:
        y = [float(i) for i in map.last_spn.split(",")][num]
    coords = [float(i) for i in map.get_coords().split()]
    coords[num] += float(y) * koef
    map.set_coords([str(i) for i in coords])
    coords = ' '.join(map.get_coords())
    return coords


def get_coords_click(pos, params):
    a, b = pos
    a = int(a) - 350
    b = int(b) - 200
    b = -b + 200
    values = [float(i) for i in params["spn"].split(",")]
    koef_a = a / 200
    koef_b = b / 200
    delta_1 = values[0] / 1.9 * koef_a
    delta_2 = values[1] / 1.5 * koef_b
    result = [float(i) for i in params["ll"].split(",")]
    result[0] += delta_1
    result[1] += delta_2
    result = [str(i) for i in result]
    result = ','.join(result)
    return result


b = ButtonMenu((1000, 360, 170, 50), "map", "x")
reset = ButtonMenu((700, 450, 170, 50), "Очистить запрос", "y")
index = Checkbox((600, 525, 170, 50), "Добавить почтовый индекс: ")
address = LabelMenu((50, 150, 300, 50), addy)


class Map:
    def __init__(self, address, scale):
        self.spns = ["0.002091531249999982,0.000989458333333304", "0.004183062499999964,0.001978916666666608",
                     "0.008366124999999927,0.003957833333333216", "0.016732249999999855,0.007915666666666432",
                     "0.03346449999999971,0.015831333333332864", "0.06692899999999942,0.03166266666666573",
                     "0.13385799999999884,0.06332533333333146", "0.2677159999999977,0.12665066666666291",
                     "0.5354319999999954,0.25330133333332583", "1.0708639999999907,0.5066026666666517",
                     "2.1417279999999814,1.0132053333333033", "4.283455999999963,2.0264106666666066",
                     "8.566911999999926,4.052821333333213", "17.13382399999985,8.105642666666427",
                     "34.2676479999997,16.211285333332853"]
        self.spns = [i.split(",") for i in self.spns]
        self.clicked = False
        self.post_index = index.get_tapped()
        self.reset = False
        try:
            self.scale = float(scale)
        except ValueError:
            self.scale = 3
        self.map_file = None
        self.address = address
        self.full_address = ""
        if address[0].isalpha():
            self.coords = self.geo_coords()
        else:
            self.coords = self.address
        self.point = self.coords
        self.draw()

    def get_bounds(self, toponym):
        delta = ""
        delta1 = ""
        if not self.clicked:
            bounds = toponym["boundedBy"]["Envelope"]["lowerCorner"].split(), toponym["boundedBy"]["Envelope"][
                "upperCorner"].split()
            delta = (float(bounds[1][0]) - float(bounds[0][0])) / self.scale
            delta1 = (float(bounds[1][1]) - float(bounds[0][1])) / self.scale
        return str(delta), str(delta1)

    def draw(self):
        req = "http://static-maps.yandex.ru/1.x/"
        if not self.clicked:
            spn = self.get_bounds(self.toponym)
            value = min(self.spns, key=lambda x: abs(float(x[0]) - float(spn[0])))
            self.index = self.spns.index(value)
            self.clicked = True
        self.req_params = {
            "ll": ','.join(self.coords.split()),
            "spn": ",".join(self.spns[self.index]),
            "l": b.get_text(),
            "size": "400,400",
            "pt": ','.join(self.point.split() + ["pm2ntm"])
        }
        if self.reset:
            del (self.req_params["pt"])
        else:
            self.last_spn = self.req_params["spn"]
        try:
            response = requests.get(req, params=self.req_params)
            if response:
                self.map_file = "map.png"
                try:
                    with open(self.map_file, "wb") as file:
                        file.write(response.content)
                except IOError as ex:
                    sys.exit(2)
                pygame.init()
                screen.blit(pygame.image.load("map.png"), (150, 200))
                pygame.display.flip()
        except:
            pass

    def set_full_address(self, value):
        self.full_address = value

    def set_point(self, value):
        self.point = value

    def get_full_address(self):
        return self.full_address

    def get_scale(self):
        return self.scale

    def set_index(self, value):
        self.index = value

    def get_index(self):
        return self.index

    def set_scale(self, value):
        self.scale = value

    def get_coords(self):
        return self.coords

    def set_coords(self, value):
        self.coords = value

    def get_reset(self):
        return self.reset

    def set_reset(self, value):
        self.reset = value

    def get_toponym(self):
        return self.toponym

    def geo_coords(self):
        geocoder_params = {
            "geocode": self.address,
            "format": "json"
        }
        try:
            response = requests.get(geocoder_api_server, params=geocoder_params)
            if response:
                json_response = response.json()
                self.toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                self.full_address = self.toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                self.change_address()
                toponym_coords = self.toponym["Point"]["pos"]
                return toponym_coords
        except:
            pass
        return None

    def change_address(self, *toponym):
        self.post_index = index.get_tapped()
        address = self.full_address
        try:
            self.posty_index = self.toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
        except Exception:
            self.posty_index = 'Нема индекса'
        self.full_address = self.toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
        try:
            self.full_address = toponym[0]["metaDataProperty"]["GeocoderMetaData"]["text"]
            self.posty_index = toponym[0]["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
        except KeyError:
            self.full_address = toponym[0]["name"] + ", " + toponym[0]["address"]
        except Exception as err:
            pass
        if self.post_index:
            self.full_address += ", " + self.posty_index


def start_screen():
    clicked = False
    BackGround = Background()
    gui = GUI()
    box = TextBox((700, 600, 170, 50), "Введите Ваш запрос")
    gui.add_element(LabelMenu((950, 310, 170, 50), "Вид карты:"))
    gui.add_element(b)
    gui.add_element(box)
    gui.add_element(reset)
    gui.add_element(address)
    gui.add_element(index)
    scale_box = TextBox((1000, 260, 170, 50), "default")
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and 150 <= event.pos[0] <= 550 and 200 <= event.pos[1] <= 600:
                clicked = True
                addressy = get_coords_click(event.pos, map.req_params)
                if event.button == 1:
                    geocoder_params = {
                        "geocode": addressy,
                        "format": "json"
                    }
                    try:
                        response = requests.get(geocoder_api_server, params=geocoder_params)
                        if response:
                            json_response = response.json()
                            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0][
                                "GeoObject"]
                            map.set_full_address(addy + toponym["metaDataProperty"]["GeocoderMetaData"]["text"])
                    except Exception:
                        pass
                    map.set_point(" ".join(addressy.split(',')))
                    map.draw()
                    address.set_text(map.full_address)

                if event.button == 3:
                    radius = 50 / 111144
                    org_params = {"apikey": api_key,
                                  "text": addressy,
                                  "type": "biz",
                                  "lang": "ru_RU",
                                  "ll": addressy,
                                  "spn": ",".join([str(radius), str(radius)])}
                    try:
                        response = requests.get(org_search, params=org_params)
                        json_r = response.json()
                        organizations = json_r["features"]
                        toponym = None
                        for i in range(len(organizations)):
                            if lonlat_distance(organizations[i]["geometry"]["coordinates"],
                                               [float(i) for i in addressy.split(",")]) < 50:
                                toponym = organizations[i]["properties"]["CompanyMetaData"]
                                break
                        map.set_full_address(toponym["name"] + ", " + toponym["address"])
                    except Exception as err:
                        map.set_full_address("")
                    map.set_point(" ".join(addressy.split(',')))
                    map.draw()
                    address.set_text(addy + map.get_full_address())
            try:
                if index.get_focus() and address.get_text() != addy:
                    if clicked and address.get_text() != addy:
                        map.change_address(toponym)
                    else:
                        map.change_address()
                    address.set_text(addy + map.get_full_address())
            except NameError:
                pass
            if b.get_pressed() and address.get_text() != addy:
                b.set_index(b.get_index() + 1)
                b.set_text(b.get_list()[b.get_index() % 3])
                map.draw()
            if box.get_done():
                try:
                    map = Map(box.text, scale_box.text)
                    address.set_text(addy + map.get_full_address())
                    clicked = False
                except AttributeError as err:
                    address.set_text("Вы что-то ввели не так!")
            if event.type == pygame.QUIT:
                terminate()
            if reset.pressed and address.get_text() != addy:
                clicked = False
                try:
                    map.set_reset(True)
                    map.draw()
                except NameError:
                    pass
                address.set_text(addy)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    map.set_coords(change_centr_map(map, 1, 1))
                    map.draw()
                if event.key == pygame.K_DOWN:
                    map.set_coords(change_centr_map(map, 1, -1))
                    map.draw()
                if event.key == pygame.K_LEFT:
                    map.set_coords(change_centr_map(map, 0, -1))
                    map.draw()
                if event.key == pygame.K_RIGHT:
                    map.set_coords(change_centr_map(map, 0, 1))
                    map.draw()
                if event.key == pygame.K_PAGEDOWN:
                    map.set_index(map.get_index() + 1)
                    if map.get_index() > 14:
                        map.set_index(map.get_index() - 1)
                    map.draw()
                if event.key == pygame.K_PAGEUP:
                    map.set_index(map.get_index() - 1)
                    if map.get_index() < 0:
                        map.set_index(map.get_index() + 1)
                    map.draw()
                if pygame.key == pygame.K_ESCAPE:
                    Map(box.text)
            if gui.get_event(event) == "q":
                os.remove("map.png")
                terminate()

        screen.blit(BackGround.image, BackGround.rect)
        try:
            screen.blit(pygame.image.load("map.png"), (150, 200))
        except:
            pass

        gui.render(screen)
        gui.update()
        pygame.display.flip()
start_screen()
