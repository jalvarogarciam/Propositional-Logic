import flet as ft
from LogicExpression import LogicExpression
from time import time, sleep

import asyncio

def main(page):

    async def truth_table(e):
        if not formula.value:
            formula.error_text = "Please enter a logic formula"
            page.update()
            formula.focus()
        else:
            
            page.controls.append(
                truth_table(formula.value)
            )
            page.update()
            del page.controls [-1]

            


    async def tipo(e):
        if not formula.value:
            formula.error_text = "Please enter a logic formula"
            page.update()
        else:
            le = LogicExpression(formula.value)
            tipo :str = ""
            if le.isrefutable():
                if le.iscontradiction():
                    tipo = "contradicción"
                else : tipo = "contingente"
            else:   tipo = "tautología"

            t = ft.Text(value=tipo)
            page.controls.append(t)
            page.update()
            page.controls.remove(t)



    formula = ft.TextField(hint_text="FORMULA", color="green", width=400)
    values = ft.TextField(hint_text="values {}", color="red", width=200)
    page.add(
        ft.Row(
            [formula, values], alignment=ft.MainAxisAlignment.CENTER,
        )
    )
    page.add(
        ft.Row(
            [ft.ElevatedButton("tabla de verdad", on_click=truth_table, color = 'purple'), 
             ft.ElevatedButton("clasificacion", on_click=tipo, color = 'orange'),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )




    def truth_table(string)->ft.DataTable:
        le = LogicExpression(string)
        vars, board = le()

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("".join(vars))),
                ft.DataColumn(ft.Text("formula")),
            ],
            rows=[]
        )
        
        for i in range(2*len(vars)):
            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("".join(board[i][0]))),
                    ft.DataCell(ft.Text(str(board[i][1]))),
                ],
            )
            table.rows.append(row)
        return table
    


ft.app(target=main)