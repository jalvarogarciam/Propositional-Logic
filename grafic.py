import flet as ft
from LogicExpression import LogicExpression as le

class key(ft.ElevatedButton):
    def __init__(self, text, button_clicked, width=60, color=ft.colors.WHITE, bgcolor=ft.colors.PURPLE):
        super().__init__()
        self.text = text
        self.expand = False
        self.on_click = button_clicked
        self.data = text
        self.bgcolor = bgcolor
        self.color = color
        self.width = width

class ActionButton(ft.ElevatedButton):
    def __init__(self, text, button_clicked):
        ...

class Panel(ft.Row):
    # application's root control (i.e. "view") containing all other controls
    def __init__(self):
        super().__init__()

        self.le = le(0)

        self.formula = ft.TextField(
            hint_text="FORMULA", expand=False,
            autofocus=True,
            filled=True, fill_color=ft.colors.WHITE70,
            width=350, cursor_color=ft.colors.BLACK,
            text_style=ft.TextStyle( 
                color=ft.colors.BLACK, 
                weight=ft.FontWeight.BOLD 
            )
        )
        self.values = ft.TextField(
            hint_text="values {}", text_align='center',
            color=ft.colors.YELLOW, width=150
        )
        self.order = ft.TextField(
            hint_text="order", text_align='center',
            color=ft.colors.YELLOW, width=150
        )
        self.classification = ft.TextField(
            hint_text="classification", text_align='center',
            color=ft.colors.RED, width=150, disabled=True
        )
        self.interpretation = ft.TextField(
            hint_text="interpretation", text_align='center',
            color=ft.colors.RED, width=200, disabled=True
        )
        self.keyboard = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        key(text="∧", button_clicked=self.button_clicked),
                        key(text="∨", button_clicked=self.button_clicked),
                        key(text="→", button_clicked=self.button_clicked),
                        key(text="←", button_clicked=self.button_clicked),
                        key(text="↔", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        key(text="↑", button_clicked=self.button_clicked),
                        key(text="↓", button_clicked=self.button_clicked),
                        key(text="↛", button_clicked=self.button_clicked),
                        key(text="↚", button_clicked=self.button_clicked),
                        key(text="⊕", button_clicked=self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        key(
                            text="1", button_clicked=self.button_clicked, 
                            width=110, bgcolor=ft.colors.BLUE, color=ft.colors.BLACK
                        ),
                        key(
                            text="¬", button_clicked=self.button_clicked, 
                            width=110, color=ft.colors.BLACK, bgcolor='purple',
                        ),
                        key(
                            text="0", button_clicked=self.button_clicked, 
                            width=110, bgcolor=ft.colors.BLUE, color=ft.colors.BLACK
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                )
                
            ]
        )

        self.board = ft.Column(width=350)

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
                    self.keyboard,
                    self.board
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
                    self.interpretation,
                ],
                width=150, height=200
            ),
        ]

    def button_clicked(self, e):
        data = e.control.data
        print(f"Button clicked with data = {data}")

        if self.formula.value == "Error":   self.reset()

        if self.formula.value == "":
            if not self.formula.value:
                self.formula.error_text = "Please, enter a logic formula"
                self.formula.update()
                self.formula.value = "Error"

        if type(e.control) == key:
            self.formula.value += data
            # Actualizar el campo de texto
            self.formula.update()
            # Mover el cursor al final del texto después de actualizar el valor
            self.formula.focus()
        
        elif type(e.control) == ft.ElevatedButton:
            if "classify" in e.control.text: self.clasify()
            elif "interpret" in e.control.text: self.interpret()


    def make_board(self):
        self.le = le(self.formula.value)

        if self.order != "": self.le.order(*(i for i in self.order.value))

        self.board.controls = [
            ft.Row(
                controls= [
                    ft.TextField(
                        value= "".join(self.le.vars), disabled=True
                    ),
                    ft.TextField(
                        value= "value", disabled=True
                    )
                ]
            )
        ]

        board = self.le()[1]

        for r in board:
            self.board.controls.append(
                ft.Row(
                    controls= [
                        ft.TextField(
                            value= "".join(r[0]), disabled=True
                        ),
                        ft.TextField(
                            value= r[1], disabled=True
                        )
                    ]
                )
            )

        
        

    def reset(self):
        self.formula.value = ""
        self.formula.error_text = ""

    def clasify(self):
        self.le = le(self.formula.value)

        if self.le.istautology(): 
            self.classification.value = "tautology"
            self.classification.color= ft.colors.GREEN
        else:
            if self.le.iscontradiction(): 
                self.classification.value = "contradiction"
                self.classification.color= ft.colors.RED
            else : 
                self.classification.value = "contingent"
                self.classification.color= ft.colors.WHITE
        
        self.classification.update()
    
    def interpret(self):
        self.le = le(self.formula.value)

        if self.order != "": self.le.order(*(i for i in self.order.value))

        values = {}
        i=0
        for val in self.values.value:
            values.update({self.le.vars[i]:int(val)})
            i+=1

        interpretation = self.le(values)
        print(values, self.le.vars)

        if interpretation:
            self.interpretation.color= ft.colors.GREEN
            self.interpretation.value= "true"
        else:
            self.interpretation.color= ft.colors.RED
            self.interpretation.value= "false"

        self.interpretation.update()

        self.make_board()
        self.update()






def main(page: ft.Page):
    page.title = "Calc App"
    # create application instance
    calc = Panel()

    # add application's root control to the page
    page.add(ft.Row([calc], alignment=ft.MainAxisAlignment.CENTER,))


ft.app(target=main)