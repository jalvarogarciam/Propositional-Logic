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

        self.formula = ft.TextField(
            hint_text="FORMULA", expand=False,
            autofocus=True, on_focus=self.on_focus,
            filled=True, fill_color=ft.colors.WHITE70,
            width=350, cursor_color=ft.colors.BLACK,
            text_style=ft.TextStyle( 
                color=ft.colors.BLACK, 
                weight=ft.FontWeight.BOLD 
            )
        )
        self.values = ft.TextField(
            hint_text="values {}", text_align='center',
            color="yellow", width=150
        )
        self.order = ft.TextField(
            hint_text="order", text_align='center',
            color="yellow", width=150
        )
        self.classification = ft.TextField(
            hint_text="classification", 
            color="red", width=150, disabled=True
        )
        self.interpretation = ft.TextField(
            hint_text="interpretation", 
            color="red", width=200, disabled=True
        )
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
                        ConnectiveButton(
                            text="1", button_clicked=self.button_clicked, 
                            width=110, bgcolor=ft.colors.BLUE, color=ft.colors.BLACK
                        ),
                        ConnectiveButton(
                            text="¬", button_clicked=self.button_clicked, 
                            width=110, color=ft.colors.BLACK, bgcolor='purple',
                        ),
                        ConnectiveButton(
                            text="0", button_clicked=self.button_clicked, 
                            width=110, bgcolor=ft.colors.BLUE, color=ft.colors.BLACK
                        ),
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
                        text="↓classify↓", 
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
                        color='yellow', 
                        on_click=self.button_clicked,
                        width=150
                    ),
                    self.interpretation
                ],
                width=150, height=200
            ),
        ]


    def on_focus(self, e):
        # Obtener el TextField y mover el cursor al final del texto
        text_field = e.control
        text_field.cursor_position = len(text_field.value)
        self.update()

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")

        if self.formula.value == "Error":   self.reset()


        if data in ("∧", "∨", "→", "←", "↔", '↑', '↚', '↛', '↓', '⊕', '1', '0', '¬'): 
            self.formula.value += data
            # Actualizar el campo de texto
            self.formula.update()
            # Mover el cursor al final del texto después de actualizar el valor
            self.formula.cursor_position = len(self.formula.value)-1
            self.formula.focus()
            self.formula.update()

        else:
            if not self.formula.value:
                self.formula.error_text = "Please, enter a logic formula"
                self.formula.update()
                self.formula.value = "Error"
            else:
                ...

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