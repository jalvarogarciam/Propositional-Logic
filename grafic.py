import flet as ft


class CalcButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked, expand=False):
        super().__init__()
        self.text = text
        self.expand = expand
        self.on_click = button_clicked
        self.data = text


class ConnectiveButton(CalcButton):
    def __init__(self, text, button_clicked, width=60, color=ft.colors.WHITE, bgcolor=ft.colors.PURPLE):
        CalcButton.__init__(self, text, button_clicked, expand=False )
        self.bgcolor = bgcolor
        self.color = color
        self.width = width


class ActionButton(CalcButton):
    def __init__(self, text, button_clicked):
        CalcButton.__init__(self, text, button_clicked, expand=False)
        self.color = ft.colors.RED



class Panel(ft.Row):
    # application's root control (i.e. "view") containing all other controls
    def __init__(self):
        super().__init__()

        self.formula = ft.TextField(hint_text="FORMULA", color=ft.colors.GREEN, width=350)
        self.values = ft.TextField(hint_text="values {}", color="red", width=150)
        self.order = ft.TextField(hint_text="order", color="yellow", width=150)
        self.classification = ft.TextField(hint_text="classification", color="red", width=150, disabled=True)
        self.interpretation = ft.TextField(hint_text="interpretation", color="red", width=200, disabled=True)
        self.connective_buttons = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ConnectiveButton(text="∧", button_clicked=self.button_clicked),
                        ConnectiveButton(text="∨", button_clicked=self.button_clicked),
                        ConnectiveButton(text="→", button_clicked=self.button_clicked),
                        ConnectiveButton(text="←", button_clicked=self.button_clicked),
                        ConnectiveButton(text="↔", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ConnectiveButton(text="↑", button_clicked=self.button_clicked),
                        ConnectiveButton(text="↓", button_clicked=self.button_clicked),
                        ConnectiveButton(text="↛", button_clicked=self.button_clicked),
                        ConnectiveButton(text="↚", button_clicked=self.button_clicked),
                        ConnectiveButton(text="⊕", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        ConnectiveButton(text="1", button_clicked=self.button_clicked, 
                                         width=110, bgcolor=ft.colors.BLUE, color=ft.colors.BLACK),
                        ConnectiveButton(text="¬", button_clicked=self.button_clicked, 
                                         width=110, color=ft.colors.BLACK),
                        ConnectiveButton(text="0", button_clicked=self.button_clicked, 
                                         width=110, bgcolor=ft.colors.BLUE, color=ft.colors.BLACK),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
                
            ]
        )



        self.controls = [
            ft.Column(
                controls=[
                    self.order, 
                    ft.ElevatedButton(
                        "↓classify↓", 
                        color='yellow', 
                        on_click=self.button_clicked,
                        width=150
                    ),
                    self.classification
                ],
                height=200
            ),
            ft.Column(
                controls=[
                    self.formula, 
                    self.connective_buttons,
                ],
                height=200
            ),
            ft.Column(
                controls=[
                    self.values,
                    ft.ElevatedButton(
                        "↓interpret↓", 
                        color='red', 
                        on_click=self.button_clicked,
                        width=150
                    ),
                    self.interpretation
                ],
                width=150, height=200
            ),
        ]



    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")

        if self.formula.value == "Error":   self.reset()


        if data in ("∧", "∨", "→", "←", "↔", '↑', '↚', '↛', '↓', '⊕', '1', '0', '¬'): 
            self.formula.value += data
            self.update()

        elif not self.formula.value:
            self.reset()
            self.update()

    def reset(self):
        self.formula.value = ""
        self.formula.error_text = ""




def main(page: ft.Page):
    page.title = "Calc App"
    # create application instance
    calc = Panel()

    # add application's root control to the page
    page.add(ft.Row([calc], alignment=ft.MainAxisAlignment.CENTER,))


ft.app(target=main)