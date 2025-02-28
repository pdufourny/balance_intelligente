"""
simulateur de balance
"""

import requests
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

# https://toga.readthedocs.io/en/stable/reference/api/index.html
# https://toga.readthedocs.io/en/stable/reference/style/pack.html#alignment
"""class Sim_Balance(toga.App):
    def startup(self):
        '''Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        '''
        main_box = toga.Box()

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
"""


class Sim_Balance(toga.App):
    def startup(self):
        main_box = toga.Box(
            style=Pack(direction=COLUMN, padding=10, alignment="center")
        )

        self.photo = toga.ImageView(style=Pack(height=400, width=640, padding=5))
        camera_button = toga.Button(
            "Photo",
            on_press=self.take_photo,
            style=Pack(height=100, padding=5, font_size=40),
        )

        main_box.add(self.photo)
        # rows of labels
        row1 = toga.Box(style=Pack(direction=ROW, padding=5))
        row2 = toga.Box(style=Pack(direction=ROW, padding=5))
        row3 = toga.Box(style=Pack(direction=ROW, padding=5))
        row4 = toga.Box(style=Pack(direction=ROW, padding=5))

        # Four labels "keys" : non mutables
        label1 = toga.Label("Produit", style=Pack(padding_right=30, font_size=50))
        label2 = toga.Label("poids", style=Pack(padding_right=30, font_size=50))
        label3 = toga.Label("Prix au Kg", style=Pack(padding_right=30, font_size=50))
        label4 = toga.Label("Prix Net", style=Pack(padding_right=30, font_size=50))

        # Second set of labels "values" => variables dépendantes de l'API
        self.label5 = toga.Label("Label 5", style=Pack(padding_left=30, font_size=50))
        self.label6 = toga.Label("Label 6", style=Pack(padding_left=30, font_size=50))
        self.label7 = toga.Label("Label 7", style=Pack(padding_left=30, font_size=50))
        self.label8 = toga.Label("Label 8", style=Pack(padding_left=30, font_size=50))

        # assign labels to their rows
        row1.add(label1)
        row1.add(self.label5)
        row2.add(label2)
        row2.add(self.label6)
        row3.add(label3)
        row3.add(self.label7)
        row4.add(label4)
        row4.add(self.label8)

        # addit it to main
        main_box.add(row1)
        main_box.add(row2)
        main_box.add(row3)
        main_box.add(row4)

        main_box.add(camera_button)

        # debug : see requests response : mutable
        self.text_input = toga.MultilineTextInput(style=Pack(padding=5, width=300))
        main_box.add(self.text_input)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()
        # im = pil_image.open("".raw)

    async def take_photo(self, widget, **kwargs):
        try:
            if not self.camera.has_permission:
                await self.camera.request_permission()

            image = await self.camera.take_photo()
            if image:
                self.photo.image = image
                # https://toga.readthedocs.io/en/stable/reference/api/resources/images.html
                requests_file = {"file": ("image.jpg", image.data, "image/jpeg")}

                res = requests.post(
                    "http://usr-pdf:6000/fast/pred", files=requests_file
                )
                # res = requests.post('http://10.40.1.55:6000/fast/pred',files= requests_file)
                self.text_input.value = str(res.status_code) + str(res.json())
                # self.label8.text = str(res.status_code)
                item_id = 99  # valeur par defaut, non defini
                if res.status_code == 200:
                    response_data = res.json()
                    item_id = response_data.get("product_id", 99)
                    self.label5.text = str(response_data.get("product_name", "N/A"))
                    self.label6.text = str(response_data.get("product_weight", "N/A"))
                    self.label7.text = str(response_data.get("product_price", "N/A"))
                    self.label8.text = str(response_data.get("net_price", "N/A"))
                else:
                    self.label5.text = "Error"
                    self.label6.text = "Error"
                    self.label7.text = "Error"
                image_res = requests.get(
                    f"http://usr-pdf:6000/fast/img?image_num={item_id}"
                )
                # image_res = requests.get(f'http://10.40.1.55:6000/fast/img?image_num={item_id}')
                if image_res.status_code == 200:
                    self.text_input.value = str(image_res.status_code)
                    self.photo.image = image_res.content
                    self.text_input.value = "chargement ok"
                else:
                    self.label5.text = "Error"

        except NotImplementedError:
            await self.main_window.dialog(
                toga.InfoDialog(
                    "appraeil photo non supporté",
                )
            )
        except PermissionError:
            await self.main_window.dialog(
                toga.InfoDialog(
                    "pas d'autorisation de prendre des photos",
                    "verifier le pyprojet.toml",
                )
            )


def main():
    return Sim_Balance()
